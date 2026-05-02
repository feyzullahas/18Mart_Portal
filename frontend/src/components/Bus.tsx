import { useState, useEffect } from 'react';
import { busService, API_BASE_URL } from '../services/busService';
import type { BusSchedule } from '../services/busService';
import { PdfViewer } from './PdfViewer';
import '../styles/Bus.css';

type ScheduleType = 'weekday' | 'weekend' | 'special';

export const Bus = ({ isOpen: propIsOpen, onToggle }: { isOpen?: boolean; onToggle?: () => void } = {}) => {
    const [schedule, setSchedule] = useState<BusSchedule | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [localOpen, setLocalOpen] = useState(false);
    const isOpen = propIsOpen !== undefined ? propIsOpen : localOpen;
    const handleToggle = onToggle ?? (() => setLocalOpen(prev => !prev));
    const [activeType, setActiveType] = useState<ScheduleType>('weekday');

    useEffect(() => {
        const fetchData = async () => {
            const cached = busService.getCachedSchedule();
            if (cached) {
                setSchedule(cached);
                autoSelectType(cached);
                setLoading(false);
            }

            try {
                const data = await busService.getSchedule();
                setSchedule(data);
                autoSelectType(data);
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

    const autoSelectType = (data: BusSchedule) => {
        // Özel gün PDF'i varsa onu göster
        if (data.special) {
            setActiveType('special');
            return;
        }
        // Hafta sonu ise hafta sonu seç
        const day = new Date().getDay();
        if (day === 0 || day === 6) {
            setActiveType('weekend');
        } else {
            setActiveType('weekday');
        }
    };

    // Aktif türe göre URL'leri belirle
    const getActiveEntry = () => {
        if (!schedule) return null;
        if (activeType === 'special') return schedule.special;
        if (activeType === 'weekend') return schedule.weekend;
        return schedule.weekday;
    };

    const activeEntry = getActiveEntry();
    const downloadPdfUrl = activeEntry?.url;
    const proxyVersion = encodeURIComponent(`${downloadPdfUrl ?? ''}|${schedule?.last_update ?? ''}`);
    const proxyPdfUrl = `${API_BASE_URL}/bus/pdf/${activeType}?v=${proxyVersion}`;

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
                                {schedule.special && (
                                    <button
                                        className={`type-btn special-btn ${activeType === 'special' ? 'active' : ''}`}
                                        onClick={() => setActiveType('special')}
                                    >
                                        ⭐ {schedule.special.label}
                                    </button>
                                )}
                                <button
                                    className={`type-btn ${activeType === 'weekday' ? 'active' : ''}`}
                                    onClick={() => setActiveType('weekday')}
                                >
                                    Hafta içi
                                </button>
                                <button
                                    className={`type-btn ${activeType === 'weekend' ? 'active' : ''}`}
                                    onClick={() => setActiveType('weekend')}
                                >
                                    Hafta sonu
                                </button>
                            </div>
                            <p className="last-update">
                                Son güncelleme: {new Date(schedule.last_update).toLocaleDateString('tr-TR')}
                            </p>
                        </div>

                        {/* PDF Viewer — tüm cihazlarda inline, zoom destekli */}
                        {activeEntry ? (
                            <PdfViewer
                                url={proxyPdfUrl}
                                downloadUrl={downloadPdfUrl}
                            />
                        ) : (
                            <div className="error-message">Bu tür için PDF bulunamadı</div>
                        )}
                    </div>
                ) : (
                    <div className="error-message">Veri bulunamadı</div>
                )}
            </div>
        </div>
    );
};

