from fasthtml.common import (
    # FastHTML's HTML tags
    A, AX, Button, Card, CheckboxX, Container, Div, Form, Grid, Group,P, H1, H2, H3, H4, H5, Hr, Hidden, Input, Li, Ul, Ol, Main, Script, Style, Textarea, Title, Titled, Select, Option, Table, Tr, Th, Td,
    # FastHTML's specific symbols
    Beforeware, FastHTML, fast_app, SortableJS, fill_form, picolink, serve, NotStr,
    # From Starlette, Fastlite, fastcore, and the Python standard library:
    FileResponse, Response ,NotFoundError, RedirectResponse, database, patch, dataclass, UploadFile
)


from h11 import Request
import markdown
from pathlib import Path
from datetime import datetime
import yaml
import locale

# Load configuration from a YAML file
config_path = Path("config.yaml")

def load_config(path):
    with open(path, "r") as file:
        return yaml.safe_load(file)

config = load_config(config_path)

# Directory containing the markdown files
content_dir = Path(config['blog']['content_dir'])

# Set locale based on configuration
locale.setlocale(locale.LC_TIME, config['blog']['locale'])



# This will be our 404 handler, which will return a simple error page.
def _not_found(req, exc): return Titled(config['blog'][404]['title'], Div(config['blog'][404]['content']))

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

@rt("/")
def list_posts():
    posts = sorted(
        [d.name for d in content_dir.iterdir() if d.is_dir()],
        key=lambda d: d.split("-")[0],
        reverse=True
    )
    return Titled(
        config['blog']['title'],
        P(config['blog']['intro']),
        *[A(H4(post), href=f"/post/{post}") for post in posts],
    )

@rt("/post/{name:str}")
def get_post(name: str):
    post_dir = content_dir / f"{name}"
    md_files = sorted([f for f in post_dir.iterdir() if f.suffix == ".md"])
    
    if not md_files:
        return Response("File not found", status_code=404)
    
    posts = [Div(
            f'Geschreven op {datetime.fromtimestamp(post_path.stat().st_ctime).strftime("%A, %-d %B %Y")}',
            Hr(),
            NotStr(
                markdown.markdown(
                    post_path.read_text(encoding="utf-8")
                    ).replace('src="', f'src="{name}/')
                ),
            Hr(),
        )
        for post_path in md_files
    ]


    return Titled(
        name,
        *posts,
        A(config['blog']['back'], href="/")
    )

@rt("/post/{name:str}/{file:str}")
def get_post_file(name: str, file: str):
    post_dir = content_dir / f"{name}"
    post_file = post_dir / f"{file}"
    
    if not post_file.exists():
        # Return a 404 response without raising an exception
        return Response("File not found", status_code=404)
    
    return FileResponse(post_file)



serve()