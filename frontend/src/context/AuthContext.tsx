import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

interface User {
    id: string;
    email: string;
    fullName?: string;
}

interface AuthContextType {
    user: User | null;
    login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
    register: (email: string, password: string, fullName?: string) => Promise<{ success: boolean; error?: string }>;
    logout: () => void;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

interface AuthProviderProps {
    children: ReactNode;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV
    ? 'http://127.0.0.1:8000'
    : 'https://18-mart-portal-4orl.vercel.app');

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    const getSavedProfileNames = (): Record<string, string> => {
        try {
            return JSON.parse(localStorage.getItem('profileNames') || '{}');
        } catch {
            return {};
        }
    };

    const saveProfileName = (email: string, fullName: string) => {
        const profileNames = getSavedProfileNames();
        profileNames[email.toLowerCase()] = fullName;
        localStorage.setItem('profileNames', JSON.stringify(profileNames));
    };

    useEffect(() => {
        // localStorage'daki token'ın süresi dolmuş mu kontrol et (local, network isteği yok)
        const validateStoredToken = () => {
            const savedUser = localStorage.getItem('user');
            const token = localStorage.getItem('token');

            if (savedUser && token) {
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    const isExpired = payload.exp * 1000 < Date.now();
                    if (isExpired) {
                        // Token süresi dolmuş, temizle
                        localStorage.removeItem('user');
                        localStorage.removeItem('token');
                    } else {
                        // Token geçerli, oturumu devam ettir
                        setUser(JSON.parse(savedUser));
                    }
                } catch {
                    // Token parse edilemiyorsa temizle
                    localStorage.removeItem('user');
                    localStorage.removeItem('token');
                }
            }
            setIsLoading(false);
        };

        validateStoredToken();
    }, []);

    const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            if (response.ok) {
                const data = await response.json();
                const profileNames = getSavedProfileNames();
                const savedFullName = profileNames[email.toLowerCase()];
                
                // Extract user info from JWT token
                const tokenPayload = JSON.parse(atob(data.access_token.split('.')[1]));
                const user: User = {
                    id: tokenPayload.user_id,
                    email,
                    fullName: savedFullName
                };
                setUser(user);
                localStorage.setItem('user', JSON.stringify(user));
                localStorage.setItem('token', data.access_token);
                return { success: true };
            } else {
                const errorData = await response.json();
                console.error('Login failed:', errorData.detail);
                return { success: false, error: errorData.detail || 'Giriş başarısız' };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: 'Sunucuya bağlanılamadı' };
        }
    };

    const register = async (email: string, password: string, fullName?: string): Promise<{ success: boolean; error?: string }> => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            if (response.ok) {
                if (fullName && fullName.trim()) {
                    saveProfileName(email, fullName.trim());
                }
                // After successful registration, automatically log in
                return await login(email, password);
            } else {
                const errorData = await response.json();
                console.error('Registration failed:', errorData.detail);
                return { success: false, error: errorData.detail || 'Kayıt başarısız' };
            }
        } catch (error) {
            console.error('Registration error:', error);
            return { success: false, error: 'Sunucuya bağlanılamadı' };
        }
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('user');
        localStorage.removeItem('token');
    };

    const value: AuthContextType = {
        user,
        login,
        register,
        logout,
        isLoading
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};
