const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://18-mart-portal-4orl.vercel.app';

export interface BusSchedule {
    weekday: {
        url: string;
        label: string;
    } | null;
    weekend: {
        url: string;
        label: string;
    } | null;
    last_update: string;
    source: string;
}

export const busService = {
    async getSchedule(): Promise<BusSchedule> {
        const response = await fetch(`${API_BASE_URL}/bus/schedule`);
        if (!response.ok) throw new Error('Otobüs saatleri alınamadı');
        return response.json();
    }
};
