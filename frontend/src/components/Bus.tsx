import { useState, useEffect } from 'react';
import { busService, API_BASE_URL } from '../services/busService';
import type { BusSchedule } from '../services/busService';
import { PdfViewer } from './PdfViewer';
import '../styles/Bus.css';

const removeDiacritics = (text: string) =>
    text
        .replace(/ı/g, 'i')
        .replace(/İ/g, 'I')
        .replace(/ğ/g, 'g')
        .replace(/Ğ/g, 'G')
        .replace(/ü/g, 'u')
        .replace(/Ü/g, 'U')
        .replace(/ş/g, 's')
        .replace(/Ş/g, 'S')
        .replace(/ö/g, 'o')
        .replace(/Ö/g, 'O')
        .replace(/ç/g, 'c')
        .replace(/Ç/g, 'C');

const getTodayDateTokens = () => {
    const now = new Date();
    const day = now.getDate();
    const month = now.getMonth() + 1;
    const monthNames = [
        'ocak', 'subat', 'mart', 'nisan', 'mayis', 'haziran',
        'temmuz', 'agustos', 'eylul', 'ekim', 'kasim', 'aralik'
    ];
    const monthName = monthNames[month - 1];
    const day2 = `${day}`.padStart(2, '0');
    const month2 = `${month}`.padStart(2, '0');

    return [
        `${day} ${monthName}`,
        `${day2} ${monthName}`,
        `${day}.${month}`,
        `${day2}.${month}`,
        `${day}.${month2}`,
        `${day2}.${month2}`,
        `${day}/${month}`,
        `${day2}/${month}`,
        `${day}/${month2}`,
        `${day2}/${month2}`,
        `${day}-${month}`,
        `${day2}-${month}`,
        `${day}-${month2}`,
        `${day2}-${month2}`
    ];
};

const findTodayPdfIndex = (pdfs: BusSchedule['pdfs']) => {
    const tokens = getTodayDateTokens();
    return pdfs.findIndex(pdf => {
        const haystack = removeDiacritics(`${pdf.label} ${pdf.url}`).toLowerCase();
        return tokens.some(token => haystack.includes(token));
    });
};

const toTitleCaseTr = (text: string) => {
    const cleaned = text.replace(/\s+/g, ' ').trim();
    if (!cleaned) return cleaned;
    return cleaned
        .toLocaleLowerCase('tr-TR')
        .split(' ')
        .map(word => (word ? word[0].toLocaleUpperCase('tr-TR') + word.slice(1) : ''))
        .join(' ');
};

export const Bus = ({ isOpen: propIsOpen, onToggle }: { isOpen?: boolean; onToggle?: () => void } = {}) => {
    const [schedule, setSchedule] = useState<BusSchedule | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [localOpen, setLocalOpen] = useState(false);
    const isOpen = propIsOpen !== undefined ? propIsOpen : localOpen;
    const handleToggle = onToggle ?? (() => setLocalOpen(prev => !prev));
    const [activeIndex, setActiveIndex] = useState(0);

    useEffect(() => {
        const fetchData = async () => {
            const cached = busService.getCachedSchedule();
            if (cached) {
                setSchedule(cached);
                autoSelectIndex(cached);
                setLoading(false);
            }

            try {
                const data = await busService.getSchedule();
                setSchedule(data);
                autoSelectIndex(data);
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

    const autoSelectIndex = (data: BusSchedule) => {
        if (data.pdfs.length === 0) return;
        const todayIndex = findTodayPdfIndex(data.pdfs);
        setActiveIndex(todayIndex >= 0 ? todayIndex : 0);
    };

    const pdfs = schedule?.pdfs ?? [];
    const activeEntry = pdfs[activeIndex] ?? null;
    const downloadPdfUrl = activeEntry?.url;
    const proxyVersion = encodeURIComponent(`${schedule?.last_update ?? ''}`);
    const proxyPdfUrl = downloadPdfUrl
        ? `${API_BASE_URL}/bus/pdf?url=${encodeURIComponent(downloadPdfUrl)}&v=${proxyVersion}`
        : '';

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
                                {pdfs.map((pdf, index) => (
                                    <button
                                        key={`${pdf.url}-${index}`}
                                        className={`type-btn ${activeIndex === index ? 'active' : ''}`}
                                        onClick={() => setActiveIndex(index)}
                                    >
                                        {toTitleCaseTr(pdf.label || `PDF ${index + 1}`)}
                                    </button>
                                ))}
                            </div>
                            <p className="last-update">
                                Son güncelleme: {new Date(schedule.last_update).toLocaleDateString('tr-TR')}
                            </p>
                        </div>

                        {/* PDF Viewer — tüm cihazlarda inline, zoom destekli */}
                        {activeEntry && proxyPdfUrl ? (
                            <PdfViewer
                                url={proxyPdfUrl}
                                downloadUrl={downloadPdfUrl}
                            />
                        ) : (
                            <div className="error-message">PDF bulunamadı</div>
                        )}
                    </div>
                ) : (
                    <div className="error-message">Veri bulunamadı</div>
                )}
            </div>
        </div>
    );
};

