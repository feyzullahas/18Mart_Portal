import { useState, useEffect } from 'react';
import { busService, API_BASE_URL } from '../services/busService';
import type { BusSchedule } from '../services/busService';
import { PdfViewer } from './PdfViewer';
import '../styles/Bus.css';

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
            const cached = busService.getCachedSchedule();
            if (cached) {
                setSchedule(cached);
                setLoading(false);
            }

            try {
                const data = await busService.getSchedule();
                setSchedule(data);

                // Bugüne göre default seç
                const day = new Date().getDay();
                if (day === 0 || day === 6) {
                    setActiveType('weekend');
                }
            } catch (err) {
                if (!cached) {
                    setError('Otobüs saatleri yüklenemedi');
                }
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
                    </div>
                ) : error ? (
                    <div className="error-message">{error}</div>
                ) : schedule ? (
                    <div className="bus-content">
                        <p className="bus-info">
                            Kaynak: <strong>{schedule.source}</strong>
                        </p>

                        <div className="schedule-selector">
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
