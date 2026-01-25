import { useState, useRef, useEffect } from 'react';
import '../styles/Schedule.css';

interface Course {
    id: number;
    user_id: number;
    name: string;
    code: string;
    day: string;
    start_time: string;
    end_time: string;
    location: string;
    instructor: string;
    created_at: string;
    updated_at: string;
}

interface Subject {
    id: string;
    name: string;
    time: string;
    location?: string;
}

interface DaySchedule {
    [key: string]: Subject[];
}

const API_BASE_URL = 'http://localhost:8000';

export const Schedule = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [schedule, setSchedule] = useState<DaySchedule>({
        'Pazartesi': [],
        'Salı': [],
        'Çarşamba': [],
        'Perşembe': [],
        'Cuma': []
    });
    const [newSubject, setNewSubject] = useState({ 
        name: '', 
        start_time: '', 
        end_time: '',
        location: '',
        day: ''
    });
    const [selectedDay, setSelectedDay] = useState('');
    const [currentDayIndex, setCurrentDayIndex] = useState(0);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const scrollContainerRef = useRef<HTMLDivElement>(null);

    const days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma'];
    const dayMapping: { [key: string]: string } = {
        'Pazartesi': 'Monday',
        'Salı': 'Tuesday',
        'Çarşamba': 'Wednesday',
        'Perşembe': 'Thursday',
        'Cuma': 'Friday'
    };

    // Get auth token
    const getAuthToken = () => {
        return localStorage.getItem('token');
    };

    // Load user's courses
    const loadCourses = async () => {
        try {
            const token = getAuthToken();
            if (!token) {
                setError('Oturum açmanız gerekiyor');
                return;
            }

            const response = await fetch(`${API_BASE_URL}/courses/`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Courses API Error:', response.status, errorText);
                throw new Error(`Dersler yüklenemedi (${response.status}): ${errorText}`);
            }

            const courses: Course[] = await response.json();
            
            // Convert courses to schedule format
            const newSchedule: DaySchedule = {
                'Pazartesi': [],
                'Salı': [],
                'Çarşamba': [],
                'Perşembe': [],
                'Cuma': []
            };

            courses.forEach(course => {
                const dayTr = Object.keys(dayMapping).find(key => dayMapping[key] === course.day);
                if (dayTr) {
                    const subject: Subject = {
                        id: course.id.toString(),
                        name: course.name,
                        time: `${course.start_time}-${course.end_time}`,
                        location: course.location
                    };
                    newSchedule[dayTr].push(subject);
                }
            });

            // Sort by time
            Object.keys(newSchedule).forEach(day => {
                newSchedule[day].sort((a, b) => a.time.localeCompare(b.time));
            });

            setSchedule(newSchedule);
        } catch (err) {
            console.error('Load courses error:', err);
            setError(`Dersler yüklenirken hata oluştu: ${err instanceof Error ? err.message : 'Bilinmeyen hata'}`);
        }
    };

    // Add new course
    const addSubject = async (day: string) => {
        if (!newSubject.name || !newSubject.start_time || !newSubject.end_time) {
            setError('Ders adı, başlangıç ve bitiş saati zorunludur');
            return;
        }

        setIsLoading(true);
        setError('');

        try {
            const token = getAuthToken();
            if (!token) {
                setError('Oturum açmanız gerekiyor');
                return;
            }

            const courseData = {
                name: newSubject.name,
                code: '', // Empty string for backend compatibility
                day: dayMapping[day],
                start_time: newSubject.start_time,
                end_time: newSubject.end_time,
                location: newSubject.location || '',
                instructor: '' // Empty string for backend compatibility
            };

            const response = await fetch(`${API_BASE_URL}/courses/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(courseData),
            });

            if (!response.ok) {
                throw new Error('Ders eklenemedi');
            }

            // Reset form and reload courses
            setNewSubject({ 
                name: '', 
                start_time: '', 
                end_time: '',
                location: '',
                day: ''
            });
            setSelectedDay('');
            await loadCourses();

        } catch (err) {
            setError('Ders eklenirken hata oluştu');
            console.error('Error adding course:', err);
        } finally {
            setIsLoading(false);
        }
    };

    // Remove course
    const removeSubject = async (_day: string, subjectId: string) => {
        setIsLoading(true);
        setError('');

        try {
            const token = getAuthToken();
            if (!token) {
                setError('Oturum açmanız gerekiyor');
                return;
            }

            const response = await fetch(`${API_BASE_URL}/courses/${subjectId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error('Ders silinemedi');
            }

            await loadCourses();

        } catch (err) {
            setError('Ders silinirken hata oluştu');
            console.error('Error removing course:', err);
        } finally {
            setIsLoading(false);
        }
    };

    // Load courses on component mount - always load when user is authenticated
    useEffect(() => {
        const token = getAuthToken();
        if (token) {
            loadCourses();
        }
    }, []);

    // Also reload when opened to refresh data
    useEffect(() => {
        if (isOpen) {
            loadCourses();
        }
    }, [isOpen]);

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
                {error && (
                    <div className="error-message" style={{ 
                        backgroundColor: '#fee', 
                        color: '#c00', 
                        padding: '10px', 
                        borderRadius: '5px', 
                        marginBottom: '10px' 
                    }}>
                        {error}
                    </div>
                )}
                
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
                                                    {subject.location && <span className="subject-location">📍 {subject.location}</span>}
                                                </div>
                                                <button 
                                                    className="remove-btn"
                                                    onClick={() => removeSubject(day, subject.id)}
                                                    disabled={isLoading}
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
                                                    disabled={isLoading}
                                                />
                                                <input
                                                    type="time"
                                                    value={newSubject.start_time}
                                                    onChange={(e) => setNewSubject(prev => ({ ...prev, start_time: e.target.value }))}
                                                    className="subject-input-field"
                                                    disabled={isLoading}
                                                />
                                                <input
                                                    type="time"
                                                    value={newSubject.end_time}
                                                    onChange={(e) => setNewSubject(prev => ({ ...prev, end_time: e.target.value }))}
                                                    className="subject-input-field"
                                                    disabled={isLoading}
                                                />
                                                <input
                                                    type="text"
                                                    placeholder="Mekan"
                                                    value={newSubject.location}
                                                    onChange={(e) => setNewSubject(prev => ({ ...prev, location: e.target.value }))}
                                                    className="subject-input-field"
                                                    disabled={isLoading}
                                                />
                                                <div className="input-buttons">
                                                    <button 
                                                        onClick={() => addSubject(day)}
                                                        className="add-btn"
                                                        disabled={isLoading}
                                                    >
                                                        {isLoading ? 'Ekleniyor...' : 'Ekle'}
                                                    </button>
                                                    <button 
                                                        onClick={() => {
                                                            setSelectedDay('');
                                                            setNewSubject({ 
                                                                name: '', 
                                                                start_time: '', 
                                                                end_time: '',
                                                                location: '',
                                                                day: ''
                                                            });
                                                        }}
                                                        className="cancel-btn"
                                                        disabled={isLoading}
                                                    >
                                                        İptal
                                                    </button>
                                                </div>
                                            </div>
                                        ) : (
                                            <button 
                                                onClick={() => setSelectedDay(day)}
                                                className="add-subject-btn"
                                                disabled={isLoading}
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
