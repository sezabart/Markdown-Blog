from fasthtml.common import (
    # FastHTML's HTML tags
    A, AX, Button, Card, CheckboxX, Container, Div, Form, Grid, Group,P,I, H1, H2, H3, H4, H5, Hr, Hidden, Input, Img, Li, Ul, Ol, Main, Script, Style, Textarea, Title, Titled, Select, Option, Table, Tr, Th, Td,
    # FastHTML's specific symbols
    Beforeware, FastHTML, fill_form, picolink, serve, NotStr,
    # From Starlette, Fastlite, fastcore, and the Python standard library:
    FileResponse, Response ,NotFoundError, RedirectResponse, patch, dataclass
)


import markdown
from pathlib import Path
from datetime import datetime
import yaml
from babel.dates import format_date

# Load configuration from a YAML file
config_path = Path("config.yaml")

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

# Directory containing the markdown files
content_dir = Path(config['content_dir'])
blogs_config = config['blogs']



# This will be our 404 handler, which will return a simple error page.
def _not_found(req, exc): return Titled('404', 'Page Not Found')

# FastHTML includes the "HTMX" and "Surreal" libraries in headers, unless you pass `default_hdrs=False`.
app = FastHTML(exception_handlers={404: _not_found},
               # PicoCSS is a tiny CSS framework that we'll use for this project.
               # `picolink` is pre-defined with the header for the PicoCSS stylesheet.
               hdrs=(picolink,
                     Style(':root { --pico-font-size: 100%}'),
                )
      )

rt = app.route

def MailForm(blog):
    blog_config = blogs_config[blog]
    return Group(
                Input(placeholder="Email", type="email", id="email", style="width: 40%"),
                Button(blog_config['email']['subscribe'], hx_post=f"/{blog}/subscribe", hx_swap="outerHTML", hx_include="#email"),
                Button(blog_config['email']['unsubscribe'], hx_delete=f"/{blog}/unsubscribe", hx_swap="outerHTML", hx_include="#email", cls="outline"),
                style="width: 100%",
            ),



def Update(update_path, post_name, blog):
    print(f"{post_name=}")
    blog_config = blogs_config[blog]
    if update_path.stem.isdigit() and len(update_path.stem) == 8:
        try:
            date = datetime.strptime(update_path.stem, "%Y%m%d")
        except ValueError:
            date = None
    else:
        date = None

    slugged_post_name = post_name.replace(" ", "-")
    return Div(
        Hr(),
        NotStr(
            markdown.markdown(
                update_path.read_text(encoding="utf-8")
                ).replace('src="', f'src="{slugged_post_name}/file/')
            ),
        I(f'{blog_config["written"]} {format_date(date, locale=blog_config['locale'])}' if date else None),
        style="max-width: 80%; margin: auto auto 5rem auto;",
    )

@rt("/")
def home():
    return Titled(
        "Bart's Portfolio",
        Div(
            Img(src="/static/headshot.jpg", alt="Bart's Headshot", style="border-radius: 50%; width: 150px; height: 150px;"),
            style="text-align: center; margin-bottom: 2rem;"
        ),
        P("👋 Welcome to my portfolio! I am a programmer with a passion for creating efficient and elegant code."),
        H2("About Me"),
        P("I have experience in Python, JavaScript, and various other programming languages and frameworks. I enjoy solving complex problems and learning new technologies."),
        H2("Contact"),
        P("Feel free to reach out to me:"),
        Ul(
            Li(A("📧 Email", href="mailto:bart@seza.si")),
            Li(A("🐙 GitHub", href="https://github.com/sezabart")),
        ),
        style="max-width: 80%; margin: auto auto 5rem auto;",
    )


@rt("/blogs/")
def list_blogs():
    return Titled(
        "Blogs",
        P("Select a blog to view its posts:"),
        *[A(H4(config['title']), href=f"/blogs/{blog}/", hx_boost="true") for blog, config in blogs_config.items()],
        style="max-width: 80%; margin: auto auto 5rem auto;",
    )

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
        A(f"{blog_config['back']} Blogs", href="/blogs/", hx_boost="true"),
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

@rt("/blogs/{blog:str}/post/{name:str}")
def get_post(blog:str, name: str):
    print(f"get_post {blog=}, {name=}")
    blog_config = blogs_config[blog]
    post_dir = content_dir / f"{blog}" / f"{name}"
    md_files = sorted([f for f in post_dir.iterdir() if f.suffix == ".md"], reverse=True)
    
    if not md_files:
        return Response("File not found", status_code=404)
    
    updates = [Update(path, name, blog) for path in md_files]


    return Titled(
        name,
        A(f"{blog_config['back']} {blog_config['title']}", href=f"/blogs/{blog}/", hx_boost="true"),
        Hr(),
        *updates,
    )

@rt("/blogs/{blog:str}/post/{name:str}/file/{filename:str}")
def get_post_file(blog:str, name: str, file: str):
    print(f"get_post_file {blog=}, {name=} {file=}")
    post_dir = content_dir / f"{name}"
    filename = filename.replace("-", " ")
    post_file = post_dir / f"{filename}"
    print(f"{post_file=}")
    if not post_file.exists():
        # Return a 404 response without raising an exception
        return Response("File not found", status_code=404)
    
    return FileResponse(post_file)




@rt("/blogs/{blog:str}/subscribe")
def post(blog:str, email: str): # to list
    blog_config = blogs_config[blog]
    mailing_list_file = Path(f"mailing_lists/{blog}.txt")
    if not mailing_list_file.exists():
        mailing_list_file.touch()
    
    with mailing_list_file.open("r+") as file:
        emails = file.read().splitlines()
        if email not in emails:
            file.write(email + "\n")
            return Button(blog_config['email']['subscribe_success'], disabled=True)
        else:
            return Button(blog_config['email']['already_subscribed'], disabled=True)

@rt("/blogs/{blog:str}/unsubscribe")
def delete(blog:str, email: str): # from list
    blog_config = blogs_config[blog]
    mailing_list_file = Path(f"mailing_lists/{blog}.txt")
    if not mailing_list_file.exists():
        return blog_config['email']['not_subscribed']
    
    with mailing_list_file.open("r+") as file:
        emails = file.read().splitlines()
        if email in emails:
            emails.remove(email)
            file.seek(0)
            file.truncate()
            file.write("\n".join(emails) + "\n")
            return Button(blog_config['email']['unsubscribe_success'], disabled=True, cls="outline")
        else:
            return Button(blog_config['email']['not_subscribed'], disabled=True, cls="outline")

serve()