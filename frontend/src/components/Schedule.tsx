import { useState } from 'react';
import '../styles/Schedule.css';

export const Schedule = () => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div className="schedule-card">
            <div className="card-header" onClick={() => setIsOpen(!isOpen)}>
                <h2>📅 Ders Programı</h2>
                <span className={`toggle-icon ${isOpen ? 'open' : ''}`}>▼</span>
            </div>

            <div className={`card-content ${isOpen ? 'open' : ''}`}>
                <div className="schedule-placeholder">
                    <span className="placeholder-icon">🚧</span>
                    <p>Ders programı özelliği çok yakında eklenecektir.</p>
                </div>
            </div>
        </div>
    );
};
