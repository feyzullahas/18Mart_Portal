import { useState, useEffect } from 'react';
import { calendarService } from '../services/calendarService';
import type { CalendarInfo, CalendarType } from '../services/calendarService';
import '../styles/Calendar.css';

export const Calendar = () => {
    // State
    const [calendar, setCalendar] = useState<CalendarInfo | null>(null);
    const [mainTypes, setMainTypes] = useState<CalendarType[]>([]);
    const [subTypes, setSubTypes] = useState<{ [key: string]: CalendarType[] }>({});

    // Selections
    const [selectedMain, setSelectedMain] = useState('general');
    const [selectedSub, setSelectedSub] = useState('');

    // Calendar Grid State
    const [currentDate, setCurrentDate] = useState(new Date());
    const [loading, setLoading] = useState(true);
    const [isOpen, setIsOpen] = useState(false);

    // Initial Load
    useEffect(() => {
        const loadTypes = async () => {
            try {
                const data = await calendarService.getTypes();
                setMainTypes(data.calendars);
                setSubTypes(data.sub_calendars);
            } catch (err) {
                console.error("Takvim tipleri yüklenemedi", err);
            }
        };
        loadTypes();
    }, []);

    // Fetch Events when selection changes
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                // Eğer alt kategori seçildiyse onu, yoksa ana kategoriyi kullan
                const idToFetch = selectedSub || selectedMain;
                const data = await calendarService.getEvents(idToFetch);
                setCalendar(data);
            } catch (err) {
                console.error("Takvim verisi yüklenemedi", err);
            } finally {
                setLoading(false);
            }
        };

        // Alt kategori gerektirmeyen veya alt kategorisi seçilmiş tipler için fetch et
        const mainType = mainTypes.find(t => t.id === selectedMain);
        if (mainType) {
            if (!mainType.has_sub || (mainType.has_sub && selectedSub)) {
                fetchData();
            }
        }
    }, [selectedMain, selectedSub, mainTypes]);

    // Main type değişince sub type'ı sıfırla ve gerekirse otomatik ilkini seç
    useEffect(() => {
        const mainType = mainTypes.find(t => t.id === selectedMain);
        if (mainType?.has_sub) {
            const subs = subTypes[selectedMain];
            if (subs && subs.length > 0) {
                setSelectedSub(subs[0].id); // Otomatik ilkini seç
            } else {
                setSelectedSub('');
            }
        } else {
            setSelectedSub('');
        }
    }, [selectedMain, mainTypes, subTypes]);


    // Calendar Logic
    const getDaysInMonth = (date: Date) => {
        return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
    };

    const getFirstDayOfMonth = (date: Date) => {
        // 0 = Sunday, 1 = Monday. We want Monday start (0=Mon, 6=Sun)
        let day = new Date(date.getFullYear(), date.getMonth(), 1).getDay();
        return day === 0 ? 6 : day - 1;
    };

    const changeMonth = (offset: number) => {
        const newDate = new Date(currentDate);
        newDate.setMonth(newDate.getMonth() + offset);
        setCurrentDate(newDate);
    };

    // Etkinlikleri günlere dağıt
    const getEventsForDay = (day: number) => {
        if (!calendar?.events) return [];

        const currentMonthStr = currentDate.toISOString().slice(0, 7); // YYYY-MM
        const dayStr = day < 10 ? `0${day}` : `${day}`;
        const targetDate = `${currentMonthStr}-${dayStr}`;

        return calendar.events.filter(event => {
            // Basit string karşılaştırması (YYY-MM-DD)
            return targetDate >= event.start && targetDate <= event.end;
        });
    };

    const renderCalendarGrid = () => {
        const daysInMonth = getDaysInMonth(currentDate);
        const firstDay = getFirstDayOfMonth(currentDate);
        const days = [];

        // Empty cells for previous month
        for (let i = 0; i < firstDay; i++) {
            days.push(<div key={`empty-${i}`} className="day-cell empty"></div>);
        }

        // Days
        const today = new Date();
        const isCurrentMonth = today.getMonth() === currentDate.getMonth() && today.getFullYear() === currentDate.getFullYear();

        for (let day = 1; day <= daysInMonth; day++) {
            const events = getEventsForDay(day);
            const isToday = isCurrentMonth && day === today.getDate();

            days.push(
                <div key={day} className={`day-cell ${isToday ? 'today' : ''} ${events.length > 0 ? 'has-events' : ''}`}>
                    <span className="day-number">{day}</span>
                    <div className="day-events">
                        {events.map((event, idx) => (
                            <div
                                key={idx}
                                className={`event-bar event-type-${event.type}`}
                                title={`${event.title} (${event.start_formatted} - ${event.end_formatted})`}
                            >
                                {event.title}
                            </div>
                        ))}
                    </div>
                </div>
            );
        }

        return days;
    };

    const months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"];
    const daysOfWeek = ["Pts", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"];

    return (
        <div className="calendar-card">
            <div className="card-header" onClick={() => setIsOpen(!isOpen)}>
                <h2>📅 Akademik Takvim</h2>
                <span className={`toggle-icon ${isOpen ? 'open' : ''}`}>▼</span>
            </div>

            <div className={`card-content ${isOpen ? 'open' : ''}`}>
                {/* Seçiciler */}
                <div className="selectors-container">
                    <div className="selector-group">
                        <label>Birim Seçiniz:</label>
                        <select
                            value={selectedMain}
                            onChange={(e) => setSelectedMain(e.target.value)}
                            className="unit-select"
                            onClick={(e) => e.stopPropagation()}
                        >
                            {mainTypes.map(t => (
                                <option key={t.id} value={t.id}>{t.name}</option>
                            ))}
                        </select>
                    </div>

                    {/* Alt Seçici (Varsa) */}
                    {mainTypes.find(t => t.id === selectedMain)?.has_sub && (
                        <div className="selector-group">
                            <label>Dönem Seçiniz:</label>
                            <select
                                value={selectedSub}
                                onChange={(e) => setSelectedSub(e.target.value)}
                                className="unit-select"
                                onClick={(e) => e.stopPropagation()}
                            >
                                {subTypes[selectedMain]?.map(t => (
                                    <option key={t.id} value={t.id}>{t.name}</option>
                                ))}
                            </select>
                        </div>
                    )}
                </div>

                {loading ? (
                    <div className="loading">Yükleniyor...</div>
                ) : (
                    <div className="calendar-grid-view">
                        {/* Navigasyon */}
                        <div className="calendar-nav">
                            <button onClick={() => changeMonth(-1)}>❮</button>
                            <span className="current-month">
                                {months[currentDate.getMonth()]} {currentDate.getFullYear()}
                            </span>
                            <button onClick={() => changeMonth(1)}>❯</button>
                        </div>

                        {/* Gün İsimleri */}
                        <div className="days-header">
                            {daysOfWeek.map(d => <span key={d}>{d}</span>)}
                        </div>

                        {/* Günler Grid */}
                        <div className="days-grid">
                            {renderCalendarGrid()}
                        </div>

                        {/* Legend */}
                        <div className="calendar-legend">
                            <div className="legend-item">
                                <span className="legend-color event-type-registration"></span> Kayıt/Seçim
                            </div>
                            <div className="legend-item">
                                <span className="legend-color event-type-term"></span> Ders Dönemi
                            </div>
                            <div className="legend-item">
                                <span className="legend-color event-type-exam"></span> Sınav
                            </div>
                            <div className="legend-item">
                                <span className="legend-color event-type-holiday"></span> Tatil
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
