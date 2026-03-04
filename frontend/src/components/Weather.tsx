import { useEffect, useState } from 'react';
import { weatherService, getWeatherEmoji, getWeatherDescription } from '../services/weatherService';
import type { CurrentWeather, Forecast } from '../services/weatherService';
import '../styles/Weather.css';

export interface WeatherProps {
    variant?: 'card' | 'header';
    isOpen?: boolean;
    onToggle?: () => void;
}

export const Weather = ({ variant = 'card', isOpen: propIsOpen, onToggle }: WeatherProps) => {
    const [current, setCurrent] = useState<CurrentWeather | null>(null);
    const [forecast, setForecast] = useState<Forecast | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [localOpen, setLocalOpen] = useState(false);
    const isOpen = propIsOpen !== undefined ? propIsOpen : localOpen;
    const handleToggle = onToggle ?? (() => setLocalOpen(prev => !prev));

    useEffect(() => {
        const fetchWeather = async () => {
            try {
                setLoading(true);
                // Header modunda sadece güncel veriyi çeksek yeterli aslında ama
                // şimdilik yapıyı bozmadan ikisini de çekelim, performans sorunu olmaz.
                const [currentData, forecastData] = await Promise.all([
                    weatherService.getCurrentWeather(),
                    weatherService.getForecast(5)
                ]);
                setCurrent(currentData);
                setForecast(forecastData);
            } catch (err) {
                // Header'da hata mesajı göstermek istemeyebiliriz, sessizce fail olabilir
                if (variant === 'card') {
                    setError('Hava durumu yüklenemedi');
                }
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchWeather();
    }, [variant]);

    if (variant === 'header') {
        if (loading) return <div className="weather-header-loading">...</div>;
        if (error || !current || !forecast) return null;
    }

    // --- Header Variant Rendering ---
    if (variant === 'header' && forecast) {
        return (
            <div className="weather-header-widget">
                {/* Today - Large */}
                <div className="weather-header-today">
                    <div className="weather-header-icon-large">
                        {getWeatherEmoji(forecast.daily.weathercode[0])}
                    </div>
                    <div className="weather-header-today-info">
                        <span className="weather-header-temp-large">
                            {Math.round(forecast.daily.temperature_2m_max[0])}°
                        </span>
                        <span className="weather-header-day">Bugün</span>
                    </div>
                </div>

                {/* Next 2 Days - Smaller */}
                <div className="weather-header-forecast">
                    {[1, 2].map((index) => {
                        const date = new Date(forecast.daily.time[index]);
                        const dayName = date.toLocaleDateString('tr-TR', { weekday: 'short' });

                        return (
                            <div key={index} className="weather-header-day-item">
                                <span className="weather-header-day-name">{dayName}</span>
                                <div className="weather-header-icon-small">
                                    {getWeatherEmoji(forecast.daily.weathercode[index])}
                                </div>
                                <span className="weather-header-temp-small">
                                    {Math.round(forecast.daily.temperature_2m_max[index])}°
                                </span>
                            </div>
                        );
                    })}
                </div>
            </div>
        );
    }

    // --- Default Card Rendering ---
    // For card variant, show the collapsed card even while loading
    if (!current) {
        return (
            <div className="weather-card">
                <div className="card-header" onClick={handleToggle}>
                    <h2>🌍 Çanakkale Hava Durumu</h2>
                    <span className={`toggle-icon ${isOpen ? 'open' : ''}`}>▼</span>
                </div>
                <div className={`card-content ${isOpen ? 'open' : ''}`}>
                    {loading ? (
                        <div className="weather-loading">Yükleniyor...</div>
                    ) : (
                        <div className="weather-error">{error || 'Hava durumu yüklenemedi'}</div>
                    )}
                </div>
            </div>
        );
    }
    return (
        <div className="weather-card">
            <div className="card-header" onClick={handleToggle}>
                <h2>🌍 Çanakkale Hava Durumu</h2>
                <span className={`toggle-icon ${isOpen ? 'open' : ''}`}>▼</span>
            </div>

            <div className={`card-content ${isOpen ? 'open' : ''}`}>
                {/* Güncel Hava Durumu */}
                <div className="current-weather">
                    <div className="weather-main">
                        <div className="weather-icon">
                            {getWeatherEmoji(current.current_weather.weathercode)}
                        </div>
                        <div className="weather-temp">
                            <span className="temp-value">{Math.round(current.current_weather.temperature)}°</span>
                            <span className="temp-unit">C</span>
                        </div>
                    </div>
                    <div className="weather-desc">
                        {getWeatherDescription(current.current_weather.weathercode)}
                    </div>
                    <div className="weather-wind">
                        💨 Rüzgar: {Math.round(current.current_weather.windspeed)} km/s
                    </div>
                </div>

                {/* 5 Günlük Tahmin */}
                {forecast && (
                    <div className="forecast">
                        <h3>Hava Tahmini</h3>
                        <div className="forecast-grid">
                            {forecast.daily.time.map((date, index) => {
                                const dayName = new Date(date).toLocaleDateString('tr-TR', { weekday: 'short' });
                                return (
                                    <div key={date} className="forecast-item">
                                        <div className="forecast-day">{dayName}</div>
                                        <div className="forecast-icon">
                                            {getWeatherEmoji(forecast.daily.weathercode[index])}
                                        </div>
                                        <div className="forecast-temp">
                                            <span className="temp-max">{Math.round(forecast.daily.temperature_2m_max[index])}°</span>
                                            <span className="temp-min">{Math.round(forecast.daily.temperature_2m_min[index])}°</span>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
