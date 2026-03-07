import { useState, useEffect } from 'react';
import { busService } from '../services/busService';
import type { BusSchedule } from '../services/busService';
import { PdfViewer } from './PdfViewer';
import '../styles/Bus.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://18-mart-portal-4orl.vercel.app';

export const Bus = ({ isOpen: propIsOpen, onToggle }: { isOpen?: boolean; onToggle?: () => void } = {}) => {
    const [schedule, setSchedule] = useState<BusSchedule | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [localOpen, setLocalOpen] = useState(false);
    const isOpen = propIsOpen !== undefined ? propIsOpen : localOpen;
    const handleToggle = onToggle ?? (() => setLocalOpen(prev => !prev));
    const [activeType, setActiveType] = useState<'weekday' | 'weekend'>('weekday');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const data = await busService.getSchedule();
                setSchedule(data);

                // Bugüne göre default seç
                const day = new Date().getDay();
                if (day === 0 || day === 6) {
                    setActiveType('weekend');
                }
            } catch (err) {
                setError('Otobüs saatleri yüklenemedi');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    // Proxy URL (CORS bypass) ve download için orijinal URL
    const proxyPdfUrl = `${API_BASE_URL}/bus/pdf/${activeType}`;
    const downloadPdfUrl = activeType === 'weekday'
        ? schedule?.weekday?.url
        : schedule?.weekend?.url;

    return (
        <div className="bus-card">
            <div className="card-header" onClick={handleToggle}>
                <h2>🚌 Otobüs Saatleri</h2>
                <span className={`toggle-icon ${isOpen ? 'open' : ''}`}>▼</span>
            </div>

            <div className={`card-content ${isOpen ? 'open' : ''}`}>
                {loading ? (
                    <div className="loading-indicator">
                        <div className="loading-spinner"></div>
                        <p>Yükleniyor...</p>
                    </div>
                ) : error ? (
                    <div className="error-message">{error}</div>
                ) : schedule ? (
                    <div className="bus-content">
                        <p className="bus-info">
                            📍 Kaynak: <strong>{schedule.source}</strong>
                        </p>

                        {/* Sefer Saatleri Seçin */}
                        <div className="schedule-selector">
                            <h3>🚏 Sefer Saatleri Seçin</h3>
                            <div className="type-buttons">
                                <button
                                    className={`type-btn ${activeType === 'weekday' ? 'active' : ''}`}
                                    onClick={() => setActiveType('weekday')}
                                >
                                    Haftaiçi
                                </button>
                                <button
                                    className={`type-btn ${activeType === 'weekend' ? 'active' : ''}`}
                                    onClick={() => setActiveType('weekend')}
                                >
                                    Haftasonu
                                </button>
                            </div>
                            <p className="last-update">
                                Son güncelleme: {new Date(schedule.last_update).toLocaleDateString('tr-TR')}
                            </p>
                        </div>

                        {/* PDF Viewer — tüm cihazlarda inline, zoom destekli */}
                        <PdfViewer
                            url={proxyPdfUrl}
                            downloadUrl={downloadPdfUrl}
                        />
                    </div>
                ) : (
                    <div className="error-message">Veri bulunamadı</div>
                )}
            </div>
        </div>
    );
};
