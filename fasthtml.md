# FastHTML MCP Style Guide

This document summarizes the FastHTML "MCP-style" conventions used in this project (Markdown-Blog). It captures how routes, views, templates, content, configuration and mail are organized so you can extend or maintain the codebase consistently.

## Big picture

- FastHTML apps are defined using `FastHTML` (in `make_app.py`) and routes are registered with the `app.route` decorator. Projects return FastHTML tag objects (A, Div, Card, Titled, etc.) from view functions — not string templates.
- The project uses a simple file-based content model: `content_dir/<blog>/<post>/` holds markdown files and assets (images). Each markdown file is an "update"; filenames that look like `YYYYMMDD` are parsed as dates.
- Configuration (blogs, mail, content_dir, domain, image_width, etc.) lives in `config.yaml` and is loaded by `make_app.py` into variables like `blogs_config`, `mail_config`, `content_dir`.
- HTMX is used for simple dynamic interactions (subscribe/unsubscribe forms, button swaps) via `hx_post`, `hx_delete`, `hx_swap`, etc. FastHTML includes HTMX and Surreal by default unless overridden.
- PicoCSS is used for styling via the `picolink` header and a `styles.css` file included as a `Style` header.

## Files and responsibilities

- `make_app.py` — Bootstraps the `FastHTML` app, loads `config.yaml`, exposes `app`, `blogs_config`, `content_dir`, and other shared globals.
- `main.py` — Route handlers for the site (landing page, list blogs, list posts, serve static files, serve posts). It imports `app` and registers routes. Typical pattern: `rt = app.route` then `@rt("/path")`.
- `update.py` — Presents rendered markdown updates and small helpers (e.g., `Update()` and `EmailUpdate()` that convert markdown -> HTML using `markdown.markdown`, wrap into `Div`/`NotStr`, and add dates when filenames are parsable).
- `mail.py` — Subscriber forms and mailing logic (subscribe/unsubscribe endpoints that store emails in `mailing_lists/<blog>.txt`, and the send flow that assembles an HTML email with inline images and sends via SMTP credentials from `config.yaml` + `SMTP_PASSWORD` env var).
- `content/` — Stores blog directories. Each blog directory (matching a key in `config.yaml`) contains post directories, which in turn contain markdown files and assets.

## Common code patterns and idioms

- Views return FastHTML components. Example:
  - return Titled("Page title", Div(...), H1("Heading"), ...)
- Wrap pre-rendered HTML with `NotStr(...)` to tell FastHTML to emit raw HTML (use when you call `markdown.markdown(...)`).
- Use `A(...)` with `hx_boost="true"` to make links navigate via HTMX where desired.
- Route functions accept typed path/query/form parameters directly (e.g., `def get_post(blog: str, post_name: str):`).
- Static assets are served via a route like `/static/{filename}` using `FileResponse` from `pathlib.Path`.
- Markdown-to-HTML pipeline in `update.py`:
  - Read file: `update_path.read_text(encoding='utf-8')`
  - Convert: `markdown.markdown(..., extensions=["markdown.extensions.tables"], output_format="html")`
  - Post-process: add responsive table class, limit image width, adjust src paths for post-relative addressing.
- Dates: filenames that are 8-digit numbers parse to `YYYYMMDD` via `datetime.strptime`; if parsing fails, date is omitted.

## Email/send flow

- Subscribers per-blog are stored in `mailing_lists/<blog>.txt` (one email per line).
- Subscribe endpoint (`/blogs/{blog}/subscribe`) appends unique emails; unsubscribe removes the line.
- Sending a post (`/blogs/{blog}/post/{post_name}/send`) is protected by checking `ADMIN_PASSWORD` in env vs `password` query param. It:
  1. Reads markdown files for the post and builds email HTML using `EmailUpdate()`.
  2. Extracts image `src` attributes, rewrites `src="` to `src="cid:` for inline embedding.
  3. Calls `send_html_to_subscribers()` which assembles a `MIMEMultipart` message, converts/resizes images with PIL, attaches them with `Content-ID` headers and uses `smtplib.SMTP_SSL` to send to each subscriber.
- `SMTP_PASSWORD` must be set in env; other SMTP details are in `config.yaml` under `mail`.

## Configuration shape (observed keys)

The `config.yaml` used in this project contains at least the following keys (example names observed in code):

- content_dir: path to content (e.g., "content")
- blogs: mapping of blog slug -> blog config. Each blog config can include:
  - title
  - intro
  - back (text used for back-links)
  - written (prefix text used with date formatting)
  - locale (for babel date formatting)
  - email: mapping containing subscribe/unsubscribe button texts, subject, link, subscribe_success, etc.
  - disclaimer (text to show near MailForm)
- mail: SMTP settings (sender, smtp.server, smtp.port, smtp.user)
- domain: site domain used in email links
- image_width: target width for inline images in emails

Note: Inspect your `config.yaml` for the exact shape; adjust the doc if you add new fields.

## Contracts (small)

- Input: A view function receives path/query/form parameters. `content_dir` holds well-formed blog directories. Markdown files are UTF-8 encoded.
- Output: FastHTML tag objects, `FileResponse` for files, or `Response` with status codes for errors.
- Error modes: missing content -> 404 `Response`, missing env vars (e.g., `SMTP_PASSWORD`) -> log and skip action.
- Success criteria: pages render and mail send endpoints return 200 when done.

## Edge cases to handle / tests to add

- Missing blog key in `blogs_config` should return 404 or a friendly error.
- Malformed date filenames shouldn't crash date formatting.
- Mailing list file concurrent writes: current code uses simple `r+` and could suffer race conditions if two subscribers subscribe at the same time — consider file locking or using a simple DB.
- Email address validation is minimal (`"@" in email`) — consider stricter validation.
- Missing `SMTP_PASSWORD` prevents sending; report a clear error.
- Large images in posts should be resized for emails (current code resizes to `image_width`), but be mindful of memory when processing many images.

## Recommended small improvements (low-risk)

- Replace plain text mailing-list storage with a tiny SQLite DB (`mailing_lists.db`) or use atomic file writes to avoid race conditions.
- Add simple input sanitization for markdown or use `bleach` when embedding untrusted HTML.
- Centralize config access in a small helper module to avoid importing many globals across files.
- Add unit tests for `Update()`/`EmailUpdate()` to ensure markdown conversion, table classes and image path rewrites behave as expected.
- Document the `config.yaml` schema and provide an example file `config.example.yaml`.

## Examples / patterns reference

- Route and view:
  - rt = app.route
  - @rt("/blogs/{blog:str}/")
  - def list_posts(blog: str):
      return Titled(blog_config['title'], P(...), *[A(H4(post), href=f"/blogs/{blog}/post/{post}") for post in posts])

- Markdown render (from `update.py`):
  - NotStr(markdown.markdown(txt, extensions=["markdown.extensions.tables"], output_format="html"))

- Subscribe endpoint (from `mail.py`):
  - with Path(`mailing_lists/<blog>.txt`).open("r+") as file: read lines; if not present append; return Button(...)

---

This guide should be enough to onboard contributors to the FastHTML style used here. If you'd like, I can extend this with a `config.example.yaml`, unit tests for the markdown pipeline, and a small `docs/` index linking to this guide and the `UpgradePlan`.