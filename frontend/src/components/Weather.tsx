import { useEffect, useState } from 'react';
import { weatherService, getWeatherEmoji, getWeatherDescription } from '../services/weatherService';
import type { CurrentWeather, Forecast } from '../services/weatherService';
import '../styles/Weather.css';

export const Weather = () => {
    const [current, setCurrent] = useState<CurrentWeather | null>(null);
    const [forecast, setForecast] = useState<Forecast | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isOpen, setIsOpen] = useState(false);

    useEffect(() => {
        const fetchWeather = async () => {
            try {
                setLoading(true);
                const [currentData, forecastData] = await Promise.all([
                    weatherService.getCurrentWeather(),
                    weatherService.getForecast(5)
                ]);
                setCurrent(currentData);
                setForecast(forecastData);
            } catch (err) {
                setError('Hava durumu yüklenemedi');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchWeather();
    }, []);

    if (loading) {
        return <div className="weather-card loading">Yükleniyor...</div>;
    }

    if (error || !current) {
        return <div className="weather-card error">{error}</div>;
    }

    return (
        <div className="weather-card">
            <div className="card-header" onClick={() => setIsOpen(!isOpen)}>
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
