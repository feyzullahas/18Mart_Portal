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
    const [selectedDayIndex, setSelectedDayIndex] = useState(0);
    const isOpen = propIsOpen !== undefined ? propIsOpen : localOpen;
    const handleToggle = onToggle ?? (() => setLocalOpen(prev => !prev));

    useEffect(() => {
        const fetchWeather = async () => {
            const cachedCurrent = weatherService.getCachedCurrentWeather();
            const cachedForecast = weatherService.getCachedForecast(7);

            if (cachedCurrent && cachedForecast) {
                setCurrent(cachedCurrent);
                setForecast(cachedForecast);
                setLoading(false);
            }

            try {
                if (!cachedCurrent || !cachedForecast) {
                    setLoading(true);
                }
                const [currentData, forecastData] = await Promise.all([
                    weatherService.getCurrentWeather(),
                    weatherService.getForecast(7)
                ]);
                setCurrent(currentData);
                setForecast(forecastData);
            } catch (err) {
                if (variant === 'card' && (!cachedCurrent || !cachedForecast)) {
                    setError('Hava durumu yüklenemedi');
                }
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
                    <h2>☀️ Çanakkale Hava Durumu</h2>
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

    // ─── Saatlik slice: seçili güne göre ──────────────────────────────
    const now = new Date();
    const pad = (n: number) => String(n).padStart(2, '0');

    let hourStart: number;
    let hourlySlice: string[];

    if (selectedDayIndex === 0) {
        // Bugün: şu andan itibaren 25 saat
        const currentHourStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:00`;
        const startIndex = forecast.hourly.time.findIndex(t => t === currentHourStr);
        hourStart = startIndex >= 0 ? startIndex : 0;
        hourlySlice = forecast.hourly.time.slice(hourStart, hourStart + 25);
    } else {
        // Seçili gün: o günün tüm saatlerini göster
        const selectedDate = forecast.daily.time[selectedDayIndex]; // "YYYY-MM-DD"
        hourStart = forecast.hourly.time.findIndex(t => t.startsWith(selectedDate));
        if (hourStart < 0) hourStart = 0;
        hourlySlice = forecast.hourly.time.slice(hourStart, hourStart + 24);
    }


    const today = new Date();

    return (
        <div className="weather-card">
            <div className="card-header" onClick={handleToggle}>
                <h2>☀️ Çanakkale Hava Durumu</h2>
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
                            <span className="detail-label">Nem</span>
                            <span className="detail-value">{current.current.relative_humidity_2m}%</span>
                        </div>
                        <div className="current-detail-item">
                            <span className="detail-label">Rüzgar</span>
                            <span className="detail-value">{Math.round(current.current.wind_speed_10m)} km/s</span>
                        </div>
                        <div className="current-detail-item">
                            <span className="detail-label">Yağış</span>
                            <span className="detail-value">{current.current.precipitation} mm</span>
                        </div>
                    </div>
                </div>

                {/* ── Saatlik Tahmin ── */}
                <div className="hourly-section">
                    <div className="section-title">
                        {selectedDayIndex === 0
                            ? 'Saatlik Tahmin'
                            : `${new Date(forecast.daily.time[selectedDayIndex]).toLocaleDateString('tr-TR', { weekday: 'long', day: 'numeric', month: 'long' })} Saatlik Tahmin`}
                    </div>
                    <div className="hourly-scroll">
                        {hourlySlice.map((timeStr, i) => {
                            const idx = hourStart + i;
                            const date = new Date(timeStr);
                            const isNow = selectedDayIndex === 0 && i === 0;
                            const label = isNow ? 'Şimdi' : `${pad(date.getHours())}:00`;
                            const precip = forecast.hourly.precipitation_probability[idx];
                            return (
                                <div key={timeStr} className={`hourly-item${isNow ? ' hourly-item--now' : ''}`}>
                                    <span className="hourly-time">{label}</span>
                                    <span className="hourly-icon">
                                        {getWeatherEmoji(forecast.hourly.weathercode[idx], date.getHours())}
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

                            return (
                                <div key={dateStr}
                                    className={`daily-item${isToday ? ' daily-item--today' : ''}${selectedDayIndex === index ? ' daily-item--selected' : ''}`}
                                    onClick={() => setSelectedDayIndex(index)}
                                    style={{ cursor: 'pointer' }}
                                >
                                    <span className="daily-day">{dayName}</span>
                                    <span className="daily-icon">
                                        {getWeatherEmoji(forecast.daily.weathercode[index])}
                                    </span>
                                    <span className="daily-precip">
                                        {precip > 0 ? `💧${precip}%` : ''}
                                    </span>
                                    <span className="daily-temp-range">
                                        <span className="daily-temp-min">{Math.round(dayMin)}°</span>
                                        <span className="daily-temp-sep">/</span>
                                        <span className="daily-temp-max">{Math.round(dayMax)}°</span>
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>

            </div>
        </div>
    );
};
