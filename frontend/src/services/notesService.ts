const API_BASE_URL = import.meta.env.VITE_API_URL
    ? (import.meta.env.VITE_API_URL as string).replace(/\/$/, '')
    : import.meta.env.DEV
    ? 'http://localhost:8000'
    : 'https://18-mart-portal-4orl.vercel.app';

export interface HomeNote {
    id: number;
    title: string;
    position: number;
    is_pinned: boolean;
}

const getAuthHeaders = (): Record<string, string> => {
    const token = localStorage.getItem('token');
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers.Authorization = `Bearer ${token}`;
    return headers;
};

export const notesService = {
    async getNotes(): Promise<HomeNote[]> {
        const res = await fetch(`${API_BASE_URL}/notes/`, { headers: getAuthHeaders() });
        if (!res.ok) throw new Error('Notlar alınamadı');
        return res.json();
    },

    async createNote(title: string): Promise<HomeNote> {
        const res = await fetch(`${API_BASE_URL}/notes/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ title }),
        });
        if (!res.ok) throw new Error('Not eklenemedi');
        return res.json();
    },

    async togglePin(id: number): Promise<HomeNote> {
        const res = await fetch(`${API_BASE_URL}/notes/${id}/toggle-pin`, {
            method: 'POST',
            headers: getAuthHeaders(),
        });
        if (!res.ok) throw new Error('Sabitleme değiştirilemedi');
        return res.json();
    },

    async deleteNote(id: number): Promise<void> {
        const res = await fetch(`${API_BASE_URL}/notes/${id}`, {
            method: 'DELETE',
            headers: getAuthHeaders(),
        });
        if (!res.ok) throw new Error('Not silinemedi');
    },

    async reorderNotes(orderedIds: number[]): Promise<void> {
        const res = await fetch(`${API_BASE_URL}/notes/reorder`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ ordered_ids: orderedIds }),
        });
        if (!res.ok) throw new Error('Sıralama güncellenemedi');
    },
};
