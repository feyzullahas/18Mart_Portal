import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import '../styles/UserMenu.css';

export const UserMenu = ({ onOpenProfile, onOpenLogin }: { onOpenProfile?: () => void; onOpenLogin?: () => void }) => {
    const [isOpen, setIsOpen] = useState(false);
    const { user } = useAuth();
    const { theme, setThemeMode } = useTheme();

    const handleOpenProfile = () => {
        onOpenProfile?.();
        setIsOpen(false);
    };

    const handleOpenLogin = () => {
        onOpenLogin?.();
        setIsOpen(false);
    };

    return (
        <div className="user-menu">
            <button
                className="user-button"
                onClick={() => setIsOpen(!isOpen)}
                aria-label="Menüyü aç"
            >
                <span className="hamburger-icon">☰</span>
            </button>

            {isOpen && (
                <div className="dropdown-menu">
                    <div className="menu-theme-row">
                        <div className="menu-theme-switch" role="radiogroup" aria-label="Tema modu">
                            <button
                                type="button"
                                role="radio"
                                aria-checked={theme === 'light'}
                                className={`menu-theme-option ${theme === 'light' ? 'active' : ''}`}
                                onClick={() => setThemeMode('light')}
                            >
                                Light
                            </button>
                            <button
                                type="button"
                                role="radio"
                                aria-checked={theme === 'dark'}
                                className={`menu-theme-option ${theme === 'dark' ? 'active' : ''}`}
                                onClick={() => setThemeMode('dark')}
                            >
                                Dark
                            </button>
                        </div>
                    </div>

                    <div className="menu-divider"></div>

                    {user ? (
                        <button className="menu-item" onClick={handleOpenProfile}>
                            Profilim
                        </button>
                    ) : (
                        <button className="menu-item" onClick={handleOpenLogin}>
                            Giriş Yap
                        </button>
                    )}
                </div>
            )}
        </div>
    );
};
