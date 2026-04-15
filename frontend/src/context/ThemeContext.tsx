import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

type Theme = 'light' | 'dark';
type ThemePreference = Theme | 'system';

interface ThemeContextType {
    theme: Theme;
    toggleTheme: () => void;
    setThemeMode: (mode: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const THEME_PREF_KEY = 'themePreference';
const LEGACY_THEME_KEY = 'theme';

const getSystemTheme = (): Theme => {
    if (typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    return 'light';
};

const resolveTheme = (preference: ThemePreference): Theme => {
    return preference === 'system' ? getSystemTheme() : preference;
};

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
    const [preference, setPreference] = useState<ThemePreference>(() => {
        const savedPreference = localStorage.getItem(THEME_PREF_KEY);
        if (savedPreference === 'light' || savedPreference === 'dark' || savedPreference === 'system') {
            return savedPreference;
        }

        // Eski sürüm uyumluluğu: daha önce kaydedilmiş manuel tema
        const legacy = localStorage.getItem(LEGACY_THEME_KEY);
        if (legacy === 'light' || legacy === 'dark') {
            return legacy;
        }

        return 'system';
    });

    const [theme, setTheme] = useState<Theme>(() => resolveTheme(preference));

    useEffect(() => {
        setTheme(resolveTheme(preference));
    }, [preference]);

    useEffect(() => {
        if (preference !== 'system') return;

        const media = window.matchMedia('(prefers-color-scheme: dark)');
        const onChange = () => setTheme(media.matches ? 'dark' : 'light');

        media.addEventListener('change', onChange);
        return () => media.removeEventListener('change', onChange);
    }, [preference]);

    useEffect(() => {
        // Seçilen tema tercihinin kalıcı olması için her zaman sakla.
        localStorage.setItem(THEME_PREF_KEY, preference);

        // Geriye dönük destek: eski anahtar sadece manuel light/dark için tutulur.
        if (preference === 'light' || preference === 'dark') {
            localStorage.setItem(LEGACY_THEME_KEY, preference);
        } else {
            localStorage.removeItem(LEGACY_THEME_KEY);
        }

        document.documentElement.setAttribute('data-theme', theme);
    }, [theme, preference]);

    const toggleTheme = () => {
        setPreference(prev => {
            if (prev === 'system') {
                return theme === 'light' ? 'dark' : 'light';
            }
            return prev === 'light' ? 'dark' : 'light';
        });
    };

    const setThemeMode = (mode: Theme) => {
        setPreference(mode);
    };

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme, setThemeMode }}>
            {children}
        </ThemeContext.Provider>
    );
};

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within ThemeProvider');
    }
    return context;
};
