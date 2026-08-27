from datetime import datetime, timezone
from app.extensions import db


class FileJob(db.Model):
    __tablename__ = "file_jobs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_type = db.Column(db.String(64), nullable=False)  # 'image_resize', 'image_compress', 'pdf_merge', 'pdf_split', etc.
    original_filename = db.Column(db.String(255), nullable=False)
    processed_filename = db.Column(db.String(255), nullable=True)
    original_size = db.Column(db.Integer, default=0, nullable=False)
    processed_size = db.Column(db.Integer, default=0, nullable=False)
    download_token = db.Column(db.String(64), nullable=True, unique=True, index=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "job_type": self.job_type,
            "original_filename": self.original_filename,
            "processed_filename": self.processed_filename,
            "original_size": self.original_size,
            "processed_size": self.processed_size,
            "download_token": self.download_token,
            "created_at": self.created_at.isoformat(),
        }
