import json
from datetime import datetime, timezone
from app.extensions import db


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(255), default="Untitled Note", nullable=False)
    content = db.Column(db.Text, default="", nullable=False)
    folder = db.Column(db.String(64), default="General", nullable=False, index=True)
    tags_json = db.Column(db.Text, default="[]", nullable=False)
    is_pinned = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    versions = db.relationship("NoteVersion", backref="note", lazy=True, cascade="all, delete-orphan")

    @property
    def tags(self):
        try:
            return json.loads(self.tags_json)
        except Exception:
            return []

    @tags.setter
    def tags(self, value):
        self.tags_json = json.dumps(value if isinstance(value, list) else [])

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "folder": self.folder,
            "tags": self.tags,
            "is_pinned": self.is_pinned,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class NoteVersion(db.Model):
    __tablename__ = "note_versions"

    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    version_number = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "version_number": self.version_number,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
        }
