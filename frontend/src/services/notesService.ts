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
    created_at?: string;
    updated_at?: string;
}

// ── localStorage önbelleği ────────────────────────────────────────────────────
const CACHE_KEY = 'home_notes_cache';

const readCache = (): HomeNote[] => {
    try {
        const raw = localStorage.getItem(CACHE_KEY);
        return raw ? (JSON.parse(raw) as HomeNote[]) : [];
    } catch {
        return [];
    }
};

const writeCache = (notes: HomeNote[]) => {
    try {
        // Sadece gerçek (pozitif ID'li) notları önbellekle
        localStorage.setItem(CACHE_KEY, JSON.stringify(notes.filter(n => n.id > 0)));
    } catch {
        // Depolama dolu olabilir; sessizce geç
    }
};

const getAuthHeaders = (): Record<string, string> => {
    const token = localStorage.getItem('token');
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers.Authorization = `Bearer ${token}`;
    return headers;
};

export const notesService = {
    /** Önce önbellekten döner; arka planda taze veriyi getirir. */
    getCachedNotes(): HomeNote[] {
        return readCache();
    },

    async getNotes(): Promise<HomeNote[]> {
        const res = await fetch(`${API_BASE_URL}/notes/`, { headers: getAuthHeaders() });
        if (!res.ok) throw new Error('Notlar alınamadı');
        const data = (await res.json()) as HomeNote[];
        writeCache(data);
        return data;
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

    clearCache() {
        localStorage.removeItem(CACHE_KEY);
    },
};
