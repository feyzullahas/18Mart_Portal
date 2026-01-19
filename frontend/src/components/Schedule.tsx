import { useState, useRef } from 'react';
import '../styles/Schedule.css';

interface Subject {
    id: string;
    name: string;
    time: string;
}

interface DaySchedule {
    [key: string]: Subject[];
}

export const Schedule = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [schedule, setSchedule] = useState<DaySchedule>({
        'Pazartesi': [],
        'Salı': [],
        'Çarşamba': [],
        'Perşembe': [],
        'Cuma': []
    });
    const [newSubject, setNewSubject] = useState({ name: '', time: '' });
    const [selectedDay, setSelectedDay] = useState('');
    const [currentDayIndex, setCurrentDayIndex] = useState(0);
    const scrollContainerRef = useRef<HTMLDivElement>(null);

    const days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma'];

    const addSubject = (day: string) => {
        if (newSubject.name && newSubject.time) {
            const subject: Subject = {
                id: Date.now().toString(),
                name: newSubject.name,
                time: newSubject.time
            };
            
            setSchedule(prev => ({
                ...prev,
                [day]: [...prev[day], subject]
            }));
            
            setNewSubject({ name: '', time: '' });
            setSelectedDay('');
        }
    };

    const removeSubject = (day: string, subjectId: string) => {
        setSchedule(prev => ({
            ...prev,
            [day]: prev[day].filter(subject => subject.id !== subjectId)
        }));
    };

    const navigateDay = (direction: 'prev' | 'next') => {
        const newIndex = direction === 'prev' 
            ? Math.max(0, currentDayIndex - 1)
            : Math.min(days.length - 1, currentDayIndex + 1);
        
        setCurrentDayIndex(newIndex);
        
        if (scrollContainerRef.current) {
            const dayWidth = scrollContainerRef.current.scrollWidth / days.length;
            scrollContainerRef.current.scrollTo({
                left: dayWidth * newIndex,
                behavior: 'smooth'
            });
        }
    };

    const goToDay = (index: number) => {
        setCurrentDayIndex(index);
        if (scrollContainerRef.current) {
            const dayWidth = scrollContainerRef.current.scrollWidth / days.length;
            scrollContainerRef.current.scrollTo({
                left: dayWidth * index,
                behavior: 'smooth'
            });
        }
    };

    return (
        <div className="schedule-card">
            <div className="card-header" onClick={() => setIsOpen(!isOpen)}>
                <h2>📚 Ders Programı</h2>
                <span className={`toggle-icon ${isOpen ? 'open' : ''}`}>▼</span>
            </div>

            <div className={`card-content ${isOpen ? 'open' : ''}`}>
                <div className="schedule-container">
                    {/* Navigation Controls */}
                    <div className="schedule-navigation">
                        <button 
                            className="nav-btn prev-btn"
                            onClick={() => navigateDay('prev')}
                            disabled={currentDayIndex === 0}
                        >
                            ‹
                        </button>
                        
                        <div className="day-indicators">
                            {days.map((day, index) => (
                                <button
                                    key={day}
                                    className={`day-indicator ${index === currentDayIndex ? 'active' : ''}`}
                                    onClick={() => goToDay(index)}
                                >
                                    {day.charAt(0)}
                                </button>
                            ))}
                        </div>
                        
                        <button 
                            className="nav-btn next-btn"
                            onClick={() => navigateDay('next')}
                            disabled={currentDayIndex === days.length - 1}
                        >
                            ›
                        </button>
                    </div>

                    {/* Scrollable Days Container */}
                    <div className="schedule-scroll-container" ref={scrollContainerRef}>
                        <div className="schedule-grid-horizontal">
                            {days.map(day => (
                                <div key={day} className="day-column-horizontal">
                                    <h3 className="day-header">{day}</h3>
                                    <div className="subjects-list">
                                        {schedule[day].map(subject => (
                                            <div key={subject.id} className="subject-item">
                                                <div className="subject-info">
                                                    <span className="subject-time">{subject.time}</span>
                                                    <span className="subject-name">{subject.name}</span>
                                                </div>
                                                <button 
                                                    className="remove-btn"
                                                    onClick={() => removeSubject(day, subject.id)}
                                                >
                                                    ✕
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="add-subject-section">
                                        {selectedDay === day ? (
                                            <div className="subject-input">
                                                <input
                                                    type="text"
                                                    placeholder="Ders adı"
                                                    value={newSubject.name}
                                                    onChange={(e) => setNewSubject(prev => ({ ...prev, name: e.target.value }))}
                                                    className="subject-input-field"
                                                />
                                                <input
                                                    type="text"
                                                    placeholder="Saat (09:00-10:00)"
                                                    value={newSubject.time}
                                                    onChange={(e) => setNewSubject(prev => ({ ...prev, time: e.target.value }))}
                                                    className="subject-input-field"
                                                />
                                                <div className="input-buttons">
                                                    <button 
                                                        onClick={() => addSubject(day)}
                                                        className="add-btn"
                                                    >
                                                        Ekle
                                                    </button>
                                                    <button 
                                                        onClick={() => {
                                                            setSelectedDay('');
                                                            setNewSubject({ name: '', time: '' });
                                                        }}
                                                        className="cancel-btn"
                                                    >
                                                        İptal
                                                    </button>
                                                </div>
                                            </div>
                                        ) : (
                                            <button 
                                                onClick={() => setSelectedDay(day)}
                                                className="add-subject-btn"
                                            >
                                                + Ders Ekle
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
