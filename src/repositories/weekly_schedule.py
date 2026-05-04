from typing import List, Optional

from fastapi import HTTPException
from sqlmodel import Session, select

from src.core.constants import TASK_CATEGORIES
from src.models.models import User, WeeklyScheduleEntry, WeeklyScheduleEntryUpdate


def _normalize_category(value: Optional[str]) -> str:
    if value and value in TASK_CATEGORIES:
        return value
    return "general"


class WeeklyScheduleRepository:
    def list_for_owner(self, db: Session, *, owner_id: int) -> List[WeeklyScheduleEntry]:
        return db.exec(
            select(WeeklyScheduleEntry)
            .where(WeeklyScheduleEntry.owner_id == owner_id)
            .order_by(
                WeeklyScheduleEntry.importance,
                WeeklyScheduleEntry.due_day,
                WeeklyScheduleEntry.sort_order,
                WeeklyScheduleEntry.id,
            )
        ).all()

    def get(self, db: Session, id: int) -> Optional[WeeklyScheduleEntry]:
        return db.get(WeeklyScheduleEntry, id)

    def get_with_permission(
        self, db: Session, *, id: int, current_user: User
    ) -> WeeklyScheduleEntry:
        row = self.get(db, id=id)
        if not row:
            raise HTTPException(status_code=404, detail="Schedule entry not found")
        if not current_user.is_superuser and row.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Insufficient permission")
        return row

    def _next_sort_order(
        self,
        db: Session,
        *,
        owner_id: int,
        due_day: str,
        importance: int,
    ) -> int:
        rows = db.exec(
            select(WeeklyScheduleEntry).where(
                WeeklyScheduleEntry.owner_id == owner_id,
                WeeklyScheduleEntry.due_day == due_day,
                WeeklyScheduleEntry.importance == importance,
            )
        ).all()
        if not rows:
            return 0
        return max(int(r.sort_order or 0) for r in rows) + 1

    def create(
        self,
        db: Session,
        *,
        owner_id: int,
        name: str,
        due_day: str,
        importance: int,
        category: str = "general",
    ) -> WeeklyScheduleEntry:
        cat = _normalize_category(category)
        sort_order = self._next_sort_order(
            db, owner_id=owner_id, due_day=due_day, importance=importance
        )
        row = WeeklyScheduleEntry(
            name=name,
            due_day=due_day,
            importance=importance,
            category=cat,
            sort_order=sort_order,
            owner_id=owner_id,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    def shift_sort_order_in_cell(
        self,
        db: Session,
        *,
        entry_id: int,
        delta: int,
        current_user: User,
    ) -> None:
        """Move an entry earlier (-1) or later (+1) among siblings sharing day + importance."""
        if delta not in (-1, 1):
            raise HTTPException(status_code=400, detail="Invalid reorder direction")
        row = self.get_with_permission(db, id=entry_id, current_user=current_user)
        siblings = list(
            db.exec(
                select(WeeklyScheduleEntry)
                .where(
                    WeeklyScheduleEntry.owner_id == row.owner_id,
                    WeeklyScheduleEntry.due_day == row.due_day,
                    WeeklyScheduleEntry.importance == row.importance,
                )
                .order_by(
                    WeeklyScheduleEntry.sort_order,
                    WeeklyScheduleEntry.id,
                )
            ).all()
        )
        idx = next((i for i, s in enumerate(siblings) if s.id == entry_id), None)
        if idx is None:
            raise HTTPException(status_code=404, detail="Schedule entry not found")
        jdx = idx + delta
        if jdx < 0 or jdx >= len(siblings):
            return
        siblings[idx], siblings[jdx] = siblings[jdx], siblings[idx]
        for i, s in enumerate(siblings):
            s.sort_order = i
            db.add(s)
        db.commit()

    def update(
        self,
        db: Session,
        *,
        db_obj: WeeklyScheduleEntry,
        obj_in: WeeklyScheduleEntryUpdate,
    ) -> WeeklyScheduleEntry:
        data = obj_in.model_dump(exclude_unset=True)
        if "category" in data:
            data["category"] = _normalize_category(data.get("category"))

        prev_day, prev_imp = db_obj.due_day, db_obj.importance
        for field, value in data.items():
            setattr(db_obj, field, value)

        cell_changed = (
            db_obj.due_day != prev_day or db_obj.importance != prev_imp
        )
        if cell_changed:
            others = db.exec(
                select(WeeklyScheduleEntry).where(
                    WeeklyScheduleEntry.owner_id == db_obj.owner_id,
                    WeeklyScheduleEntry.due_day == db_obj.due_day,
                    WeeklyScheduleEntry.importance == db_obj.importance,
                    WeeklyScheduleEntry.id != db_obj.id,
                )
            ).all()
            max_so = max((int(o.sort_order or 0) for o in others), default=-1)
            db_obj.sort_order = max_so + 1

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> WeeklyScheduleEntry:
        obj = db.get(WeeklyScheduleEntry, id)
        if obj is None:
            raise HTTPException(status_code=404, detail="Schedule entry not found")
        db.delete(obj)
        db.commit()
        return obj


weekly_schedule_repo = WeeklyScheduleRepository()
