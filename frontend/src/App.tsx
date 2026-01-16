import { ThemeProvider } from './context/ThemeContext';
import { ThemeToggle } from './components/ThemeToggle';
import { Weather } from './components/Weather';
import { Meals } from './components/Meals';
import { Bus } from './components/Bus';
import { Calendar } from './components/Calendar';
import './App.css';

function App() {
    return (
        <ThemeProvider>
            <div className="app">
                <div className="app-container">
                    {/* Header */}
                    <header className="app-header">
                        <img src="/favicon.png" alt="18Mart Portal" className="header-logo" />
                        <h1 className="header-title">18Mart Portal</h1>
                        <p className="header-subtitle">Çanakkale Onsekiz Mart Üniversitesi Öğrenci Portalı</p>
                    </header>

                    {/* Dashboard Cards */}
                    <main className="app-main">
                        <Weather />
                        <Meals />
                        <Bus />
                        <Calendar />
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
