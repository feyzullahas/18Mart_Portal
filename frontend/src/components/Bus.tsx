import { useState, useEffect } from 'react';
import { busService } from '../services/busService';
import type { BusSchedule } from '../services/busService';
import '../styles/Bus.css';

export const Bus = ({ isOpen: propIsOpen, onToggle }: { isOpen?: boolean; onToggle?: () => void } = {}) => {
    const [schedule, setSchedule] = useState<BusSchedule | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [localOpen, setLocalOpen] = useState(false);
    const [pdfLoading, setPdfLoading] = useState(true);
    const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
    const isOpen = propIsOpen !== undefined ? propIsOpen : localOpen;
    const handleToggle = onToggle ?? (() => setLocalOpen(prev => !prev));
    const [activeType, setActiveType] = useState<'weekday' | 'weekend'>('weekday');

    useEffect(() => {
        const handleResize = () => setIsMobile(window.innerWidth <= 768);
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

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

    // Tab değişince loading'i sıfırla
    useEffect(() => {
        setPdfLoading(true);
    }, [currentPdf]);

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
                                {isMobile ? (
                                    <div className="pdf-mobile-view">
                                        <p className="pdf-mobile-hint">
                                            En güncel PDF için tıklayın.
                                        </p>
                                        <a
                                            href={currentPdf}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="pdf-open-btn"
                                        >
                                            📄 PDF'i Görüntüle
                                        </a>
                                        <a
                                            href={currentPdf}
                                            download
                                            className="download-btn"
                                        >
                                            ⬇️ İndir
                                        </a>
                                    </div>
                                ) : (
                                    <>
                                        {pdfLoading && (
                                            <div className="pdf-loading">
                                                <div className="loading-spinner"></div>
                                                <p>PDF yükleniyor...</p>
                                            </div>
                                        )}
                                        <iframe
                                            key={currentPdf}
                                            src={`https://docs.google.com/viewer?url=${encodeURIComponent(currentPdf)}&embedded=true`}
                                            title="Otobüs Saatleri PDF"
                                            width="100%"
                                            height="600"
                                            style={{ border: 'none', borderRadius: '8px', display: pdfLoading ? 'none' : 'block' }}
                                            onLoad={() => setPdfLoading(false)}
                                        />
                                        <a
                                            href={currentPdf}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="download-btn"
                                        >
                                            ↗️ Yeni Sekmede Aç
                                        </a>
                                    </>
                                )}
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
