from fasthtml.common import (
    # FastHTML's HTML tags
    A, AX, Button, Card, CheckboxX, Container, Div, Form, Grid, Group,P, H1, H2, H3, H4, H5, Hr, Hidden, Input, Li, Ul, Ol, Main, Script, Style, Textarea, Title, Titled, Select, Option, Table, Tr, Th, Td,
    # FastHTML's specific symbols
    Beforeware, FastHTML, fast_app, SortableJS, fill_form, picolink, serve, NotStr,
    # From Starlette, Fastlite, fastcore, and the Python standard library:
    FileResponse, NotFoundError, RedirectResponse, database, patch, dataclass, UploadFile
)

import os
import markdown
from pathlib import Path
from datetime import datetime

# This will be our 404 handler, which will return a simple error page.
def _not_found(req, exc): return Titled('Oh no!', Div('We could not find that page :('))

# FastHTML includes the "HTMX" and "Surreal" libraries in headers, unless you pass `default_hdrs=False`.
app = FastHTML(exception_handlers={404: _not_found},
               # PicoCSS is a tiny CSS framework that we'll use for this project.
               # `picolink` is pre-defined with the header for the PicoCSS stylesheet.
               hdrs=(picolink,
                     # `Style` is an `FT` object, which are 3-element lists consisting of:
                     # (tag_name, children_list, attrs_dict).
                     Style(':root { --pico-font-size: 100%; }'),
                )
      )

# `app.route` (or `rt`) requires only the path, using the decorated function's name as the HTTP verb.
rt = app.route

@rt("/") # Index page
def get():
    return Titled('Barts Blog', Div('Welcome to my blog!'))

# Directory containing the markdown files
content_dir = Path("example_content")

@rt("/posts")
def list_posts():
    posts = sorted(
        [f.stem for f in content_dir.glob("*.md")],
        key=lambda f: (content_dir / f"{f}.md").stat().st_ctime,
        reverse=True
    )
    return Titled(
        'Barts Blogs', 
        P('Intro tekst'),
        H4(Ol(*[Li(A(post, href=f"/posts/{post}")) for post in posts], reversed=True)),
    )

@rt("/posts/src/{src_name}")
def get_src(src_name: str):
    src_path = content_dir / src_name
    if not src_path.exists():
        raise NotFoundError()
    
    return FileResponse(src_path)

@rt("/posts/{name}")
def get_post(name: str):
    if "." in name:  # Check if the name has a file extension
        src_path = content_dir / name
        if not src_path.exists():
            raise NotFoundError()
        return FileResponse(src_path)
    
    # Else its a post in markdown

    post_path = content_dir / f"{name}.md"
    if not post_path.exists():
        raise NotFoundError()
    
    with open(post_path, "r", encoding="utf-8") as f:
        md_content = f.read()
        print(md_content)
        creation_date = datetime.fromtimestamp(post_path.stat().st_ctime)
        last_modified_date = datetime.fromtimestamp(post_path.stat().st_mtime)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(md_content)


    return Titled(
        name,
        f'Geschreven op {creation_date.strftime("%A, %-d %B %Y")}',
        Hr(),
        NotStr(html_content),
        Hr(),
        A("Terug", href="/posts")
    )



serve()