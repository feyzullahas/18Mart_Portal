import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import '../styles/UserMenu.css';

export const UserMenu = ({ onOpenProfile }: { onOpenProfile?: () => void }) => {
    const [isOpen, setIsOpen] = useState(false);
    const { user, logout } = useAuth();
    const displayName = user?.fullName?.trim() || 'Çomülü';
    const avatarChar = displayName.charAt(0).toUpperCase();

    const handleLogout = () => {
        logout();
        setIsOpen(false);
    };

    if (!user) return null;

    return (
        <div className="user-menu">
            <button 
                className="user-button"
                onClick={() => {
                    if (onOpenProfile) {
                        onOpenProfile();
                        return;
                    }
                    setIsOpen(!isOpen);
                }}
            >
                <div className="user-avatar">
                    {avatarChar}
                </div>
                <span className="user-email">Profil</span>
            </button>

            {isOpen && (
                <div className="dropdown-menu">
                    <div className="user-info">
                        <div className="user-avatar-large">
                            {avatarChar}
                        </div>
                        <div className="user-details">
                            <p className="user-email-large">{displayName}</p>
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
