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
import './App.css';

const AppContent = () => {
    const { user, isLoading } = useAuth();

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
                        <div className="header-user">
                            <UserMenu />
                        </div>
                    </header>

                    {/* Dashboard Cards */}
                    <main className="app-main">
                        <div className="widget-wrapper weather-widget mobile-only-weather">
                            <Weather />
                        </div>
                        <div className="widget-wrapper meals-widget">
                            <Meals />
                        </div>
                        <div className="widget-wrapper schedule-widget">
                            <Schedule />
                        </div>
                        <div className="widget-wrapper calendar-widget">
                            <Calendar />
                        </div>
                        <div className="widget-wrapper bus-widget">
                            <Bus />
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
