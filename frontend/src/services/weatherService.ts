const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://18-mart-portal-4orl.vercel.app';

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
    async getCurrentWeather(): Promise<CurrentWeather> {
        const response = await fetch(`${API_BASE_URL}/weather/current`);
        if (!response.ok) throw new Error('Hava durumu alınamadı');
        return response.json();
    },

    async getForecast(days: number = 7): Promise<Forecast> {
        const response = await fetch(`${API_BASE_URL}/weather/forecast?days=${days}`);
        if (!response.ok) throw new Error('Tahmin alınamadı');
        return response.json();
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
