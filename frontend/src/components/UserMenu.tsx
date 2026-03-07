import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import '../styles/UserMenu.css';

export const UserMenu = () => {
    const [isOpen, setIsOpen] = useState(false);
    const { user, logout } = useAuth();

    const handleLogout = () => {
        logout();
        setIsOpen(false);
    };

    if (!user) return null;

    return (
        <div className="user-menu">
            <button 
                className="user-button"
                onClick={() => setIsOpen(!isOpen)}
            >
                <div className="user-avatar">
                    {user.email.charAt(0).toUpperCase()}
                </div>
                <span className="user-email">{user.email}</span>
                <span className={`dropdown-icon ${isOpen ? 'open' : ''}`}>▼</span>
            </button>

            {isOpen && (
                <div className="dropdown-menu">
                    <div className="user-info">
                        <div className="user-avatar-large">
                            {user.email.charAt(0).toUpperCase()}
                        </div>
                        <div className="user-details">
                            <p className="user-email-large">{user.email}</p>
                            <p className="user-role">Öğrenci</p>
                        </div>
                    </div>
                    
                    <div className="menu-divider"></div>
                    
                    <button className="menu-item logout-item" onClick={handleLogout}>
                        Çıkış Yap
                    </button>
                </div>
            )}
        </div>
    );
};
