## Goals (prioritized)

1. Clean up FastHTML codebase and document it better (low-risk foundations).
2. Make the landing page dynamic (select/dropdown influencing cards) without adding a DB; keep file-based content.
3. Add a portfolio blog integrated into the landing page and the existing blog system.
4. Improve mail/send flow: prevent accidental duplicate sends, add safer send controls, and harden mailing-list handling.
5. Add provision for symlinking to content stored in user Documents (and document server patterns).
6. Dockerize the app for easier deployment.

---

## Assumptions

- The project will remain file-based for content (no DB) unless we explicitly decide to add one.
- `config.yaml` defines `content_dir`, `blogs`, `mail`, `domain`, and `image_width`.
- We will avoid breaking public behavior; changes / migrations will be incremental and tested.

---

## Plan: phases, milestones and tasks

Phase A — Foundations (clean + docs) [1 week]
- Purpose: create a stable, well-documented codebase so later changes are easy and low-risk.
- Tasks:
	- Add `fasthtml.md` (style guide) — done.
	- Add `config.example.yaml` documenting expected keys and an example `blogs` entry.
	- Centralize app globals (optionally extract a small `core.py` or strengthen `make_app.py`). Goal: minimize cross-file imports of ad-hoc globals.
	- Add simple unit tests for `update.Update`/`EmailUpdate` pipeline (markdown -> html, date parsing, image src rewriting).
	- Add a README section describing local dev steps + env vars (`SMTP_PASSWORD`, `ADMIN_PASSWORD`).

Phase B — Landing page and portfolio [1–2 weeks]
- Purpose: make landing page configurable and add a portfolio blog that uses the same content model.
- Tasks:
	- Design the landing dropdown data model: small JSON/YAML config in `config.yaml` or a `landing.json` that lists options and card metadata (title, image, tags, slug for linking to a blog).
	- Implement UI: a `Select` element on landing page; tie selection to card filter. Use HTMX for in-page updates (`hx-get` / `hx-target`) — no DB required.
	- Create `content/portfolio/` and document its structure so the portfolio blog uses the same handlers as other blogs (add an entry in `config.yaml` under `blogs`).
	- Add a sample portfolio post with images and ensure email send/rendering still works for portfolio posts.

Phase C — Mail + send protections [1 week]
- Purpose: make mail sending safe and reliable.
- Tasks:
	- Add send-locking: when `/send` endpoint is called, create a small lock file (e.g., `mail_locks/<blog>/<post>.lock`) or set an atomic flag in a tiny SQLite DB to prevent duplicate sends. Remove lock on success or expiration.
	- Add `last_sent` metadata: store last sent timestamp per post to avoid accidental re-sends (file-based JSON or tiny DB). Show confirmation page before sending listing recipients count and requiring ADMIN_PASSWORD and a confirm button.
	- Harden subscriber storage: either use append-only file writes with file locks (fcntl) or replace `mailing_lists/*.txt` with a small SQLite table (`email TEXT UNIQUE`), plus an administrative export/import script.
	- Improve email validation (regex) and optional double opt-in (future).

Phase D — Content symlinks & server considerations [3–5 days]
- Purpose: let authors store content in `~/Documents` and let the server reference it via symlinks.
- Tasks:
	- Document symlink plan in `fasthtml.md` and in an ops note: on the server, create a secure path (e.g., `/srv/markdown/`) and symlink `content/portfolio` -> `/home/<user>/Documents/Blog/`.
	- Add startup checks in `make_app.py` that validate `content_dir` and warn if any symlink points outside allowed paths (optional security check).

Phase E — Dockerize and deploy [2–3 days]
- Purpose: make running locally and on server reproducible.
- Tasks:
	- Add `Dockerfile` and `docker-compose.yml` for a minimal production run (Uvicorn + FastHTML). Keep secrets via env vars.
	- Add a small `startup.sh` (already present) and document how to run in container.
	- Test email send flow inside Docker (ensure `SMTP_PASSWORD` arrives via env).

---

## Implementation checklist (concrete files to change)

- `config.example.yaml` (new) — document schema.
- `fasthtml.md` (new) — style guide (created).
- `UpgradePlan.md` (this file) — update and keep current.
- `make_app.py` — possible small refactor (centralize config access; add `validate_config()` and `startup_checks`).
- `main.py` — landing page change (add dropdown UI; small HTMX endpoints to filter cards), minor cleanup.
- `update.py` — add tests for markdown pipeline; ensure safe handling of missing files.
- `mail.py` — add lock/last_sent handling, improve validation, optionally migrate mailing list storage to SQLite.
- tests/ — add unit tests for `update.Update`, `EmailUpdate`, and mail subscribe/unsubscribe logic.

---

## Next steps (what I can do for you now)

1. Create `config.example.yaml` and a sample `content/portfolio/` post and wire it into `config.yaml` (I can add those files).
2. Implement a non-DB landing page dropdown using HTMX and a small `landing:` section in `config.yaml` mapping options to card filters.
3. Implement send-locking and `last_sent` metadata (file-based first, then optional SQLite migration).

If you want, I can start with item A (centralized docs + `config.example.yaml` + 1-2 unit tests) and open a feature branch for the landing page change.

---

Notes:
- I kept the plan incremental and file-based to reduce risk. If you prefer to move faster using SQLite for mailing lists and locks, we can do that earlier (it simplifies concurrency and deduplication).
- I can also create a PR template and a `CONTRIBUTING.md` if you expect collaborators.
