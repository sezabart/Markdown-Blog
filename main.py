from fasthtml.common import (
    # FastHTML's HTML tags
    A, AX, Button, Card, CheckboxX, Container, Div, Form, Grid, Group,P,I, H1, H2, H3, H4, H5, Hr, Hidden, Input, Img, Li, Ul, Ol, Main, Script, Style, Strong, Textarea, Title, Titled, Select, Option, Table, Tr, Th, Td,
    # FastHTML's specific symbols
    serve, NotStr,
    # From Starlette, Fastlite, fastcore, and the Python standard library:
    FileResponse, Response ,NotFoundError, RedirectResponse, patch, dataclass
)


import markdown
from pathlib import Path
from datetime import datetime
from babel.dates import format_date


from make_app import app, blogs_config, content_dir

rt = app.route


def Update(update_path, post_name, blog):
    blog_config = blogs_config[blog]
    if update_path.stem.isdigit() and len(update_path.stem) == 8:
        try:
            date = datetime.strptime(update_path.stem, "%Y%m%d")
        except ValueError:
            date = None
    else:
        date = None

    return Div(
        Hr(),
        NotStr(
            markdown.markdown(
                update_path.read_text(encoding="utf-8"),
                extensions=["markdown.extensions.tables"]
                ).replace('src="', f'src="{post_name}/')
            ),
        I(f'{blog_config["written"]} {format_date(date, locale=blog_config["locale"])}' if date else None),
        style="max-width: 80%; margin: auto auto 5rem auto;",
    )

@rt("/")
def home():
    return Titled(
        "SEZA",
        Div(
            Img(src="/static/headshot.jpg", alt="Bart's Headshot", style="border-radius: 50%; width: 300px; height: 300px;"),
            style="margin-bottom: 2rem;"
        ),
        H1("Bart Smits"),
        P("👋 I am a programmer with a passion for creating efficient and elegant code."),
        H2("About Skills, I have..."),
        Group(
            Card(Img(src="/static/django.png", alt="Django", style="width: 100px;"), footer=P("Expertise in Django, a high-level Python web framework."), style="max-width: 250px;"),
            Card(Img(src="/static/git.png", alt="Git", style="width: 100px;"), footer=P("Experience with Git, a distributed version control system."), style="max-width: 250px;"),
            Card(Img(src="/static/tensorflow.png", alt="TensorFlow", style="width: 100px;"), footer=P("Worked with TensorFlow, an open-source machine learning framework."), style="max-width: 250px;"),
            style="display: flex; justify-content: center; gap: 1rem; margin-bottom: 2rem;",
        ),
        Group(
            Card(Img(src="/static/htmx.png", alt="HTMX", style="width: 100px;"), footer=P("Expertise in HTMX, a library that allows you to access modern browser features directly from HTML."), style="max-width: 250px;"),
            Card(Img(src="/static/fastapi.png", alt="FastAPI", style="width: 100px;"), footer=P("Worked with FastAPI, a modern, fast (high-performance), web framework for building APIs with Python."), style="max-width: 250px;"),
            Card(Img(src="/static/sqlite.png", alt="SQLite", style="width: 100px;"), footer=P("Expertise in SQLite, a small, fast, self-contained, high-reliability, full-featured, SQL database engine."), style="max-width: 250px;"),
            style="display: flex; justify-content: center; gap: 1rem; margin-bottom: 2rem;",
        ),

        H2("About My Journey 🚀"),
        P(Strong("Education:  "), "Willem van Oranje College -> TU Delft (BSc Aerospace Engineering)"),
        P(Strong("In the Netherlands:  "), "Technical Assistance at Vidiled -> Independent Installer at FSN"),
        P(Strong("To Slovenia:  "), "Bartender at Hostel Pod Voglom -> Independent Programmer for Tehnosol"),
        P(Strong("Establishing:  "), "Set up S.P.: SEZA -> Freelance work for Luxonis"),
        P(Strong("Current:  "), "Working on a personal project -> Your next project?"),

        H2("Contact"),
        P("Feel free to reach out to via my ", A("📧 Email", href="mailto:bart@seza.si"), " and check out my ", A("🐙 GitHub", href="https://github.com/sezabart")),
        style="max-width: 80%; margin: auto auto 5rem auto; text-align: center;",
    )

@rt("/static/{filename:str}")
def get_static_file(filename: str):
    static_dir = Path("static")
    static_file = static_dir / f"{filename}"
    if not static_file.exists():
        return Response("File not found", status_code=404)
    return FileResponse(static_file)


@rt("/blogs/")
def list_blogs():
    return Titled(
        "Blogs",
        P("Select a blog to view its posts:"),
        *[A(H4(config['title']), href=f"/blogs/{blog}/", hx_boost="true") for blog, config in blogs_config.items()],
        style="max-width: 80%; margin: auto auto 5rem auto;",
    )

from mail import MailForm

@rt("/blogs/{blog:str}/")
def list_posts(blog:str):
    blog_config = blogs_config[blog]
    blog_dir = content_dir / f"{blog}"
    posts = sorted(
        [d.name for d in blog_dir.iterdir() if d.is_dir()],
        key=lambda d: d.split("-")[0],
        reverse=True
    )
    return Titled(
        blog_config['title'],
        #A(f"{blog_config['back']} Blogs", href="/blogs/" , hx_boost="true"),
        Hr(),
        P(blog_config['intro']),
        *[A(H4(post), href=f"/blogs/{blog}/post/{post}", hx_boost="true") for post in posts],
        Div(
            Hr(),
            MailForm(blog),
            P(blog_config['disclaimer']),
            style="position: fixed; bottom: 0; width: 85%",
        ),
    )

@rt("/blogs/{blog:str}/post/{post_name:str}")
def get_post(blog:str, post_name: str):
    blog_config = blogs_config[blog]
    post_dir = content_dir / f"{blog}" / f"{post_name}"
    md_files = sorted([f for f in post_dir.iterdir() if f.suffix == ".md"], reverse=False)
    
    if not md_files:
        return Response("File not found", status_code=404)
    
    updates = [Update(path, post_name, blog) for path in md_files]


    return Titled(
        post_name,
        A(f"{blog_config['back']} {blog_config['title']}", href=f"/blogs/{blog}/", hx_boost="true"),
        Hr(),
        *updates,
    )

@rt("/blogs/{blog:str}/post/{post_name:str}/{filename:str}")
def get_post_file(blog:str, post_name: str, filename: str):
    # Content_dir / Blog_dir / Post_dir / Filename
    # Post_dir is the title of the post, and is allowed to have spaces
    post_dir = content_dir / f"{blog}" / f"{post_name}"
    post_file = post_dir / f"{filename}"

    if not post_file.exists():
        # Return a 404 response without raising an exception
        return Response("File not found", status_code=404)
    
    return FileResponse(post_file)


if __name__ == "__main__":
    serve()