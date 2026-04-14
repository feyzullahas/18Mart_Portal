const PROD_API_BASE_URL = 'https://18-mart-portal-4orl.vercel.app';
const WEATHER_CURRENT_CACHE_KEY = 'weather_current_cache_v1';
const WEATHER_FORECAST_CACHE_KEY = 'weather_forecast_cache_v1_7';

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

const API_BASE_URL = resolveApiBaseUrl();

type CachedPayload<T> = {
    data: T;
    expiresAt: number;
};

const getMidnightTimestamp = () => {
    const midnight = new Date();
    midnight.setHours(24, 0, 0, 0);
    return midnight.getTime();
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

export interface CurrentWeather {
    current: {
        time: string;
        temperature_2m: number;
        apparent_temperature: number;
        relative_humidity_2m: number;
        weathercode: number;
        wind_speed_10m: number;
        precipitation: number;
    };
}

export interface Forecast {
    hourly: {
        time: string[];
        temperature_2m: number[];
        weathercode: number[];
        precipitation_probability: number[];
        apparent_temperature: number[];
    };
    daily: {
        time: string[];
        temperature_2m_max: number[];
        temperature_2m_min: number[];
        apparent_temperature_max: number[];
        apparent_temperature_min: number[];
        weathercode: number[];
        precipitation_probability_max: number[];
    };
}

export const weatherService = {
    getCachedCurrentWeather(): CurrentWeather | null {
        return getCachedData<CurrentWeather>(WEATHER_CURRENT_CACHE_KEY);
    },

    getCachedForecast(days: number = 7): Forecast | null {
        if (days !== 7) return null;
        return getCachedData<Forecast>(WEATHER_FORECAST_CACHE_KEY);
    },

    async getCurrentWeather(): Promise<CurrentWeather> {
        const response = await fetch(`${API_BASE_URL}/weather/current`);
        if (!response.ok) throw new Error('Hava durumu alınamadı');
        const data = await response.json();
        setCachedData(WEATHER_CURRENT_CACHE_KEY, data);
        return data;
    },

    async getForecast(days: number = 7): Promise<Forecast> {
        const response = await fetch(`${API_BASE_URL}/weather/forecast?days=${days}`);
        if (!response.ok) throw new Error('Tahmin alınamadı');
        const data = await response.json();
        if (days === 7) {
            setCachedData(WEATHER_FORECAST_CACHE_KEY, data);
        }
        return data;
    },

    async prefetchDailyWeather(): Promise<void> {
        const cachedCurrent = this.getCachedCurrentWeather();
        const cachedForecast = this.getCachedForecast(7);
        if (cachedCurrent && cachedForecast) return;

        try {
            await Promise.all([
                cachedCurrent ? Promise.resolve(cachedCurrent) : this.getCurrentWeather(),
                cachedForecast ? Promise.resolve(cachedForecast) : this.getForecast(7)
            ]);
        } catch {
            // Prefetch hataları kullanıcı akışını engellememeli.
        }
    }
};

// WMO hava kodu → emoji (gece saatleri için ay/yıldız varyantları)
export const getWeatherEmoji = (code: number, hour?: number): string => {
    const isNight = hour !== undefined && (hour >= 21 || hour < 6);
    if (code === 0) return isNight ? '🌙' : '☀️';
    if (code === 1) return isNight ? '🌘' : '🌤️';
    if (code === 2) return '⛅';
    if (code === 3) return '☁️';
    if (code <= 48) return '🌫️';
    if (code <= 55) return '🌦️';
    if (code <= 67) return '🌧️';
    if (code <= 77) return '🌨️';
    if (code <= 82) return '🌦️';
    if (code <= 86) return '🌨️';
    return '⛈️';
};

// WMO hava kodu → Türkçe açıklama
export const getWeatherDescription = (code: number): string => {
    if (code === 0) return 'Açık';
    if (code === 1) return 'Az Bulutlu';
    if (code === 2) return 'Parçalı Bulutlu';
    if (code === 3) return 'Kapalı';
    if (code <= 48) return 'Sisli';
    if (code <= 55) return 'Çiseleme';
    if (code <= 65) return 'Yağmurlu';
    if (code <= 67) return 'Dondurucu Yağmur';
    if (code <= 75) return 'Kar Yağışlı';
    if (code === 77) return 'Kar Taneleri';
    if (code <= 82) return 'Sağanak Yağış';
    if (code <= 86) return 'Kar Sağanağı';
    return 'Fırtınalı';
};
