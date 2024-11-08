from fasthtml.common import (
    FastHTML, Titled, Style, picolink
)


# This will be our 404 handler, which will return a simple error page.
def _not_found(req, exc): return Titled('404', 'Page Not Found')

# FastHTML includes the "HTMX" and "Surreal" libraries in headers, unless you pass `default_hdrs=False`.
app = FastHTML(exception_handlers={404: _not_found},
               # PicoCSS is a tiny CSS framework that we'll use for this project.
               # `picolink` is pre-defined with the header for the PicoCSS stylesheet.
               hdrs=(picolink,
                     Style(':root { --pico-font-size: 100%}'),
                    Style(open("styles.css").read())
                )
      )


from pathlib import Path
import yaml

# Load configuration from a YAML file
config_path = Path("config.yaml")

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

# Directory containing the markdown files
content_dir = Path(config['content_dir'])
blogs_config = config['blogs']