const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://18-mart-portal-4orl.vercel.app';

export interface CurrentWeather {
    current_weather: {
        temperature: number;
        windspeed: number;
        weathercode: number;
        time: string;
    };
}

export interface Forecast {
    daily: {
        time: string[];
        temperature_2m_max: number[];
        temperature_2m_min: number[];
        weathercode: number[];
    };
}

export const weatherService = {
    async getCurrentWeather(): Promise<CurrentWeather> {
        const response = await fetch(`${API_BASE_URL}/weather/current`);
        if (!response.ok) throw new Error('Hava durumu alınamadı');
        return response.json();
    },

    async getForecast(days: number = 5): Promise<Forecast> {
        const response = await fetch(`${API_BASE_URL}/weather/forecast?days=${days}`);
        if (!response.ok) throw new Error('Tahmin alınamadı');
        return response.json();
    }
};

// Hava durumu kodlarını emoji'ye çevir
export const getWeatherEmoji = (code: number): string => {
    if (code === 0) return '☀️';
    if (code <= 3) return '⛅';
    if (code <= 48) return '🌫️';
    if (code <= 67) return '🌧️';
    if (code <= 77) return '🌨️';
    if (code <= 82) return '🌧️';
    if (code <= 86) return '🌨️';
    return '⛈️';
};

// Hava durumu kodlarını açıklamaya çevir
export const getWeatherDescription = (code: number): string => {
    if (code === 0) return 'Açık';
    if (code <= 3) return 'Parçalı Bulutlu';
    if (code <= 48) return 'Sisli';
    if (code <= 67) return 'Yağmurlu';
    if (code <= 77) return 'Karlı';
    if (code <= 82) return 'Sağanak Yağışlı';
    if (code <= 86) return 'Kar Yağışlı';
    return 'Fırtınalı';
};
