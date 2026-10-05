from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required
from app.extensions import db
from app.models.note import Note, NoteVersion
from app.services.note_service import (
    compute_reading_stats,
    render_markdown_to_html,
    restore_note_version,
    save_note_version,
)
from app.services.auth_service import log_activity
from app.utils.decorators import api_or_login_required

notes_bp = Blueprint("notes", __name__)


@notes_bp.route("/notes")
@login_required
def view():
    return render_template("tools/notes.html")


@notes_bp.route("/api/v1/notes", methods=["GET"])
@api_or_login_required
def get_notes():
    user_id = current_user.id
    folder = request.args.get("folder")
    tag = request.args.get("tag")
    search = request.args.get("search")

    query = Note.query.filter_by(user_id=user_id)
    if folder and folder != "all":
        query = query.filter_by(folder=folder)
    if search:
        p = f"%{search.strip()}%"
        query = query.filter((Note.title.ilike(p)) | (Note.content.ilike(p)))

    notes = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc()).all()
    res = []
    for n in notes:
        d = n.to_dict()
        d["reading_stats"] = compute_reading_stats(n.content)
        res.append(d)
    return jsonify(res)


@notes_bp.route("/api/v1/notes", methods=["POST"])
@api_or_login_required
def create_note():
    user_id = current_user.id
    data = request.get_json(silent=True) or {}
    title = data.get("title", "Untitled Note").strip() or "Untitled Note"
    content = data.get("content", "")
    folder = data.get("folder", "General").strip() or "General"
    tags = data.get("tags", [])

    note = Note(user_id=user_id, title=title, content=content, folder=folder)
    note.tags = tags

    try:
        db.session.add(note)
        db.session.commit()
        save_note_version(note)
        log_activity(user_id, "created_note", "notes", f"Created note: {title}")
        return jsonify({"status": "success", "note": note.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@notes_bp.route("/api/v1/notes/<int:note_id>", methods=["GET"])
@api_or_login_required
def get_note(note_id):
    user_id = current_user.id
    note = Note.query.filter_by(id=note_id, user_id=user_id).first_or_404()
    d = note.to_dict()
    d["html_preview"] = render_markdown_to_html(note.content)
    d["reading_stats"] = compute_reading_stats(note.content)
    return jsonify(d)


@notes_bp.route("/api/v1/notes/<int:note_id>", methods=["PUT", "PATCH"])
@api_or_login_required
def update_note(note_id):
    user_id = current_user.id
    note = Note.query.filter_by(id=note_id, user_id=user_id).first_or_404()
    data = request.get_json(silent=True) or {}

    content_changed = False
    if "title" in data:
        note.title = data["title"].strip() or note.title
    if "content" in data and data["content"] != note.content:
        note.content = data["content"]
        content_changed = True
    if "folder" in data:
        note.folder = data["folder"].strip() or "General"
    if "tags" in data:
        note.tags = data["tags"]

    try:
        db.session.commit()
        if content_changed:
            save_note_version(note)
        return jsonify({"status": "success", "note": note.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@notes_bp.route("/api/v1/notes/<int:note_id>/pin", methods=["POST"])
@api_or_login_required
def toggle_pin(note_id):
    user_id = current_user.id
    note = Note.query.filter_by(id=note_id, user_id=user_id).first_or_404()
    note.is_pinned = not note.is_pinned
    db.session.commit()
    return jsonify({"status": "success", "is_pinned": note.is_pinned})


@notes_bp.route("/api/v1/notes/<int:note_id>", methods=["DELETE"])
@api_or_login_required
def delete_note(note_id):
    user_id = current_user.id
    note = Note.query.filter_by(id=note_id, user_id=user_id).first_or_404()
    db.session.delete(note)
    db.session.commit()
    return jsonify({"status": "success", "message": "Note deleted."})


@notes_bp.route("/api/v1/notes/<int:note_id>/versions", methods=["GET"])
@api_or_login_required
def get_versions(note_id):
    user_id = current_user.id
    note = Note.query.filter_by(id=note_id, user_id=user_id).first_or_404()
    versions = NoteVersion.query.filter_by(note_id=note.id).order_by(NoteVersion.created_at.desc()).all()
    return jsonify([v.to_dict() for v in versions])


@notes_bp.route("/api/v1/notes/<int:note_id>/versions/<int:version_id>/restore", methods=["POST"])
@api_or_login_required
def restore_version(note_id, version_id):
    user_id = current_user.id
    note = restore_note_version(note_id, version_id, user_id)
    if not note:
        return jsonify({"status": "error", "message": "Version not found."}), 404
    return jsonify({"status": "success", "note": note.to_dict()})
