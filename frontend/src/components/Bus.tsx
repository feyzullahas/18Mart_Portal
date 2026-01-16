import { useState, useEffect } from 'react';
import { busService } from '../services/busService';
import type { BusSchedule } from '../services/busService';
import '../styles/Bus.css';

export const Bus = () => {
    const [schedule, setSchedule] = useState<BusSchedule | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isOpen, setIsOpen] = useState(false);
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

    const currentPdf = activeType === 'weekday'
        ? schedule?.weekday?.url
        : schedule?.weekend?.url;

    return (
        <div className="bus-card">
            <div className="card-header" onClick={() => setIsOpen(!isOpen)}>
                <h2>🚌 Otobüs Saatleri</h2>
                <span className={`toggle-icon ${isOpen ? 'open' : ''}`}>▼</span>
            </div>

            <div className={`card-content ${isOpen ? 'open' : ''}`}>
                {loading ? (
                    <div className="loading-spinner">Yükleniyor...</div>
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
                                    📅 Haftaiçi
                                </button>
                                <button
                                    className={`type-btn ${activeType === 'weekend' ? 'active' : ''}`}
                                    onClick={() => setActiveType('weekend')}
                                >
                                    🌴 Haftasonu
                                </button>
                            </div>
                            <p className="last-update">
                                Son güncelleme: {new Date(schedule.last_update).toLocaleDateString('tr-TR')}
                            </p>
                        </div>

                        {/* PDF Viewer */}
                        {currentPdf && (
                            <div className="pdf-viewer">
                                <iframe
                                    src={`${currentPdf}#toolbar=1&navpanes=0`}
                                    title="Otobüs Saatleri PDF"
                                    width="100%"
                                    height="500"
                                />
                                <a
                                    href={currentPdf}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="download-btn"
                                >
                                    ↗ PDF'yi Yeni Sekmede Aç
                                </a>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="error-message">Veri bulunamadı</div>
                )}
            </div>
        </div>
    );
};
