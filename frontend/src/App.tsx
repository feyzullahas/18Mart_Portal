import { useState } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeToggle } from './components/ThemeToggle';
import { Weather } from './components/Weather';
import { Meals } from './components/Meals';
import { Bus } from './components/Bus';
import { Calendar } from './components/Calendar';
import { Schedule } from './components/Schedule';
import { Auth } from './components/Auth';
import { UserMenu } from './components/UserMenu';
import { ExamCountdown } from './components/ExamCountdown';
import './App.css';

const AppContent = () => {
    const { user, isLoading } = useAuth();
    const [openCard, setOpenCard] = useState<string | null>(null);
    const makeToggle = (id: string) => () => setOpenCard(prev => prev === id ? null : id);

    if (isLoading) {
        return (
            <div className="app">
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Yükleniyor...</p>
                </div>
            </div>
        );
    }

    if (!user) {
        return <Auth />;
    }

    return (
        <ThemeProvider>
            <div className="app">
                <div className="app-container">
                    {/* Header */}
                    <header className="app-header">
                        <img src="/favicon.png" alt="18 Mart Portal" className="header-logo" />
                        <div className="header-content">
                            <h1 className="header-title">18 Mart Portal</h1>
                            <p className="header-subtitle">Çanakkale Onsekiz Mart Üniversitesi Öğrenci Portalı</p>
                        </div>
                        <div className="header-weather">
                            <Weather variant="header" />
                        </div>
                        <div className="header-exam-countdown">
                            <ExamCountdown variant="header" />
                        </div>
                        <div className="header-user">
                            <UserMenu />
                        </div>
                    </header>

                    {/* Dashboard Cards */}
                    <main className="app-main">
                        <div className="widget-wrapper weather-widget mobile-only-weather">
                            <Weather isOpen={openCard === 'weather'} onToggle={makeToggle('weather')} />
                        </div>
                        <div className="widget-wrapper exam-countdown-widget">
                            <ExamCountdown isOpen={openCard === 'exam'} onToggle={makeToggle('exam')} />
                        </div>
                        <div className="widget-wrapper meals-widget">
                            <Meals isOpen={openCard === 'meals'} onToggle={makeToggle('meals')} />
                        </div>
                        <div className="widget-wrapper schedule-widget">
                            <Schedule isOpen={openCard === 'schedule'} onToggle={makeToggle('schedule')} />
                        </div>
                        <div className="widget-wrapper calendar-widget">
                            <Calendar isOpen={openCard === 'calendar'} onToggle={makeToggle('calendar')} />
                        </div>
                        <div className="widget-wrapper bus-widget">
                            <Bus isOpen={openCard === 'bus'} onToggle={makeToggle('bus')} />
                        </div>
                    </main>

                    {/* Footer */}
                    <footer className="app-footer">
                        <p className="footer-copyright">© 2026 18 Mart Portal - Tüm Hakları Saklıdır</p>
                        <p className="footer-info">Versiyon 1.0 | Çanakkale Onsekiz Mart Üniversitesi için geliştirilmiştir</p>
                    </footer>
                </div>

                {/* Theme Toggle Button */}
                <ThemeToggle />
            </div>
        </ThemeProvider>
    );
};

function App() {
    return (
        <AuthProvider>
            <AppContent />
        </AuthProvider>
    );
}

export default App;
