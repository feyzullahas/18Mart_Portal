import { ThemeProvider } from './context/ThemeContext';
import { ThemeToggle } from './components/ThemeToggle';
import { Weather } from './components/Weather';
import { Meals } from './components/Meals';
import { Bus } from './components/Bus';
import { Calendar } from './components/Calendar';
import { Schedule } from './components/Schedule';
import './App.css';

function App() {
    return (
        <ThemeProvider>
            <div className="app">
                <div className="app-container">
                    {/* Header */}
                    <header className="app-header">
                        <img src="/favicon.png" alt="18Mart Portal" className="header-logo" />
                        <div className="header-content">
                            <h1 className="header-title">18Mart Portal</h1>
                            <p className="header-subtitle">Çanakkale Onsekiz Mart Üniversitesi Öğrenci Portalı</p>
                        </div>
                        <div className="header-weather">
                            <Weather variant="header" />
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
                        <p className="footer-copyright">© 2026 18Mart Portal - Tüm Hakları Saklıdır</p>
                        <p className="footer-info">Versiyon 1.0 | Çanakkale Onsekiz Mart Üniversitesi için geliştirilmiştir</p>
                    </footer>
                </div>

                {/* Theme Toggle Button */}
                <ThemeToggle />
            </div>
        </ThemeProvider>
    );
}

export default App;
