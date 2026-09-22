import { useState, useEffect, useCallback, useRef } from 'react';
import { FiTrash2 } from 'react-icons/fi';
import { AiOutlinePushpin, AiFillPushpin } from 'react-icons/ai';
import {
    DndContext,
    PointerSensor,
    TouchSensor,
    closestCenter,
    useSensor,
    useSensors,
    type DragEndEvent,
} from '@dnd-kit/core';
import {
    SortableContext,
    arrayMove,
    useSortable,
    verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { notesService, type HomeNote } from '../services/notesService';
import { useAuth } from '../context/AuthContext';
import '../styles/HomeNotes.css';

// ─── Sürüklenebilir Not Öğesi ────────────────────────────────────────────────
const SortableNoteItem = ({
    note,
    deletingId,
    pinningId,
    onDelete,
    onTogglePin,
}: {
    note: HomeNote;
    deletingId: number | null;
    pinningId: number | null;
    onDelete: (id: number) => void;
    onTogglePin: (id: number) => void;
}) => {
    const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: note.id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            className={`home-note-item${isDragging ? ' dragging' : ''}${note.is_pinned ? ' pinned' : ''}${note.id < 0 ? ' optimistic' : ''}`}
        >
            <button
                type="button"
                className="home-note-drag-handle"
                aria-label="Notu taşımak için basılı tut ve sürükle"
                {...attributes}
                {...listeners}
            >
                ⋮⋮
            </button>
            <span className="home-note-title">{note.title}</span>
            <div className="home-note-actions">
                <button
                    type="button"
                    className={`home-note-pin${note.is_pinned ? ' active' : ''}`}
                    onClick={() => onTogglePin(note.id)}
                    disabled={pinningId === note.id || note.id < 0}
                    aria-label={note.is_pinned ? 'Sabitlemeyi kaldır' : 'Sabitle'}
                    title={note.is_pinned ? 'Sabitlemeyi kaldır' : 'Sabitle'}
                >
                    {note.is_pinned ? <AiFillPushpin /> : <AiOutlinePushpin />}
                </button>
                <button
                    type="button"
                    className="home-note-delete"
                    onClick={() => onDelete(note.id)}
                    disabled={deletingId === note.id || note.id < 0}
                    aria-label="Notu sil"
                >
                    <FiTrash2 />
                </button>
            </div>
        </div>
    );
};
// ─────────────────────────────────────────────────────────────────────────────

export const HomeNotes = ({ onOpenLogin }: { onOpenLogin?: () => void }) => {
    const { user } = useAuth();
    const [notes, setNotes] = useState<HomeNote[]>([]);
    const [loading, setLoading] = useState(false);
    const [inputValue, setInputValue] = useState('');
    const [saving, setSaving] = useState(false);
    const [deletingId, setDeletingId] = useState<number | null>(null);
    const [pinningId, setPinningId] = useState<number | null>(null);
    const [error, setError] = useState('');
    const inputRef = useRef<HTMLInputElement>(null);
    // Geçici ID sayacı (optimistic update için negatif)
    const tempIdRef = useRef(-1);

    const fetchNotes = useCallback(async () => {
        if (!user) return;
        // Önbellekte veri varsa loading gösterme, arka planda güncelle
        const cached = notesService.getCachedNotes();
        if (cached.length > 0) {
            setNotes(cached);
            setLoading(false);
        } else {
            setLoading(true);
        }
        try {
            const data = await notesService.getNotes();
            setNotes(data);
        } catch {
            if (cached.length === 0) setError('Notlar yüklenemedi.');
        } finally {
            setLoading(false);
        }
    }, [user]);

    useEffect(() => {
        // Kullanıcı değişince önbelleği temizle
        if (!user) {
            notesService.clearCache();
            setNotes([]);
        }
        void fetchNotes();
    }, [fetchNotes, user]);


    // ── Not Ekle (Optimistic) ─────────────────────────────────────────────────
    const handleAdd = async () => {
        const title = inputValue.trim();
        if (!title || saving) return;

        // 1) UI'ı anında güncelle (geçici negatif ID ile)
        const tempId = tempIdRef.current--;
        const tempNote: HomeNote = {
            id: tempId,
            title,
            position: 0,
            is_pinned: false,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
        };
        setNotes(prev => {
            const pinned = prev.filter(n => n.is_pinned);
            const unpinned = prev.filter(n => !n.is_pinned);
            return [...pinned, tempNote, ...unpinned];
        });
        setInputValue('');
        setSaving(true);
        setError('');

        // 2) Arka planda API çağrısı
        try {
            const realNote = await notesService.createNote(title);
            // Geçici notu gerçek nota değiştir
            setNotes(prev => prev.map(n => (n.id === tempId ? realNote : n)));
        } catch {
            // Hata varsa geçici notu kaldır
            setNotes(prev => prev.filter(n => n.id !== tempId));
            setError('Not eklenemedi.');
        } finally {
            setSaving(false);
        }
    };

    // ── Sabitle/Kaldır (Optimistic) ───────────────────────────────────────────
    const handleTogglePin = async (id: number) => {
        if (id < 0) return; // Henüz kaydedilmemiş not
        setPinningId(id);
        setError('');

        // 1) UI'ı anında güncelle
        const snapshot = [...notes];
        setNotes(prev => {
            const toggled = prev.map(n =>
                n.id === id ? { ...n, is_pinned: !n.is_pinned } : n
            );
            // Sıralamayı güncelle: sabitlenmiş üste
            const pinned = toggled.filter(n => n.is_pinned);
            const unpinned = toggled.filter(n => !n.is_pinned);
            return [...pinned, ...unpinned];
        });

        // 2) Arka planda API
        try {
            await notesService.togglePin(id);
        } catch {
            // Hata varsa orijinal listeye dön
            setNotes(snapshot);
            setError('Sabitleme değiştirilemedi.');
        } finally {
            setPinningId(null);
        }
    };

    // ── Sil (Optimistic) ─────────────────────────────────────────────────────
    const handleDelete = async (id: number) => {
        if (id < 0) return;
        setDeletingId(id);
        setError('');

        // 1) UI'ı anında güncelle
        const snapshot = [...notes];
        setNotes(prev => prev.filter(n => n.id !== id));

        // 2) Arka planda API
        try {
            await notesService.deleteNote(id);
        } catch {
            // Hata varsa geri al
            setNotes(snapshot);
            setError('Not silinemedi.');
        } finally {
            setDeletingId(null);
        }
    };

    const sensors = useSensors(
        useSensor(PointerSensor, { activationConstraint: { distance: 6 } }),
        useSensor(TouchSensor, { activationConstraint: { delay: 220, tolerance: 8 } }),
    );

    const handleDragEnd = async (event: DragEndEvent) => {
        if (!event.over || event.active.id === event.over.id) return;

        const oldIndex = notes.findIndex(n => n.id === event.active.id);
        const newIndex = notes.findIndex(n => n.id === event.over!.id);
        if (oldIndex === -1 || newIndex === -1) return;

        const reordered = arrayMove(notes, oldIndex, newIndex);
        setNotes(reordered);

        try {
            await notesService.reorderNotes(reordered.map(n => n.id));
        } catch {
            // sessiz geç
        }
    };

    return (
        <section className="home-notes-section">
            <h3>Notlar</h3>

            {!user ? (
                <div className="home-notes-locked">
                    <p>Not eklemek için giriş yapın.</p>
                    {onOpenLogin && (
                        <button
                            type="button"
                            className="portal-auth-btn portal-lock-action"
                            onClick={onOpenLogin}
                        >
                            Giriş Yap
                        </button>
                    )}
                </div>
            ) : (
                <>
                    {/* Not Ekleme Formu */}
                    <form
                        className="home-notes-form"
                        onSubmit={e => { e.preventDefault(); void handleAdd(); }}
                    >
                        <input
                            ref={inputRef}
                            type="text"
                            className="home-notes-input"
                            placeholder="Yeni not ekle..."
                            value={inputValue}
                            onChange={e => setInputValue(e.target.value)}
                            maxLength={255}
                            onFocus={() => {
                                setTimeout(() => {
                                    inputRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                }, 350);
                            }}
                        />
                        <button
                            type="submit"
                            className="home-notes-add-btn"
                            disabled={!inputValue.trim() || saving}
                        >
                            +
                        </button>
                    </form>

                    {error && <p className="home-notes-error">{error}</p>}

                    {/* Not Listesi */}
                    {loading ? (
                        <div className="home-notes-loading">
                            <div className="loading-spinner" />
                        </div>
                    ) : notes.length === 0 ? (
                        <p className="home-notes-empty">Henüz not yok.</p>
                    ) : (
                        <DndContext
                            sensors={sensors}
                            collisionDetection={closestCenter}
                            onDragEnd={event => void handleDragEnd(event)}
                        >
                            <SortableContext
                                items={notes.map(n => n.id)}
                                strategy={verticalListSortingStrategy}
                            >
                                <div className="home-notes-list">
                                    {notes.map(note => (
                                        <SortableNoteItem
                                            key={note.id}
                                            note={note}
                                            deletingId={deletingId}
                                            pinningId={pinningId}
                                            onDelete={id => void handleDelete(id)}
                                            onTogglePin={id => void handleTogglePin(id)}
                                        />
                                    ))}
                                </div>
                            </SortableContext>
                        </DndContext>
                    )}
                </>
            )}
        </section>
    );
};
