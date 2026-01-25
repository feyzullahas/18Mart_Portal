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
}

export const ExamCountdown = ({ variant = 'card' }: ExamCountdownProps) => {
    const [midtermTime, setMidtermTime] = useState<CountdownTime>({ days: 0, hours: 0, minutes: 0, seconds: 0 });
    const [finalTime, setFinalTime] = useState<CountdownTime>({ days: 0, hours: 0, minutes: 0, seconds: 0 });
    const [isOpen, setIsOpen] = useState(false);

    // Sabit tarihler
    const midtermDate = new Date('2026-04-06T09:00:00'); // 6 Nisan 2026, 09:00
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
            setMidtermTime(calculateCountdown(midtermDate));
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
                    <div className="exam-countdown-header-label">Vizelere kalan</div>
                    <div className="exam-countdown-header-time">{formatCompact(midtermTime)}</div>
                </div>
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
            <div className="card-header" onClick={() => setIsOpen(!isOpen)}>
                <h2>📝 Vize & Final Sayacı</h2>
                <span className={`toggle-icon ${isOpen ? 'open' : ''}`}>▼</span>
            </div>

            {isOpen && (
                <div className="card-content open">
                    <div className="exam-countdown-content">
                        {/* Vizeler */}
                        <div className="exam-countdown-section">
                            <div className="exam-countdown-header">
                                <h3>📚 Vizelere kalan süre</h3>
                                <div className="exam-countdown-date">6 Nisan 2026</div>
                            </div>
                            <div className="exam-countdown-time-large">
                                <div className="time-unit">
                                    <span className="time-value">{midtermTime.days}</span>
                                    <span className="time-label">gün</span>
                                </div>
                                <div className="time-unit">
                                    <span className="time-value">{String(midtermTime.hours).padStart(2, '0')}</span>
                                    <span className="time-label">saat</span>
                                </div>
                                <div className="time-unit">
                                    <span className="time-value">{String(midtermTime.minutes).padStart(2, '0')}</span>
                                    <span className="time-label">dakika</span>
                                </div>
                                <div className="time-unit">
                                    <span className="time-value">{String(midtermTime.seconds).padStart(2, '0')}</span>
                                    <span className="time-label">saniye</span>
                                </div>
                            </div>
                        </div>

                        {/* Finaller */}
                        <div className="exam-countdown-section">
                            <div className="exam-countdown-header">
                                <h3>🎯 Finallere kalan süre</h3>
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
            )}
        </div>
    );
};
