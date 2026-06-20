import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

_env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
    autoescape=select_autoescape(["html"]),
)


def render_html(summary: dict) -> str:
    return _env.get_template("report.html").render(**summary)
