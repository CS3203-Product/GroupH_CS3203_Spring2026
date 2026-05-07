"""Distraction blocker: blocked sites and daily blocking window (AM/PM)."""

from __future__ import annotations

from urllib.parse import urlparse

from fastapi import HTTPException
from nicegui import ui

from src.db.session import get_db_context
from src.frontend.components import notifications
from src.frontend.components.auth_utils import get_current_user_from_state
from src.frontend.layouts.default import dashboard_frame, guard_authenticated
from src.productivity.blocker_schedule import (
    ampm_parts_to_hhmm,
    hhmm_to_ampm_parts,
    is_valid_hhmm,
    local_window_to_utc_hhmm_pair,
    utc_window_to_local_hhmm_pair,
)
from src.repositories.blocked_site import blocked_site_repo
from src.repositories.user import user_repo


def _normalize_hostname(raw: str) -> str:
    s = (raw or "").strip().lower()
    if not s:
        return ""
    if "://" in s:
        try:
            host = urlparse(s).hostname
            if host:
                s = host
        except ValueError:
            pass
    s = s.split("/")[0].split("?")[0]
    if s.startswith("www."):
        s = s[4:]
    return s


async def _browser_timezone() -> str:
    try:
        tz = await ui.run_javascript(
            "return Intl.DateTimeFormat().resolvedOptions().timeZone",
            timeout=5.0,
        )
        if isinstance(tz, str) and tz.strip():
            return tz.strip()
    except Exception:
        pass
    return "UTC"


@ui.page("/distraction-blocker")
async def distraction_blocker_page() -> None:
    if not guard_authenticated():
        return

    with dashboard_frame(title="Distraction blocker"):
        ui.label(
            "Sites are blocked only during your chosen window. "
            "Use the browser extension for enforcement."
        ).classes("text-body2 text-slate-600 dark:text-slate-300 mb-4")

        with ui.card().classes("w-full max-w-3xl p-6"):
            ui.label("Blocking schedule").classes("text-h6 text-emerald-700 dark:text-emerald-300")
            ui.label(
                "When should distractions be blocked? If “from” is later than “to”, "
                "the window crosses midnight (e.g. 10:00 PM → 6:00 AM). "
                "Times follow your browser’s timezone; they are stored and checked in UTC."
            ).classes("text-caption text-slate-500 mt-1 mb-4")

            with ui.row().classes("w-full flex-wrap items-end gap-4"):
                ui.label("From").classes("text-weight-medium")
                start_h = ui.select(
                    list(range(1, 13)),
                    value=10,
                    label="Hour",
                ).classes("min-w-[100px]")
                start_m = ui.number("Min", value=30, min=0, max=59, format="%.0f").classes(
                    "min-w-[88px]"
                )
                start_ap = ui.select(["AM", "PM"], value="AM", label="").classes("min-w-[88px]")

            with ui.row().classes("w-full flex-wrap items-end gap-4 mt-2"):
                ui.label("To").classes("text-weight-medium")
                end_h = ui.select(
                    list(range(1, 13)),
                    value=8,
                    label="Hour",
                ).classes("min-w-[100px]")
                end_m = ui.number("Min", value=0, min=0, max=59, format="%.0f").classes(
                    "min-w-[88px]"
                )
                end_ap = ui.select(["AM", "PM"], value="PM", label="").classes("min-w-[88px]")

            async def load_schedule_from_user() -> None:
                try:
                    tz = await _browser_timezone()
                    with get_db_context() as db:
                        user = get_current_user_from_state(db)
                        s_local, e_local = utc_window_to_local_hhmm_pair(
                            user.distraction_block_start,
                            user.distraction_block_end,
                            tz,
                        )
                    sh, sm, sap = hhmm_to_ampm_parts(s_local)
                    eh, em, eap = hhmm_to_ampm_parts(e_local)
                    start_h.value = sh
                    start_m.value = sm
                    start_ap.value = sap
                    end_h.value = eh
                    end_m.value = em
                    end_ap.value = eap
                except HTTPException:
                    pass

            async def save_schedule() -> None:
                try:
                    s_hhmm = ampm_parts_to_hhmm(
                        int(start_h.value),
                        int(start_m.value or 0),
                        str(start_ap.value),
                    )
                    e_hhmm = ampm_parts_to_hhmm(
                        int(end_h.value),
                        int(end_m.value or 0),
                        str(end_ap.value),
                    )
                except ValueError as e:
                    notifications.show_error(str(e))
                    return
                if not is_valid_hhmm(s_hhmm) or not is_valid_hhmm(e_hhmm):
                    notifications.show_error("Invalid time; use hours 1–12 and minutes 0–59.")
                    return
                tz = await _browser_timezone()
                s_utc, e_utc = local_window_to_utc_hhmm_pair(s_hhmm, e_hhmm, tz)
                try:
                    with get_db_context() as db:
                        user = get_current_user_from_state(db)
                        user_repo.update_distraction_schedule(
                            db, user=user, start=s_utc, end=e_utc
                        )
                    notifications.show_success("Schedule saved.")
                except HTTPException as e:
                    notifications.show_error(e.detail)
                except Exception as e:
                    notifications.show_error(str(e))

            ui.button("Save schedule", on_click=save_schedule, icon="schedule").classes(
                "mt-4"
            ).props("color=primary")

        with ui.card().classes("w-full max-w-3xl p-6 mt-4"):
            ui.label("Blocked sites").classes("text-h6 text-emerald-700 dark:text-emerald-300")
            ui.label("Enter a hostname (e.g. youtube.com). www. is stripped automatically.").classes(
                "text-caption text-slate-500 mt-1 mb-4"
            )

            site_input = ui.input(
                "Site to block",
                placeholder="youtube.com",
            ).classes("w-full max-w-lg")

            sites_column = ui.column().classes("w-full gap-2 mt-4")

            def remove_hostname(hostname: str) -> None:
                try:
                    with get_db_context() as db:
                        cur = get_current_user_from_state(db)
                        blocked_site_repo.delete(db, owner_id=cur.id, url=hostname)
                    notifications.show_success(f"Removed {hostname}")
                    refresh_site_rows()
                except HTTPException as err:
                    notifications.show_error(err.detail)
                except Exception as ex:
                    notifications.show_error(str(ex))

            def refresh_site_rows() -> None:
                sites_column.clear()
                try:
                    with get_db_context() as db:
                        user = get_current_user_from_state(db)
                        urls = blocked_site_repo.list_urls(db, owner_id=user.id)
                except HTTPException:
                    urls = []
                with sites_column:
                    for host in urls:
                        with ui.row().classes(
                            "w-full items-center gap-2 py-2 px-3 rounded-lg bg-slate-100 dark:bg-slate-900"
                        ):
                            ui.label(host).classes("flex-grow text-body1")
                            ui.button(
                                icon="delete",
                                on_click=lambda h=host: remove_hostname(h),
                            ).props("flat dense round color=negative")

            def add_site() -> None:
                host = _normalize_hostname(site_input.value or "")
                if not host:
                    notifications.show_error("Enter a site hostname.")
                    return
                try:
                    with get_db_context() as db:
                        user = get_current_user_from_state(db)
                        blocked_site_repo.add(db, owner_id=user.id, url=host)
                    notifications.show_success(f"Added {host}")
                    site_input.value = ""
                    refresh_site_rows()
                except HTTPException as e:
                    notifications.show_error(e.detail)
                except Exception as e:
                    notifications.show_error(str(e))

            with ui.row().classes("w-full gap-2 items-end"):
                site_input.on("keydown.enter", add_site)
                ui.button("Add site", on_click=add_site, icon="add").props("color=primary")

            refresh_site_rows()

        await load_schedule_from_user()
