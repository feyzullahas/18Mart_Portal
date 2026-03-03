const API_BASE_URL = 'https://18-mart-portal.vercel.app';

export interface CalendarEvent {
    start: string; // YYYY-MM-DD
    end: string;
    title: string;
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
    }
};
