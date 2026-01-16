import { useTheme } from '../context/ThemeContext';
import '../styles/ThemeToggle.css';

export const ThemeToggle = () => {
    const { theme, toggleTheme } = useTheme();

    return (
        <button
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={theme === 'light' ? 'Koyu moda geç' : 'Açık moda geç'}
        >
            {theme === 'light' ? '🌙' : '☀️'}
        </button>
    );
};
