import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

interface User {
    id: string;
    email: string;
}

interface AuthContextType {
    user: User | null;
    login: (email: string, password: string) => Promise<boolean>;
    register: (email: string, password: string) => Promise<boolean>;
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

const API_BASE_URL = 'http://localhost:8000';

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Check localStorage for existing user session
        const savedUser = localStorage.getItem('user');
        const token = localStorage.getItem('token');
        if (savedUser && token) {
            setUser(JSON.parse(savedUser));
        }
        setIsLoading(false);
    }, []);

    const login = async (email: string, password: string): Promise<boolean> => {
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
                
                // Extract user info from JWT token
                const tokenPayload = JSON.parse(atob(data.access_token.split('.')[1]));
                const user: User = {
                    id: tokenPayload.user_id,
                    email
                };
                setUser(user);
                localStorage.setItem('user', JSON.stringify(user));
                localStorage.setItem('token', data.access_token);
                return true;
            } else {
                const errorData = await response.json();
                console.error('Login failed:', errorData.detail);
                return false;
            }
        } catch (error) {
            console.error('Login error:', error);
            return false;
        }
    };

    const register = async (email: string, password: string): Promise<boolean> => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            if (response.ok) {
                // After successful registration, automatically log in
                return await login(email, password);
            } else {
                const errorData = await response.json();
                console.error('Registration failed:', errorData.detail);
                return false;
            }
        } catch (error) {
            console.error('Registration error:', error);
            return false;
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
