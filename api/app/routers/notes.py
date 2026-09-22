from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.home_note import HomeNote
from app.models.user import User
from app.routers.auth_new import get_current_user

router = APIRouter(prefix="/notes", tags=["notes"])


class NoteCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class NoteUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class NoteReorderRequest(BaseModel):
    ordered_ids: List[int]


def _note_to_dict(n: HomeNote) -> dict:
    return {
        "id": n.id,
        "title": n.title,
        "position": n.position,
        "is_pinned": n.is_pinned,
    }


@router.get("/")
def get_notes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Giriş yapan kullanıcının notlarını döndürür (sabitliler önce)."""
    notes = (
        db.query(HomeNote)
        .filter(HomeNote.user_id == current_user.id)
        .order_by(HomeNote.is_pinned.desc(), HomeNote.position.asc(), HomeNote.id.asc())
        .all()
    )
    return [_note_to_dict(n) for n in notes]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_note(
    payload: NoteCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Yeni not ekler (en üste)."""
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Not başlığı boş olamaz.")

    # Yeni notun en üste çıkması için diğer notları aşağı kaydır
    db.query(HomeNote).filter(HomeNote.user_id == current_user.id).update(
        {"position": HomeNote.position + 1}
    )

    note = HomeNote(
        user_id=current_user.id,
        title=title,
        position=0,
        is_pinned=False,
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    return _note_to_dict(note)


@router.put("/{note_id}")
def update_note(
    note_id: int,
    payload: NoteUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Notu günceller."""
    note = (
        db.query(HomeNote)
        .filter(HomeNote.id == note_id, HomeNote.user_id == current_user.id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Not bulunamadı.")

    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Not başlığı boş olamaz.")

    note.title = title
    db.commit()
    return {"message": "Not güncellendi."}


@router.post("/{note_id}/toggle-pin")
def toggle_pin(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Notun sabitleme durumunu değiştirir."""
    note = (
        db.query(HomeNote)
        .filter(HomeNote.id == note_id, HomeNote.user_id == current_user.id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Not bulunamadı.")

    note.is_pinned = not note.is_pinned
    db.commit()
    return _note_to_dict(note)


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Notu siler."""
    note = (
        db.query(HomeNote)
        .filter(HomeNote.id == note_id, HomeNote.user_id == current_user.id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Not bulunamadı.")

    db.delete(note)
    db.commit()
    return {"message": "Not silindi."}


@router.post("/reorder")
def reorder_notes(
    payload: NoteReorderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Notların sırasını günceller."""
    notes = (
        db.query(HomeNote)
        .filter(HomeNote.user_id == current_user.id)
        .all()
    )
    note_map = {n.id: n for n in notes}

    for idx, note_id in enumerate(payload.ordered_ids):
        if note_id in note_map:
            note_map[note_id].position = idx

    db.commit()
    return {"message": "Sıralama güncellendi."}
