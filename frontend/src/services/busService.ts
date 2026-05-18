const PROD_API_BASE_URL = 'https://18-mart-portal-4orl.vercel.app';
const BUS_CACHE_KEY = 'bus_schedule_cache_v3';

const resolveApiBaseUrl = () => {
    const envApiUrl = import.meta.env.VITE_API_URL;
    if (envApiUrl) {
        return envApiUrl.replace(/\/$/, '');
    }

    if (import.meta.env.DEV) {
        return 'http://localhost:8000';
    }

    return PROD_API_BASE_URL;
};

const getMidnightTimestamp = () => {
    const midnight = new Date();
    midnight.setHours(24, 0, 0, 0);
    return midnight.getTime();
};

export const API_BASE_URL = resolveApiBaseUrl();

export interface BusSchedule {
    pdfs: Array<{
        url: string;
        label: string;
    }>;
    last_update: string;
    source: string;
}

type LegacyBusSchedule = {
    weekday?: { url: string; label: string } | null;
    weekend?: { url: string; label: string } | null;
    special?: { url: string; label: string } | null;
    last_update?: string;
    source?: string;
};

type CachedPayload<T> = {
    data: T;
    expiresAt: number;
};

const getCachedData = <T,>(key: string): T | null => {
    try {
        const raw = localStorage.getItem(key);
        if (!raw) return null;
        const parsed = JSON.parse(raw) as CachedPayload<T>;
        if (!parsed?.expiresAt || Date.now() > parsed.expiresAt) {
            localStorage.removeItem(key);
            return null;
        }
        return parsed.data;
    } catch {
        return null;
    }
};

const setCachedData = <T,>(key: string, data: T) => {
    const payload: CachedPayload<T> = {
        data,
        expiresAt: getMidnightTimestamp()
    };
    localStorage.setItem(key, JSON.stringify(payload));
};

const normalizeSchedule = (raw: BusSchedule | LegacyBusSchedule | null): BusSchedule | null => {
    if (!raw) return null;
    const anyRaw = raw as BusSchedule & LegacyBusSchedule;
    if (Array.isArray(anyRaw.pdfs)) {
        return {
            pdfs: anyRaw.pdfs,
            last_update: anyRaw.last_update ?? new Date().toISOString(),
            source: anyRaw.source ?? ''
        };
    }

    const pdfs = [anyRaw.special, anyRaw.weekend, anyRaw.weekday]
        .filter(Boolean)
        .map(entry => ({
            url: entry!.url,
            label: entry!.label
        }));

    return {
        pdfs,
        last_update: anyRaw.last_update ?? new Date().toISOString(),
        source: anyRaw.source ?? ''
    };
};

export const busService = {
    getCachedSchedule(): BusSchedule | null {
        const cached = getCachedData<BusSchedule | LegacyBusSchedule>(BUS_CACHE_KEY);
        const normalized = normalizeSchedule(cached);
        if (normalized && cached !== normalized) {
            setCachedData(BUS_CACHE_KEY, normalized);
        }
        return normalized;
    },

    async getSchedule(): Promise<BusSchedule> {
        const response = await fetch(`${API_BASE_URL}/bus/schedule`);
        if (!response.ok) throw new Error('Otobüs saatleri alınamadı');
        const data = await response.json();
        const normalized = normalizeSchedule(data) ?? {
            pdfs: [],
            last_update: new Date().toISOString(),
            source: ''
        };
        setCachedData(BUS_CACHE_KEY, normalized);
        return normalized;
    },

    async prefetchDailySchedule(): Promise<void> {
        const cached = this.getCachedSchedule();
        if (cached) return;
        try {
            await this.getSchedule();
        } catch {
            // Prefetch hataları kullanıcı akışını engellememeli.
        }
    }
};
