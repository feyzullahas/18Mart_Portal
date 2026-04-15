const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://18-mart-portal-4orl.vercel.app';

export interface CalendarEvent {
    id?: number;
    start: string; // YYYY-MM-DD
    end: string;
    title: string;
    description?: string;
    type: string;
    start_formatted: string;
    end_formatted: string;
    days_left: number;
    is_past: boolean;
    is_active: boolean;
}

export interface CalendarInfo {
    id: string;
    name: string;
    events: CalendarEvent[];
}

export interface CalendarType {
    id: string;
    name: string;
    category?: string;
    has_sub?: boolean;
}

export interface CalendarListResponse {
    calendars: CalendarType[];
    sub_calendars: { [key: string]: CalendarType[] };
}

interface CreateMyCalendarEventPayload {
    date: string;
    title: string;
    description?: string;
}

const getAuthHeaders = (): Record<string, string> => {
    const token = localStorage.getItem('token');

    const headers: Record<string, string> = {
        'Content-Type': 'application/json'
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    return headers;
};

export const calendarService = {
    async getTypes(): Promise<CalendarListResponse> {
        const response = await fetch(`${API_BASE_URL}/calendar/list`);
        if (!response.ok) throw new Error('Takvim listesi alınamadı');
        return response.json();
    },

    async getEvents(calendarId: string = 'general'): Promise<CalendarInfo> {
        const response = await fetch(`${API_BASE_URL}/calendar/?id=${calendarId}`);
        if (!response.ok) throw new Error('Takvim verileri alınamadı');
        return response.json();
    },

    async getMyEvents(): Promise<CalendarInfo> {
        const response = await fetch(`${API_BASE_URL}/calendar/my`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Benim takvimim verileri alınamadı');
        return response.json();
    },

    async createMyEvent(payload: CreateMyCalendarEventPayload): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/calendar/my`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({ detail: 'Görev kaydedilemedi' }));
            throw new Error(err.detail || 'Görev kaydedilemedi');
        }
    }
};
