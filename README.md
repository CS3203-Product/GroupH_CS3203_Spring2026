# 🌿 UnCram · CS3203 Productivity App

> **Stay organized. Block noise. Ship your work.**

UnCram is a full-stack productivity workspace built with **NiceGUI** and **FastAPI**: task boards, weekly scheduling, Pomodoro-style focus, ambient audio, priorities, and a collaboration hub — backed by **PostgreSQL** and JWT auth (from the [NiceGUI + FastAPI template](https://github.com/jaehyeon-kim/nicegui-fastapi-template)).

---

## ✨ What you get

| Area | Description |
|------|-------------|
| 🗂️ **Task board** | Card-style items tied to your account (demo data layer). |
| 📅 **Schedule** | Importance × weekday grid for time blocking. |
| ⏱️ **Focus timer** | Pomodoro flow with local alarm audio. |
| 🎧 **Ambient** | Streamed ambient sample + audio manager presets. |
| 📌 **Priorities** | Quick capture UI with day buckets. |
| 👥 **Collaboration** | Tasks, invites, accept/decline (session-scoped UI state). |
| 🚫 **Distraction blocker** | Web UI for blocked sites + schedule; Chrome MV3 extension enforces blocking. |
| 🔐 **API** | `/docs` Swagger for JSON endpoints (`/api/v1/...`). |

---

## 🧱 Project layout

```text
app.py                 # Entry: NiceGUI + FastAPI, static mounts, routers
DistractionBlocker_extension/   # Load unpacked in Chrome/Edge (see below)
assets/sound/          # Served at /assets/sound (e.g. alarm.mp3)
src/
  ambient_focus/       # AudioManager, presets, Spotify/YouTube stubs
  productivity/        # Scheduling, Uncram, analytics, focus, distraction blocker
  frontend/            # Pages, layout, theme, auth state
  backend/, core/, db/, models/, repositories/   # API + SQLModel stack
tests/                 # pytest (scheduler, collaboration, analytics, audio, blocker)
```

---

## 🚀 Quick start

### 1 · Prerequisites

- Python **3.10+**: https://www.python.org/downloads/
- Visual Studio Code: https://code.visualstudio.com/download
- **Docker** (for PostgreSQL): https://www.docker.com/get-started/

### 2 · Clone & virtualenv

```bash or powershell
git clone https://github.com/CS3203-Product/GroupH_CS3203_Spring2026.git
cd CS3203-Productivity-App
python3 -m venv .venv
Mac: source .venv/bin/activate
Windows: .venv\Scripts\activate    
pip install -r requirements.txt
# Windows: If "running on scripts is disabled" appears, run Powershell as an administrator,
# run Set-ExecutionPolicy -Scope CurrentUser RemoteSigned, type A and hit enter
```


### 3 · Environment

```bash or powershell
Mac: cp .env.template .env
Windows: Copy-Item .env.template .env
# Edit .env if needed (defaults match docker-compose)
```

### 4 · Database
Open Docker, and sign in (or create an account)
```bash or powershell
docker compose up -d
```
Open CS3203-Productivity-App in Visual Studio Code, then open docker-compose.yml and .env
Ensure `DATABASE_URL` in `.env` matches the **host port** mapped in `docker-compose.yml` (e.g. `localhost:55432` if you use that mapping).

### 5 · Run the app

```bash or powershell
Mac: source .venv/bin/activate
Windows: .venv\Scripts\Activate.ps1
python app.py
```

App should open automnatically, if not then open:

- 🖥️ **App:** [http://localhost:8000](http://localhost:8000)
- 📘 **Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)

Default superuser (change in production!) is set in `.env` as `FIRST_SUPERUSER` / `FIRST_SUPERUSER_PASSWORD`.

---

## 🚫 Distraction Blocker (browser extension)

The extension checks each top-level navigation against your **blocked sites** and **blocking schedule** stored in the app database. The backend must be running and reachable from the browser.

### 1 · Configure blocking in UnCram

1. Sign in to the web app (same account you will use in the extension).
2. Open **Distraction blocker** in the left drawer.
3. Add hostnames to block (for example `youtube.com`). Paste a full URL if you like; `www.` is stripped automatically.
4. Set **From** / **To** with **AM/PM** and click **Save schedule**. That window is when listed sites are treated as blocked (overnight ranges are supported if “from” is later than “to”).

### 2 · Install the extension (Chrome or Edge)

1. Open `chrome://extensions` (Chrome) or `edge://extensions` (Edge).
2. Turn on **Developer mode**.
3. Click **Load unpacked** and choose the folder **`DistractionBlocker_extension`** at the root of this repo (the folder that contains `manifest.json`).

### 3 · Point the extension at your API and sign in

1. Open the extension’s **options** page: from `chrome://extensions`, click **Details** under “Distraction Blocker”, then **Extension options** (or open the options URL Chrome shows for the extension).
2. **API base URL**: use the origin where UnCram runs, **no trailing slash** — for local dev this is usually `http://localhost:8000`. For a deployed server, use that HTTPS origin instead.
3. Click **Save API URL** if you changed it.
4. Enter your **email** and **password** (same as the web app) and click **Sign in**. The extension stores a JWT and your user id in extension storage.

Until you sign in, the background script will not redirect tabs.

### 4 · Verify

With the app running and you signed in, browse to a hostname on your blocked list **during your saved schedule**. The tab should redirect to the extension’s blocked page.

**Troubleshooting**

- **401 / sign-in errors**: Confirm the API URL matches the running server and credentials are correct.
- **Nothing blocked**: Check the **Distraction blocker** page for the hostname and schedule; remember blocking only applies inside the configured time window.
- **Production**: Serve the app over **HTTPS** and use that URL as the API base; mixed content may block `fetch` from an HTTPS page to `http://localhost`.

---

## 🧪 Tests

```bash
source .venv/bin/activate
pytest tests/ -v
```

Or unittest-style for a single module:

```bash or powershell
python -m unittest tests.test_collaboration -v
```

---

## 🎨 UI theme

The app uses an **emerald / slate** palette, dark mode by default, and a left **workspace** drawer for navigation. Static audio lives under **`/assets/sound`**.

---

## 🗺️ Roadmap (high level)

- **Phase 1 — Focus:** timer polish, distraction blocker polish, richer ambient library.  
- **Phase 2 — Progress:** analytics dashboards, collaboration polish, shared calendars.

---

## 👥 Team

- [dopc](https://discord.com)
- [thesilverback4521](https://discord.com)
- [cindaman](https://discord.com)
- [yoghurtboy](https://discord.com)
- [nguyetng](https://discord.com)
- [onejosh](https://discord.com)
- [crazinessjoy](https://discord.com)

Reach the CS3203 team on [Discord](https://discord.com) (handles from course roster / group agreement).

---

*Built with Python · NiceGUI · FastAPI · PostgreSQL*
