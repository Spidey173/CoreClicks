import json
from datetime import datetime, timezone
from app.extensions import db


class ColorPalette(db.Model):
    __tablename__ = "color_palettes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(128), default="Custom Palette", nullable=False)
    harmony_type = db.Column(db.String(32), default="Complementary", nullable=False)
    colors_json = db.Column(db.Text, nullable=False)  # JSON list of HEX colors
    is_favorite = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    @property
    def colors(self):
        try:
            return json.loads(self.colors_json)
        except Exception:
            return []

    @colors.setter
    def colors(self, value):
        self.colors_json = json.dumps(value if isinstance(value, list) else [])

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "harmony_type": self.harmony_type,
            "colors": self.colors,
            "is_favorite": self.is_favorite,
            "created_at": self.created_at.isoformat(),
        }
