Implementation artifacts and low-risk starter work

This file captures a concrete list of files to change, tests to add, and small low-risk extras to implement next (from the UpgradePlan Phase A/B/C). Use this as a checklist for incremental PRs.

1) Files to change (concrete)

- `make_app.py`
  - Add `validate_config()` and small `startup_checks()` that ensure `content_dir` exists and `blogs` keys are present.
  - Expose `landing_config` (already done).

- `main.py`
  - Add landing-select UI (done).
  - Add HTMX endpoint to return cards (done).
  - Small cleanup: use `core.get_blog_config()` once `core.py` is adopted.

- `mail.py`
  - Add send-locking and `last_sent` metadata. Provide an endpoint that returns recipients count and requires explicit confirm.
  - Replace naive text file append with atomic writes and optional SQLite migration helper.

- `update.py`
  - Add unit tests for `Update()` and `EmailUpdate()` (tests added).
  - Centralize markdown rendering options into a helper function to make tests and email rendering consistent.

- `config.yaml` / `config.example.yaml`
  - Add `landing` section (example already added).
  - Add `portfolio` blog example (done in example and `config.yaml`).

2) Tests to add (concrete)

- tests/test_update.py (done)
  - Happy-path markdown rendering for dated and non-dated filenames.

- tests/test_mail.py (skeleton created)
  - Subscribe/unsubscribe flows using temporary mailing list files.
  - Atomic write behavior or SQLite-backed dedup test.
  - send-lock creation and removal (simulate success/failure).

- tests/test_landing_ui.py (skeleton created)
  - Test `/landing/cards` returns expected number of card items for each `role`.
  - Test fallback behavior when `landing` config missing.

3) Low-risk extras to implement now (starter code included)

- `core.py` (created) — tiny helpers to centralize paths and small utilities:
  - `get_blogs_config()`
  - `get_landing_config()`
  - `mailing_list_path(blog)`
  - `mail_lock_path(blog, post_name)`
  - `last_sent_path(blog, post_name)`

- Test stubs and fixtures to make later TDD straightforward.

4) Migration/ops helpers (later)

- `scripts/migrate_mailing_lists_to_sqlite.py` — export existing `mailing_lists/*.txt` into `mailing.db` with `email` unique index.
- `scripts/symlink_content.sh` — documented helper for creating symlinks from user Documents to server content dir.

5) Contracts and acceptance criteria (small)

- Markdown rendering helper returns (html_string, list_of_image_paths).
- Subscribe endpoint accepts `email` and returns HTTP 200 with a normalized message.
- Send endpoint returns 200 only after ADMIN_PASSWORD and an explicit confirm action.
- Tests must pass locally (`pytest`).

6) Next small PR suggestions

- PR1: docs + tests (this PR): `IMPLEMENTATION.md`, tests, `config.example.yaml` (done), small `core.py` (done).
- PR2: landing UX complete + examples (done partially).
- PR3: mail protections: locking, last_sent metadata, atomic writes or SQLite migration.
- PR4: Dockerfile + docker-compose.


Notes

- Keep changes small and incremental. When introducing SQLite, provide migration scripts and keep file-based method as fallback.
- Use atomic file writes using a temporary file + rename or use `sqlite` for concurrency-safe operations.
