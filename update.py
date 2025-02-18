from fasthtml.common import Div, Hr, NotStr, I
import markdown
from datetime import datetime
from babel.dates import format_date
from make_app import blogs_config

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
                extensions=["markdown.extensions.tables"],
                output_format="html"
            ).replace('<table>', '<table class="responsive-table">').replace('src="', f'src="{post_name}/')
            ),
        I(f'{blog_config["written"]} {format_date(date, locale=blog_config["locale"])}' if date else None),
        style="max-width: 80%; margin: auto auto 5rem auto;",
    )

def EmailUpdate(update_path, post_name, blog):
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
                extensions=["markdown.extensions.tables"],
                output_format="html"
        )),
        I(f'{blog_config["written"]} {format_date(date, locale=blog_config["locale"])}' if date else None),
    )