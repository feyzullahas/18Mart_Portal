import { useEffect, useState } from 'react';
import '../styles/ExamCountdown.css';

interface CountdownTime {
    days: number;
    hours: number;
    minutes: number;
    seconds: number;
}

export interface ExamCountdownProps {
    variant?: 'card' | 'header';
    isOpen?: boolean;
    onToggle?: () => void;
}

export const ExamCountdown = ({ variant = 'card', isOpen: propIsOpen, onToggle }: ExamCountdownProps) => {
    const [finalTime, setFinalTime] = useState<CountdownTime>({ days: 0, hours: 0, minutes: 0, seconds: 0 });
    const [localOpen, setLocalOpen] = useState(false);
    const isOpen = propIsOpen !== undefined ? propIsOpen : localOpen;
    const handleToggle = onToggle ?? (() => setLocalOpen(prev => !prev));

    // Sabit tarihler
    const finalDate = new Date('2026-06-08T09:00:00'); // 8 Haziran 2026, 09:00

    const calculateCountdown = (targetDate: Date): CountdownTime => {
        const now = new Date();
        const difference = targetDate.getTime() - now.getTime();

        if (difference <= 0) {
            return { days: 0, hours: 0, minutes: 0, seconds: 0 };
        }

        const days = Math.floor(difference / (1000 * 60 * 60 * 24));
        const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((difference % (1000 * 60)) / 1000);

        return { days, hours, minutes, seconds };
    };

    useEffect(() => {
        const updateCountdowns = () => {
            setFinalTime(calculateCountdown(finalDate));
        };

        updateCountdowns();
        const interval = setInterval(updateCountdowns, 1000);

        return () => clearInterval(interval);
    }, []);

    
    const formatCompact = (time: CountdownTime) => {
        if (time.days > 0) return `${time.days}g ${time.hours}s`;
        if (time.hours > 0) return `${time.hours}s ${time.minutes}d`;
        if (time.minutes > 0) return `${time.minutes}d ${time.seconds}s`;
        return `${time.seconds}s`;
    };

    // Header variant - küçük ve sabit
    if (variant === 'header') {
        return (
            <div className="exam-countdown-header-widget">
                <div className="exam-countdown-header-item">
                    <div className="exam-countdown-header-label">Finallere kalan</div>
                    <div className="exam-countdown-header-time">{formatCompact(finalTime)}</div>
                </div>
            </div>
        );
    }

    // Card variant - açılır-kapanır
    return (
        <div className="exam-countdown-card">
            <div className="card-header" onClick={handleToggle}>
                <h2>📝 Final Sayacı</h2>
                <span className={`toggle-icon ${isOpen ? 'open' : ''}`}>▼</span>
            </div>

            <div className={`card-content ${isOpen ? 'open' : ''}`}>
                    <div className="exam-countdown-content">
                        <div className="exam-countdown-section">
                            <div className="exam-countdown-header">
                                <div className="exam-countdown-date">8 Haziran 2026</div>
                            </div>
                            <div className="exam-countdown-time-large">
                                <div className="time-unit">
                                    <span className="time-value">{finalTime.days}</span>
                                    <span className="time-label">gün</span>
                                </div>
                                <div className="time-unit">
                                    <span className="time-value">{String(finalTime.hours).padStart(2, '0')}</span>
                                    <span className="time-label">saat</span>
                                </div>
                                <div className="time-unit">
                                    <span className="time-value">{String(finalTime.minutes).padStart(2, '0')}</span>
                                    <span className="time-label">dakika</span>
                                </div>
                                <div className="time-unit">
                                    <span className="time-value">{String(finalTime.seconds).padStart(2, '0')}</span>
                                    <span className="time-label">saniye</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
        </div>
    );
};
