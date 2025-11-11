from fasthtml.common import (
    # FastHTML's HTML tags
    A, AX, Button, Card, CheckboxX, Container, Div, Form, Grid, Group,P,I, H1, H2, H3, H4, H5, Hr, Hidden, Input, Img, Li, Ul, Ol, Main, Script, Style, Strong, Textarea, Title, Titled, Select, Option, Table, Tr, Th, Td,
    # FastHTML's specific symbols
    serve, NotStr,
    # From Starlette, Fastlite, fastcore, and the Python standard library:
    FileResponse, Response ,NotFoundError, RedirectResponse, patch, dataclass
)

from pathlib import Path
from make_app import app, blogs_config, content_dir
from make_app import landing_config

rt = app.route


from update import Update

@rt("/")
def home():
    # Landing options come from make_app.landing_config (optional). We render a Select that
    # requests card groups from /landing/cards via HTMX. If no landing_config is provided,
    # show the original static cards.
    options = landing_config.get('options', []) if landing_config else []
    default_key = landing_config.get('default') if landing_config else None

    # Default cards (kept for fallback / no-landing-config)
    default_cards = Group(
        Card(Img(src="/static/django.png", alt="Django", style="width: 100px;"), footer=P("Expertise in Django"), style="max-width: 250px;"),
        Card(Img(src="/static/git.png", alt="Git", style="width: 100px;"), footer=P("Experience with Git"), style="max-width: 250px;"),
        Card(Img(src="/static/htmx.png", alt="HTMX", style="width: 100px;"), footer=P("HTMX skills"), style="max-width: 250px;"),
        style="display: flex; justify-content: center; gap: 1rem; margin-bottom: 2rem;",
    )

    return Titled(
        "SEZA",

        Div(
            Img(src="/static/headshot.jpg", alt="Bart's Headshot", style="border-radius: 50%; width: 300px; height: 300px;"),
            style="margin-bottom: 2rem;"
        ),

        H1("Bart Smits"),

        # Make the label text look like the select so they visually match
        Div(
            P("👋 I am", style="text-align: right; margin: 0; align-self: flex-start;"),  # align to top
            role_select(options=options, default_key=default_key),
            P("with the following skills:"),
            style="display: inline-flex; gap: 0.75rem; align-items: flex-start;"
        ),
        
        # Render initial cards: if landing options exist, render the default option's cards; otherwise render fallback default_cards.
        Div(
            landing_cards(default_key) if options else default_cards, id="landing-cards"
        ),

        A(H2("Read my Portfolio Blog 📝"), href="/blogs/portfolio/", hx_boost="true",
          style="display: block; text-align: center; margin-bottom: 3rem;"),

        # Journey section
        Div(
            H2("About My Journey 🚀"),
            P(Strong("Education:  "), "Willem van Oranje College -> TU Delft (BSc Aerospace Engineering)"),
            P(Strong("In the Netherlands:  "), "Technical Assistance at Vidiled -> Independent Installer at FSN"),
            P(Strong("To Slovenia:  "), "Bartender at Hostel Pod Voglom -> Independent Programmer for Tehnosol"),
            P(Strong("Establishing:  "), "Set up S.P.: SEZA -> Freelance work for Luxonis"),
            P(Strong("Current:  "), "Working on a personal project -> Your next project?"),

            H2("Contact"),
            P("Feel free to reach out to via my ", A("📧 Email", href="mailto:bart@seza.si"), " and check out my ", A("🐙 GitHub", href="https://github.com/sezabart")),
            
        ),
        style="max-width: 80%; margin: auto auto 5rem auto; text-align: center;",
    )

def role_select(options=None, default_key=None):
    return Div(
        Select(
            *[Option(opt.get('label'), value=opt.get('key'), selected=(opt.get('key') == default_key)) for opt in options],
            id="landing-select",
            name="role",
            hx_get="/landing/cards",
            hx_trigger="change",
            hx_target="#landing-cards",
            hx_swap="innerHTML",
            hx_include="#landing-select",
                    style=(
                        "appearance:none; -webkit-appearance:none; -moz-appearance:none;"
                        "background: transparent; border: none; border-bottom: 1px solid #374151;"
                        "padding: 0.3rem 0 2px 5px; font-size: 1rem; line-height: 1; cursor: pointer; outline: none;"
                        "vertical-align: middle;"
                    ),
        ) if options else P("developer"),
    ),

@rt("/landing/cards")
def landing_cards(role: str = None):
    # Return a Group of Cards filtered by landing_config. `role` corresponds to option 'key'.
    options = landing_config.get('options', []) if landing_config else []
    if not options:
        return Div("No landing configuration available.")

    # If role == 'all' or no role provided, show all cards
    show_all = (role == 'all' or role is None)

    # Find the chosen option only if not showing all
    chosen = None
    if not show_all and role:
        for opt in options:
            if opt.get('key') == role:
                chosen = opt
                break

    cards = []
    iter_options = options if show_all or chosen is None else [chosen]
    for opt in iter_options:
        for c in opt.get('cards', []):
            img = c.get('img') or '/static/headshot.jpg'
            cards.append(Card(Img(src=img, alt=c.get('title', ''), style="width: 100px;"), footer=P(c.get('desc', '')), style="max-width: 250px;"))

    return Group(*cards, style="display: flex; justify-content: center; gap: 1rem; margin-bottom: 2rem;")

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
            MailForm(blog) if blog_config.get('email') else None,
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