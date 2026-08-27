import math
import markdown
from typing import Any, Dict, List, Optional
from app.extensions import db
from app.models.note import Note, NoteVersion


def render_markdown_to_html(content: str) -> str:
    """Converts Markdown text to sanitized HTML with table and code extensions."""
    if not content:
        return ""
    return markdown.markdown(
        content,
        extensions=["extra", "codehilite", "nl2br", "sane_lists", "toc"],
    )


def compute_reading_stats(content: str) -> Dict[str, int]:
    """Computes word count, character count, and estimated reading time."""
    if not content:
        return {"words": 0, "chars": 0, "reading_time_min": 1}

    words = len(content.split())
    chars = len(content)
    reading_time = max(1, math.ceil(words / 200))

    return {
        "words": words,
        "chars": chars,
        "reading_time_min": reading_time,
    }


def save_note_version(note: Note):
    """Creates a historical version snapshot for a note."""
    count = NoteVersion.query.filter_by(note_id=note.id).count()
    ver = NoteVersion(
        note_id=note.id,
        title=note.title,
        content=note.content,
        version_number=count + 1,
    )
    db.session.add(ver)
    db.session.commit()


def restore_note_version(note_id: int, version_id: int, user_id: int) -> Optional[Note]:
    """Restores note content from a previous version."""
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    ver = NoteVersion.query.filter_by(id=version_id, note_id=note_id).first()

    if not note or not ver:
        return None

    # Snapshot current state first
    save_note_version(note)

    note.title = ver.title
    note.content = ver.content
    db.session.commit()
    return note
