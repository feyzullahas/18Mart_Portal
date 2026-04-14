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
import { UserMenu } from './components/UserMenu';
import { ProfileSettings } from './components/ProfileSettings';
import { weatherService } from './services/weatherService';
import { busService } from './services/busService';
import { FiHome, FiCalendar, FiBookOpen } from 'react-icons/fi';
import { MdRestaurantMenu } from 'react-icons/md';
import { FaBus } from 'react-icons/fa6';
import { type IconType } from 'react-icons';
import './App.css';

type PortalPage = 'home' | 'meals' | 'calendar' | 'bus' | 'schedule' | 'profile';

interface NavItem {
    key: PortalPage;
    label: string;
    title: string;
    icon: IconType;
}

const AppContent = () => {
    const { user, isLoading } = useAuth();
    const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
    const [activePage, setActivePage] = useState<PortalPage>('home');

    const navItems: NavItem[] = [
        { key: 'home', label: 'Ana Sayfa', title: 'Ana Sayfa', icon: FiHome },
        { key: 'meals', label: 'Yemek', title: 'Günün Yemek Menüsü', icon: MdRestaurantMenu },
        { key: 'bus', label: 'Otobüs', title: 'Otobüs Saatleri', icon: FaBus },
        { key: 'schedule', label: 'Program', title: 'Ders Programım', icon: FiBookOpen },
        { key: 'calendar', label: 'Takvim', title: 'Akademik Takvim', icon: FiCalendar }
    ];

    useEffect(() => {
        if (user && isAuthModalOpen) {
            setIsAuthModalOpen(false);
        }
    }, [user, isAuthModalOpen]);

    useEffect(() => {
        const getApiBaseUrl = () => {
            const envApiUrl = import.meta.env.VITE_API_URL;
            if (envApiUrl) {
                return envApiUrl.replace(/\/$/, '');
            }
            return import.meta.env.DEV ? 'http://localhost:8000' : 'https://18-mart-portal-4orl.vercel.app';
        };

        const getCachedData = <T,>(key: string): T | null => {
            try {
                const raw = localStorage.getItem(key);
                if (!raw) return null;
                const parsed = JSON.parse(raw) as { data: T; expiresAt: number };
                if (!parsed?.expiresAt || Date.now() > parsed.expiresAt) {
                    localStorage.removeItem(key);
                    return null;
                }
                return parsed.data;
            } catch {
                return null;
            }
        };

        const setDailyCache = <T,>(key: string, data: T) => {
            const midnight = new Date();
            midnight.setHours(24, 0, 0, 0);
            localStorage.setItem(
                key,
                JSON.stringify({
                    data,
                    expiresAt: midnight.getTime()
                })
            );
        };

        const prefetchMeals = async () => {
            const now = new Date();
            const year = now.getFullYear();
            const month = now.getMonth() + 1;
            const osemKey = 'meals_osem_cache_v1';
            const kykKey = `meals_kyk_cache_v1_${year}_${month}`;
            const apiUrl = getApiBaseUrl();

            const cachedOsem = getCachedData<unknown[]>(osemKey);
            const cachedKyk = getCachedData<unknown[]>(kykKey);

            const requests: Promise<void>[] = [];

            if (!cachedOsem) {
                requests.push(
                    fetch(`${apiUrl}/meals/osem`)
                        .then((res) => {
                            if (!res.ok) throw new Error('ÖSEM prefetch başarısız');
                            return res.json();
                        })
                        .then((data) => {
                            setDailyCache(osemKey, data);
                        })
                        .catch(() => {
                            // Sessiz geç: prefetch başarısızlığı UI'ı bloklamamalı.
                        })
                );
            }

            if (!cachedKyk) {
                requests.push(
                    fetch(`${apiUrl}/meals/kyk?year=${year}&month=${month}`)
                        .then((res) => {
                            if (!res.ok) throw new Error('KYK prefetch başarısız');
                            return res.json();
                        })
                        .then((data) => {
                            setDailyCache(kykKey, data);
                        })
                        .catch(() => {
                            // Sessiz geç: prefetch başarısızlığı UI'ı bloklamamalı.
                        })
                );
            }

            if (requests.length > 0) {
                await Promise.all(requests);
            }
        };

        void weatherService.prefetchDailyWeather();
        void busService.prefetchDailySchedule();
        void prefetchMeals();
    }, []);

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

    const renderActivePage = () => {
        switch (activePage) {
            case 'home':
                return {
                    title: '',
                    content: (
                        <>
                            <h1 className="portal-home-greeting">
                                Merhaba {user?.fullName?.trim()?.split(/\s+/)[0] || 'Çomülü'}!
                            </h1>
                            <div className="portal-home-sections">
                                <section className="portal-home-block">
                                    <h3>Hava Durumu</h3>
                                    <Weather isOpen />
                                </section>
                                <section className="portal-home-block">
                                    <h3>Finallere kalan gün sayısı</h3>
                                    <ExamCountdown isOpen />
                                </section>
                            </div>
                        </>
                    )
                };
            case 'meals':
                return { title: 'Günün Yemek Menüsü', content: <Meals isOpen /> };
            case 'calendar':
                return { title: 'Akademik Takvim', content: <Calendar isOpen /> };
            case 'bus':
                return { title: 'Otobüs Saatleri', content: <Bus isOpen /> };
            case 'schedule':
                return {
                    title: 'Ders Programım',
                    content: user ? (
                        <Schedule isOpen />
                    ) : (
                        <div className="portal-locked-state" role="note" aria-label="Kilitle korunuyor">
                            <p>Bu özelliği kullanmak için giriş yapın.</p>
                            <button
                                type="button"
                                className="portal-auth-btn portal-lock-action"
                                onClick={() => setIsAuthModalOpen(true)}
                            >
                                Giriş Yap
                            </button>
                        </div>
                    )
                };
            case 'profile':
                return {
                    title: '',
                    content: user ? <ProfileSettings /> : (
                        <div className="portal-locked-state" role="note" aria-label="Kilitle korunuyor">
                            <p>Bu özelliği kullanmak için giriş yapın.</p>
                            <button
                                type="button"
                                className="portal-auth-btn portal-lock-action"
                                onClick={() => setIsAuthModalOpen(true)}
                            >
                                Giriş Yap
                            </button>
                        </div>
                    )
                };
        }
    };

    const currentPage = renderActivePage();

    return (
        <div className="portal-app">
            <header className="portal-navbar">
                <div className="portal-brand">
                    <img src="/favicon.png" alt="18 Mart Portal" className="portal-logo" />
                    <div>
                        <h1>18 Mart Portal</h1>
                    </div>
                </div>

                <nav className="portal-nav" aria-label="Ana gezinme">
                    {navItems.map((item) => (
                        <button
                            key={item.key}
                            type="button"
                            className={`portal-nav-btn ${activePage === item.key ? 'active' : ''}`}
                            onClick={() => setActivePage(item.key)}
                        >
                            {item.label}
                        </button>
                    ))}
                </nav>

                <div className="portal-auth">
                    {user ? (
                        <UserMenu onOpenProfile={() => setActivePage('profile')} />
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
                <section className="portal-page-container">
                    <article className="portal-panel portal-panel-single">
                        {currentPage.title && <h2>{currentPage.title}</h2>}
                        {currentPage.content}
                    </article>
                </section>
            </main>

            <nav className="portal-bottom-nav" aria-label="Ana gezinme">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    return (
                        <button
                            key={item.key}
                            type="button"
                            className={`portal-bottom-nav-btn ${activePage === item.key ? 'active' : ''}`}
                            onClick={() => setActivePage(item.key)}
                            aria-label={item.title}
                        >
                            <Icon className="nav-icon" aria-hidden="true" />
                            <span className="nav-label">{item.label}</span>
                        </button>
                    );
                })}
            </nav>

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
