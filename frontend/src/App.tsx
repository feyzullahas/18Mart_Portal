import { useEffect, useState } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Weather } from './components/Weather';
import { Meals } from './components/Meals';
import { Bus } from './components/Bus';
import { Calendar } from './components/Calendar';
import { Schedule } from './components/Schedule';
import { Auth } from './components/Auth';
import { ExamCountdown } from './components/ExamCountdown';
import { InstallPrompt } from './components/InstallPrompt';
import './App.css';

const AppContent = () => {
    const { user, isLoading, logout } = useAuth();
    const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

    useEffect(() => {
        if (user && isAuthModalOpen) {
            setIsAuthModalOpen(false);
        }
    }, [user, isAuthModalOpen]);

    if (isLoading) {
        return (
            <div className="portal-app portal-app-loading">
                <div className="portal-loading-container">
                    <div className="loading-spinner"></div>
                    <p>Yükleniyor...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="portal-app">
            <header className="portal-navbar">
                <div className="portal-brand">
                    <img src="/favicon.png" alt="18 Mart Portal" className="portal-logo" />
                    <div>
                        <h1>18 Mart Portal</h1>
                        <p>Campus Dashboard</p>
                    </div>
                </div>

                <nav className="portal-nav" aria-label="Ana gezinme">
                    <a href="#weather">Hava</a>
                    <a href="#exam">Final</a>
                    <a href="#meals">Yemek</a>
                    <a href="#calendar">Takvim</a>
                    <a href="#bus">Otobüs</a>
                    <a href="#schedule">Ders Programı</a>
                </nav>

                <div className="portal-auth">
                    <div className="portal-navbar-countdown" aria-hidden="false">
                        <ExamCountdown variant="header" />
                    </div>
                    {user ? (
                        <button type="button" className="portal-auth-btn" onClick={logout}>
                            Çıkış Yap
                        </button>
                    ) : (
                        <button
                            type="button"
                            className="portal-auth-btn"
                            onClick={() => setIsAuthModalOpen(true)}
                        >
                            Giriş Yap
                        </button>
                    )}
                </div>
            </header>

            <main className="portal-main">
                <span id="exam" className="portal-anchor"></span>

                <section className="portal-grid portal-grid-main">
                    <article className="portal-panel portal-panel-weather" id="weather">
                        <h2>Hava Durumu</h2>
                        <Weather isOpen />
                    </article>

                    <article className="portal-panel portal-panel-exam" id="exam-mobile">
                        <h2>Vize Final Sayacı</h2>
                        <ExamCountdown isOpen />
                    </article>

                    <article className="portal-panel portal-panel-meals" id="meals">
                        <h2>Günün Yemek Menüsü</h2>
                        <Meals isOpen />
                    </article>

                    <article className="portal-panel portal-panel-calendar" id="calendar">
                        <h2>Akademik Takvim</h2>
                        <Calendar isOpen />
                    </article>

                    <article className="portal-panel portal-panel-bus" id="bus">
                        <h2>Otobüs Saatleri</h2>
                        <Bus isOpen />
                    </article>

                    <article className="portal-panel portal-panel-schedule" id="schedule">
                        <h2>Ders Programım</h2>
                        {user ? (
                            <Schedule isOpen />
                        ) : (
                            <div className="portal-locked-state" role="note" aria-label="Kilitle korunuyor">
                                <div className="portal-lock-icon" aria-hidden="true">🔒</div>
                                <p>Bu özelliği kullanmak için giriş yapın.</p>
                                <button
                                    type="button"
                                    className="portal-auth-btn portal-lock-action"
                                    onClick={() => setIsAuthModalOpen(true)}
                                >
                                    Giriş Yap
                                </button>
                            </div>
                        )}
                    </article>
                </section>
            </main>

            <footer className="portal-footer">
                <p>Yazılım Geliştirme Kulübü - 18 Mart Portal</p>
                <p>Çanakkale Onsekiz Mart Üniversitesi</p>
            </footer>

            <InstallPrompt />

            {isAuthModalOpen && (
                <div className="auth-modal-overlay" role="dialog" aria-modal="true" aria-label="Giriş ekranı">
                    <div className="auth-modal">
                        <Auth embedded onClose={() => setIsAuthModalOpen(false)} />
                    </div>
                </div>
            )}
        </div>
    );
};

function App() {
    return (
        <ThemeProvider>
            <AuthProvider>
                <AppContent />
            </AuthProvider>
        </ThemeProvider>
    );
}

export default App;
