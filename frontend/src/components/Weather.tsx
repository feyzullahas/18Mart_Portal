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
                const [currentData, forecastData] = await Promise.all([
                    weatherService.getCurrentWeather(),
                    weatherService.getForecast(7)
                ]);
                setCurrent(currentData);
                setForecast(forecastData);
            } catch (err) {
                if (variant === 'card') setError('Hava durumu yüklenemedi');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchWeather();
    }, [variant]);

    // ─── Header Variant ──────────────────────────────────────────
    if (variant === 'header') {
        if (loading) return <div className="weather-header-loading">...</div>;
        if (error || !current || !forecast) return null;

        return (
            <div className="weather-header-widget">
                <div className="weather-header-today">
                    <div className="weather-header-icon-large">
                        {getWeatherEmoji(forecast.daily.weathercode[0])}
                    </div>
                    <div className="weather-header-today-info">
                        <span className="weather-header-temp-large">
                            {Math.round(current.current.temperature_2m)}°
                        </span>
                        <span className="weather-header-day">Bugün</span>
                    </div>
                </div>
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

    // ─── Card Variant – loading / error shell ────────────────────
    if (!current || !forecast) {
        return (
            <div className="weather-card">
                <div className="card-header" onClick={handleToggle}>
                    <h2>🌍 Çanakkale Hava Durumu</h2>
                    <span className={`toggle-icon ${isOpen ? 'open' : ''}`}>▼</span>
                </div>
                <div className={`card-content ${isOpen ? 'open' : ''}`}>
                    {loading
                        ? <div className="weather-loading">Yükleniyor...</div>
                        : <div className="weather-error">{error || 'Hava durumu yüklenemedi'}</div>}
                </div>
            </div>
        );
    }

    // ─── Saatlik slice: şu andan itibaren 25 saat ───────────────
    const now = new Date();
    const pad = (n: number) => String(n).padStart(2, '0');
    const currentHourStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:00`;
    const startIndex = forecast.hourly.time.findIndex(t => t === currentHourStr);
    const hourStart = startIndex >= 0 ? startIndex : 0;
    const hourlySlice = forecast.hourly.time.slice(hourStart, hourStart + 25);

    // ─── Sıcaklık barı için global min/max ──────────────────────
    const globalMin = Math.min(...forecast.daily.temperature_2m_min);
    const globalMax = Math.max(...forecast.daily.temperature_2m_max);
    const tempRange = globalMax - globalMin || 1;

    const today = new Date();

    return (
        <div className="weather-card">
            <div className="card-header" onClick={handleToggle}>
                <h2>🌍 Çanakkale Hava Durumu</h2>
                <span className={`toggle-icon ${isOpen ? 'open' : ''}`}>▼</span>
            </div>

            <div className={`card-content ${isOpen ? 'open' : ''}`}>

                {/* ── Anlık Hava ── */}
                <div className="current-weather">
                    <div className="current-weather-main">
                        <div className="current-weather-icon">
                            {getWeatherEmoji(current.current.weathercode)}
                        </div>
                        <div className="current-weather-info">
                            <div className="current-temp">
                                {Math.round(current.current.temperature_2m)}
                                <span className="current-temp-unit">°C</span>
                            </div>
                            <div className="current-desc">
                                {getWeatherDescription(current.current.weathercode)}
                            </div>
                            <div className="current-feels">
                                Hissedilen {Math.round(current.current.apparent_temperature)}°C
                            </div>
                        </div>
                    </div>
                    <div className="current-details">
                        <div className="current-detail-item">
                            <span className="detail-icon">💧</span>
                            <span className="detail-label">Nem</span>
                            <span className="detail-value">{current.current.relative_humidity_2m}%</span>
                        </div>
                        <div className="current-detail-item">
                            <span className="detail-icon">💨</span>
                            <span className="detail-label">Rüzgar</span>
                            <span className="detail-value">{Math.round(current.current.wind_speed_10m)} km/s</span>
                        </div>
                        <div className="current-detail-item">
                            <span className="detail-icon">🌂</span>
                            <span className="detail-label">Yağış</span>
                            <span className="detail-value">{current.current.precipitation} mm</span>
                        </div>
                    </div>
                </div>

                {/* ── Saatlik Tahmin ── */}
                <div className="hourly-section">
                    <div className="section-title">Saatlik Tahmin</div>
                    <div className="hourly-scroll">
                        {hourlySlice.map((timeStr, i) => {
                            const idx = hourStart + i;
                            const date = new Date(timeStr);
                            const isNow = i === 0;
                            const label = isNow ? 'Şimdi' : `${pad(date.getHours())}:00`;
                            const precip = forecast.hourly.precipitation_probability[idx];
                            return (
                                <div key={timeStr} className={`hourly-item${isNow ? ' hourly-item--now' : ''}`}>
                                    <span className="hourly-time">{label}</span>
                                    <span className="hourly-icon">
                                        {getWeatherEmoji(forecast.hourly.weathercode[idx])}
                                    </span>
                                    {precip > 0 && (
                                        <span className="hourly-precip">💧{precip}%</span>
                                    )}
                                    <span className="hourly-temp">
                                        {Math.round(forecast.hourly.temperature_2m[idx])}°
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* ── 7 Günlük Tahmin ── */}
                <div className="daily-section">
                    <div className="section-title">7 Günlük Tahmin</div>
                    <div className="daily-list">
                        {forecast.daily.time.map((dateStr, index) => {
                            const date = new Date(dateStr);
                            const isToday = date.toDateString() === today.toDateString();
                            const dayName = isToday
                                ? 'Bugün'
                                : date.toLocaleDateString('tr-TR', { weekday: 'long' });
                            const dayMin = forecast.daily.temperature_2m_min[index];
                            const dayMax = forecast.daily.temperature_2m_max[index];
                            const precip = forecast.daily.precipitation_probability_max[index];
                            const barLeft = ((dayMin - globalMin) / tempRange) * 100;
                            const barWidth = ((dayMax - dayMin) / tempRange) * 100;

                            return (
                                <div key={dateStr} className={`daily-item${isToday ? ' daily-item--today' : ''}`}>
                                    <span className="daily-day">{dayName}</span>
                                    <span className="daily-icon">
                                        {getWeatherEmoji(forecast.daily.weathercode[index])}
                                    </span>
                                    <span className="daily-precip">
                                        {precip > 0 ? `💧${precip}%` : ''}
                                    </span>
                                    <div className="daily-bar-row">
                                        <span className="daily-temp-min">{Math.round(dayMin)}°</span>
                                        <div className="daily-bar-track">
                                            <div
                                                className="daily-bar-fill"
                                                style={{ left: `${barLeft}%`, width: `${Math.max(barWidth, 8)}%` }}
                                            />
                                        </div>
                                        <span className="daily-temp-max">{Math.round(dayMax)}°</span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

            </div>
        </div>
    );
};
