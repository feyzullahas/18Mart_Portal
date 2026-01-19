import { useState, useEffect } from 'react';
import '../styles/Meals.css';

interface MealItem {
    name: string;
    calories?: number;
}

interface KykDay {
    date: string;
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

export const Meals = () => {
    const [activeTab, setActiveTab] = useState<'osem' | 'kyk'>('osem');
    const [kykData, setKykData] = useState<KykDay[]>([]);
    const [osemData, setOsemData] = useState<OsemDay[]>([]);
    const [selectedOsemIndex, setSelectedOsemIndex] = useState(0);
    const [selectedKykIndex, setSelectedKykIndex] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isOpen, setIsOpen] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                const [osemRes, kykRes] = await Promise.all([
                    fetch('http://127.0.0.1:8000/meals/osem'),
                    fetch('http://127.0.0.1:8000/meals/kyk')
                ]);
                const osem = await osemRes.json();
                const kyk = await kykRes.json();
                setOsemData(osem);
                setKykData(kyk);

                // Bugünü bul ve seç (ÖSEM)
                const todayOsemIdx = osem.findIndex((d: OsemDay) => d.isToday);
                if (todayOsemIdx >= 0) setSelectedOsemIndex(todayOsemIdx);

                // Bugünü bul ve seç (KYK)
                const todayKykIdx = kyk.findIndex((d: KykDay) => d.isToday);
                if (todayKykIdx >= 0) setSelectedKykIndex(todayKykIdx);
            } catch (err) {
                setError('Yemek verileri çekilemedi');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const currentOsemDay = osemData[selectedOsemIndex];
    const currentKykDay = kykData[selectedKykIndex];

    // ÖSEM navigasyon
    const goToPrevOsem = () => {
        setSelectedOsemIndex(selectedOsemIndex > 0 ? selectedOsemIndex - 1 : osemData.length - 1);
    };
    const goToNextOsem = () => {
        setSelectedOsemIndex(selectedOsemIndex < osemData.length - 1 ? selectedOsemIndex + 1 : 0);
    };

    // KYK navigasyon
    const goToPrevKyk = () => {
        setSelectedKykIndex(selectedKykIndex > 0 ? selectedKykIndex - 1 : kykData.length - 1);
    };
    const goToNextKyk = () => {
        setSelectedKykIndex(selectedKykIndex < kykData.length - 1 ? selectedKykIndex + 1 : 0);
    };

    return (
        <div className="meals-card">
            <div className="card-header" onClick={() => setIsOpen(!isOpen)}>
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
                        🏫 ÖSEM (Üniversite)
                    </button>
                    <button
                        className={activeTab === 'kyk' ? 'active' : ''}
                        onClick={() => setActiveTab('kyk')}
                    >
                        🏠 KYK (Yurt)
                    </button>
                </div>

                {/* İçerik */}
                {loading ? (
                    <div className="loading-indicator">
                        <div className="loading-spinner"></div>
                        <p>Menü getiriliyor...</p>
                    </div>
                ) : error ? (
                    <div className="error-message">{error}</div>
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
                            <h3>🍽️ Öğle Yemeği</h3>
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
                                <h3>☀️ Kahvaltı</h3>
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
                                <h3>🌙 Akşam Yemeği</h3>
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
