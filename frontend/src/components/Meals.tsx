import { useState, useEffect, useCallback } from 'react';
import '../styles/Meals.css';

interface MealItem {
    name: string;
    calories?: number;
}

interface KykDay {
    date: string;
    dateRaw?: string;
    breakfast: MealItem[];
    dinner: MealItem[];
    total_calories_breakfast?: number;
    total_calories_dinner?: number;
    isToday?: boolean;
}

interface OsemDay {
    date: string;
    dateRaw: string;
    menu: MealItem[];
    total_calories?: number;
    isToday?: boolean;
}

export const Meals = ({ isOpen: propIsOpen, onToggle }: { isOpen?: boolean; onToggle?: () => void } = {}) => {
    const [activeTab, setActiveTab] = useState<'osem' | 'kyk'>('osem');
    const [kykData, setKykData] = useState<KykDay[]>([]);
    const [osemData, setOsemData] = useState<OsemDay[]>([]);
    const [selectedOsemIndex, setSelectedOsemIndex] = useState(0);
    const [selectedKykIndex, setSelectedKykIndex] = useState(0);
    const [loadingOsem, setLoadingOsem] = useState(true);
    const [loadingKyk, setLoadingKyk] = useState(true);
    const [osemError, setOsemError] = useState<string | null>(null);
    const [kykError, setKykError] = useState<string | null>(null);
    const [localOpen, setLocalOpen] = useState(false);
    const isOpen = propIsOpen !== undefined ? propIsOpen : localOpen;
    const handleToggle = onToggle ?? (() => setLocalOpen(prev => !prev));

    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;
    const OSEM_CACHE_KEY = 'meals_osem_cache_v1';
    const KYK_CACHE_KEY = `meals_kyk_cache_v1_${year}_${month}`;

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

    const setCachedData = <T,>(key: string, data: T) => {
        // Gün sonuna kadar tut: gün içi hızlı açılış sağlar, ertesi gün otomatik yenilenir.
        const midnight = new Date();
        midnight.setHours(24, 0, 0, 0);
        const payload = {
            data,
            expiresAt: midnight.getTime(),
        };
        localStorage.setItem(key, JSON.stringify(payload));
    };

    const setDefaultOsemIndex = (osem: OsemDay[]) => {
        const todayOsemIdx = osem.findIndex((d) => d.isToday);
        if (todayOsemIdx >= 0) {
            setSelectedOsemIndex(todayOsemIdx);
            return;
        }

        // Haftasonu ise bir önceki Cuma'yı seç
        const currentDate = new Date();
        const dayOfWeek = currentDate.getDay();
        if (dayOfWeek === 6 || dayOfWeek === 0) {
            const daysToFriday = dayOfWeek === 6 ? 1 : 2;
            const friday = new Date(currentDate);
            friday.setDate(currentDate.getDate() - daysToFriday);
            const fridayStr = friday.toISOString().split('T')[0];
            const fridayIdx = osem.findIndex((d) => d.dateRaw === fridayStr);
            if (fridayIdx >= 0) setSelectedOsemIndex(fridayIdx);
        }
    };

    const setDefaultKykIndex = (kyk: KykDay[]) => {
        const todayKykIdx = kyk.findIndex((d) => d.isToday);
        if (todayKykIdx >= 0) setSelectedKykIndex(todayKykIdx);
    };

    const fetchOsemData = useCallback(async () => {
        const apiUrl = import.meta.env.VITE_API_URL || 'https://18-mart-portal-4orl.vercel.app';
        const res = await fetch(`${apiUrl}/meals/osem`);
        if (!res.ok) throw new Error('ÖSEM verisi alınamadı');
        return res.json();
    }, []);

    const fetchKykData = useCallback(async () => {
        const now = new Date();
        const year = now.getFullYear();
        const month = now.getMonth() + 1;
        const apiUrl = import.meta.env.VITE_API_URL || 'https://18-mart-portal-4orl.vercel.app';
        const res = await fetch(`${apiUrl}/meals/kyk?year=${year}&month=${month}`);
        if (!res.ok) throw new Error('KYK verisi alınamadı');
        return res.json();
    }, []);

    useEffect(() => {
        // 1) Varsa cache'i anında göster
        const cachedOsem = getCachedData<OsemDay[]>(OSEM_CACHE_KEY);
        if (cachedOsem && cachedOsem.length > 0) {
            setOsemData(cachedOsem);
            setDefaultOsemIndex(cachedOsem);
            setLoadingOsem(false);
        }

        const cachedKyk = getCachedData<KykDay[]>(KYK_CACHE_KEY);
        if (cachedKyk && cachedKyk.length > 0) {
            setKykData(cachedKyk);
            setDefaultKykIndex(cachedKyk);
            setLoadingKyk(false);
        }

        // 2) Arka planda güncel veriyi çek (stale-while-revalidate)
        const refreshOsem = async () => {
            if (!cachedOsem) setLoadingOsem(true);
            setOsemError(null);
            try {
                const osem = await fetchOsemData();
                setOsemData(osem);
                setDefaultOsemIndex(osem);
                setCachedData(OSEM_CACHE_KEY, osem);
            } catch (err) {
                console.error(err);
                if (!cachedOsem) setOsemError('ÖSEM verisi çekilemedi');
            } finally {
                setLoadingOsem(false);
            }
        };

        const refreshKyk = async () => {
            if (!cachedKyk) setLoadingKyk(true);
            setKykError(null);
            try {
                const kyk = await fetchKykData();
                setKykData(kyk);
                setDefaultKykIndex(kyk);
                setCachedData(KYK_CACHE_KEY, kyk);
            } catch (err) {
                console.error(err);
                if (!cachedKyk) setKykError('KYK verisi çekilemedi');
            } finally {
                setLoadingKyk(false);
            }
        };

        void Promise.all([refreshOsem(), refreshKyk()]);
    }, [fetchOsemData, fetchKykData]);

    const currentOsemDay = osemData[selectedOsemIndex];
    const currentKykDay = kykData[selectedKykIndex];

    // ÖSEM navigasyon
    const goToPrevOsem = () => {
        setSelectedOsemIndex(selectedOsemIndex > 0 ? selectedOsemIndex - 1 : osemData.length - 1);
    };
    const goToNextOsem = () => {
        setSelectedOsemIndex(selectedOsemIndex < osemData.length - 1 ? selectedOsemIndex + 1 : 0);
    };

    // KYK gün navigasyon
    const goToPrevKyk = () => {
        setSelectedKykIndex(selectedKykIndex > 0 ? selectedKykIndex - 1 : kykData.length - 1);
    };
    const goToNextKyk = () => {
        setSelectedKykIndex(selectedKykIndex < kykData.length - 1 ? selectedKykIndex + 1 : 0);
    };

    return (
        <div className="meals-card">
            <div className="card-header" onClick={handleToggle}>
                <h2>🍴 Günün Yemek Menüsü</h2>
                <span className={`toggle-icon ${isOpen ? 'open' : ''}`}>▼</span>
            </div>

            <div className={`card-content ${isOpen ? 'open' : ''}`}>
                {/* Tab Seçici */}
                <div className="tab-container">
                    <button
                        className={activeTab === 'osem' ? 'active' : ''}
                        onClick={() => setActiveTab('osem')}
                    >
                        ÖSEM (Üniversite)
                    </button>
                    <button
                        className={activeTab === 'kyk' ? 'active' : ''}
                        onClick={() => setActiveTab('kyk')}
                    >
                        KYK (Yurt)
                    </button>
                </div>

                {/* İçerik */}
                {activeTab === 'osem' && loadingOsem && !currentOsemDay ? (
                    <div className="loading-indicator">
                        <div className="loading-spinner"></div>
                    </div>
                ) : activeTab === 'kyk' && loadingKyk && !currentKykDay ? (
                    <div className="loading-indicator">
                        <div className="loading-spinner"></div>
                    </div>
                ) : activeTab === 'osem' && osemError && !currentOsemDay ? (
                    <div className="error-message">{osemError}</div>
                ) : activeTab === 'kyk' && kykError && !currentKykDay ? (
                    <div className="error-message">{kykError}</div>
                ) : activeTab === 'osem' && currentOsemDay ? (
                    <div className="osem-section">
                        {/* Gün Seçici */}
                        <div className="day-navigator">
                            <button className="nav-btn" onClick={goToNextOsem}>◀</button>
                            <div className="day-info">
                                <span className="day-date">{currentOsemDay.date}</span>
                                {currentOsemDay.isToday && <span className="today-badge">Bugün</span>}
                            </div>
                            <button className="nav-btn" onClick={goToPrevOsem}>▶</button>
                        </div>

                        {/* Menü */}
                        <div className="meal-column single">
                            <h3>Öğle Yemeği</h3>
                            <div className="meal-items">
                                {currentOsemDay.menu.map((m, i) => (
                                    <div key={i} className="meal-row">
                                        <span className="meal-name">{m.name}</span>
                                        {m.calories && <span className="cal">{m.calories} kcal</span>}
                                    </div>
                                ))}
                            </div>
                            {currentOsemDay.total_calories && (
                                <div className="total-cal">Toplam: {currentOsemDay.total_calories} kcal</div>
                            )}
                            <a
                                href="https://odeme.comu.edu.tr/"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="osem-balance-btn"
                            >
                                Bakiye Yükle
                            </a>
                        </div>
                    </div>
                ) : activeTab === 'kyk' && currentKykDay ? (
                    <div className="kyk-section">
                        {/* Gün Seçici */}
                        <div className="day-navigator">
                            <button className="nav-btn" onClick={goToPrevKyk}>◀</button>
                            <div className="day-info">
                                <span className="day-date">{currentKykDay.date}</span>
                                {currentKykDay.isToday && <span className="today-badge">Bugün</span>}
                            </div>
                            <button className="nav-btn" onClick={goToNextKyk}>▶</button>
                        </div>

                        <div className="meal-grid">
                            {/* Kahvaltı */}
                            <div className="meal-column">
                                <h3>Kahvaltı</h3>
                                <div className="meal-items">
                                    {currentKykDay.breakfast.map((m, i) => (
                                        <div key={i} className="meal-row">
                                            <span className="meal-name">{m.name}</span>
                                            {m.calories && <span className="cal">{m.calories} kcal</span>}
                                        </div>
                                    ))}
                                </div>
                                {currentKykDay.total_calories_breakfast && (
                                    <div className="total-cal">Toplam: {currentKykDay.total_calories_breakfast} kcal</div>
                                )}
                            </div>

                            {/* Akşam */}
                            <div className="meal-column">
                                <h3>Akşam Yemeği</h3>
                                <div className="meal-items">
                                    {currentKykDay.dinner.map((m, i) => (
                                        <div key={i} className="meal-row">
                                            <span className="meal-name">{m.name}</span>
                                            {m.calories && <span className="cal">{m.calories} kcal</span>}
                                        </div>
                                    ))}
                                </div>
                                {currentKykDay.total_calories_dinner && (
                                    <div className="total-cal">Toplam: {currentKykDay.total_calories_dinner} kcal</div>
                                )}
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="error-message">Menü bulunamadı</div>
                )}
            </div>
        </div>
    );
};
