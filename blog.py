from argparse import Action
from ast import Return
from calendar import c
from gc import disable
from fasthtml.common import (
    # FastHTML's HTML tags
    A, AX, Button, Card, CheckboxX, Container, Div, Form, Grid, Group,P,I, H1, H2, H3, H4, H5, Hr, Hidden, Input, Li, Ul, Ol, Main, Script, Style, Textarea, Title, Titled, Select, Option, Table, Tr, Th, Td,
    # FastHTML's specific symbols
    Beforeware, FastHTML, fast_app, SortableJS, fill_form, picolink, serve, NotStr,
    # From Starlette, Fastlite, fastcore, and the Python standard library:
    FileResponse, Response ,NotFoundError, RedirectResponse, database, patch, dataclass, UploadFile
)


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
                     Style(':root { --pico-font-size: 100%}'),
                )
      )

# `app.route` (or `rt`) requires only the path, using the decorated function's name as the HTTP verb.
rt = app.route


def MailForm():
    return Group(
                Input(placeholder="Email", type="email", id="email"),
                Button("", id="info", disabled=True, style="width: 30%;", cls="secondary"),
                Button(config['blog']['email']['subscribe'], hx_post="/subscribe", hx_swap="innerHTML", hx_include="#email", hx_target="#info"),
                Button(config['blog']['email']['unsubscribe'], hx_delete="/unsubscribe", hx_swap="innerHTML", hx_include="#email", hx_target="#info", cls="outline"),
                style="width: 100%",
            ),



def Update(path, name):
    if path.stem.isdigit() and len(path.stem) == 8:
        try:
            date = datetime.strptime(path.stem, "%Y%m%d")
        except ValueError:
            date = None
    else:
        date = None

    return Div(
        Hr(),
        NotStr(
            markdown.markdown(
                path.read_text(encoding="utf-8")
                ).replace('src="', f'src="{name}/')
            ),
        I(f'{config['blog']['written']} {date.strftime("%A, %-d %B %Y")}' if date else None),
        style="max-width: 80%; margin: auto auto 5rem auto;",
        )


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
        *[A(H4(post), href=f"/post/{post}", hx_boost="true") for post in posts],
        Div(
            Hr(),
            MailForm(),
            P(config['blog']['disclaimer']),
            style="position: fixed; bottom: 0; width: 85%",
        ),
    )

@rt("/post/{name:str}")
def get_post(name: str):
    post_dir = content_dir / f"{name}"
    md_files = sorted([f for f in post_dir.iterdir() if f.suffix == ".md"], reverse=True)
    
    if not md_files:
        return Response("File not found", status_code=404)
    
    updates = [Update(path, name) for path in md_files]


    return Titled(
        name,
        A(f"{config['blog']['back']} {config['blog']['title']}", href="/", hx_boost="true"),
        Hr(),
        *updates,
    )

@rt("/post/{name:str}/{file:str}")
def get_post_file(name: str, file: str):
    post_dir = content_dir / f"{name}"
    post_file = post_dir / f"{file}"
    
    if not post_file.exists():
        # Return a 404 response without raising an exception
        return Response("File not found", status_code=404)
    
    return FileResponse(post_file)


mailing_list_file = Path("mailing_list.txt")

@rt("/subscribe")
def post(email: str): # to list
    if not mailing_list_file.exists():
        mailing_list_file.touch()
    
    with mailing_list_file.open("r+") as file:
        emails = file.read().splitlines()
        if email not in emails:
            file.write(email + "\n")
            return config['blog']['email']['subscribe_success']
        else:
            return config['blog']['email']['already_subscribed']

@rt("/unsubscribe")
def delete(email: str): # from list
    if not mailing_list_file.exists():
        return config['blog']['email']['not_subscribed']
    
    with mailing_list_file.open("r+") as file:
        emails = file.read().splitlines()
        if email in emails:
            emails.remove(email)
            file.seek(0)
            file.truncate()
            file.write("\n".join(emails) + "\n")
            return config['blog']['email']['unsubscribe_success']
        else:
            return config['blog']['email']['not_subscribed']

serve()