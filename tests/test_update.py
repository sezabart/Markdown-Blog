import sys
import tempfile
from pathlib import Path
# ensure repo root is importable for tests
import pathlib as _pathlib
sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parents[1]))
from update import Update, EmailUpdate


def test_update_renders_markdown(tmp_path):
    md = tmp_path / "20250101.md"
    md.write_text("# Hello\n\nThis is *markdown*.")

    # Call Update which returns a FastHTML Div-like object; ensure it contains html string when converted
    result = Update(md, "Sample Post", "portfolio")
    # We expect that NotStr-wrapped HTML is present in the representation somewhere
    s = str(result)
    assert "<h1>" in s and "Hello" in s


def test_emailupdate_renders_markdown(tmp_path):
    md = tmp_path / "note.md"
    md.write_text("Simple text with **bold**")

    result = EmailUpdate(md, "Sample Post", "portfolio")
    s = str(result)
    assert "<strong>" in s or "<b>" in s or "bold" in s
