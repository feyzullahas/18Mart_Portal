import { useEffect, useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import '../styles/Auth.css';

declare global {
    interface Window {
        google?: {
            accounts: {
                id: {
                    initialize: (config: {
                        client_id: string;
                        callback: (response: { credential?: string }) => void;
                    }) => void;
                    renderButton: (
                        parent: HTMLElement,
                        options: {
                            theme?: 'outline' | 'filled_blue' | 'filled_black';
                            size?: 'large' | 'medium' | 'small';
                            type?: 'standard' | 'icon';
                            text?: 'signin_with' | 'signup_with' | 'continue_with' | 'signin';
                            shape?: 'rectangular' | 'pill' | 'circle' | 'square';
                            logo_alignment?: 'left' | 'center';
                            width?: number;
                        }
                    ) => void;
                };
            };
        };
    }
}

interface AuthProps {
    embedded?: boolean;
    onClose?: () => void;
}

export const Auth = ({ embedded = false, onClose }: AuthProps) => {
    const [isLogin, setIsLogin] = useState(true);
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    
    const { login, loginWithGoogle, register } = useAuth();
    const { theme } = useTheme();
    const googleButtonContainerRef = useRef<HTMLDivElement | null>(null);
    const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            // Validation for registration
            if (!isLogin) {
                if (password !== confirmPassword) {
                    setError('Şifreler eşleşmiyor.');
                    setIsLoading(false);
                    return;
                }
                
                if (password.length < 6) {
                    setError('Şifre en az 6 karakter olmalıdır.');
                    setIsLoading(false);
                    return;
                }

                if (!/\d/.test(password)) {
                    setError('Şifre en az bir rakam içermelidir.');
                    setIsLoading(false);
                    return;
                }
            }

            const result = isLogin 
                ? await login(email, password)
                : await register(email, password, fullName);

            if (!result.success) {
                setError(result.error || (isLogin
                    ? 'Giriş başarısız. Lütfen bilgilerinizi kontrol edin.'
                    : 'Kayıt başarısız. Lütfen bilgilerinizi kontrol edin.'));
            }
        } catch (err) {
            setError('Bir hata oluştu. Lütfen tekrar deneyin.');
        } finally {
            setIsLoading(false);
        }
    };

    const toggleMode = () => {
        setIsLogin(!isLogin);
        setError('');
        setFullName('');
        setEmail('');
        setPassword('');
        setConfirmPassword('');
    };

    useEffect(() => {
        if (!isLogin || !googleClientId || !googleButtonContainerRef.current) {
            return;
        }

        const initGoogleSignIn = () => {
            if (!window.google || !googleButtonContainerRef.current) {
                return;
            }

            const resolvedTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';

            googleButtonContainerRef.current.innerHTML = '';
            window.google.accounts.id.initialize({
                client_id: googleClientId,
                callback: async ({ credential }) => {
                    if (!credential) {
                        setError('Google kimlik bilgisi alınamadı.');
                        return;
                    }

                    setIsLoading(true);
                    setError('');
                    const result = await loginWithGoogle(credential);
                    if (!result.success) {
                        setError(result.error || 'Google ile giriş başarısız.');
                    }
                    setIsLoading(false);
                },
            });

            window.google.accounts.id.renderButton(googleButtonContainerRef.current, {
                theme: resolvedTheme === 'dark' ? 'filled_blue' : 'outline',
                size: 'large',
                type: 'standard',
                text: 'signin_with',
                shape: 'rectangular',
                logo_alignment: 'left',
                width: 320,
            });
        };

        if (window.google) {
            initGoogleSignIn();
            return;
        }

        const existingScript = document.querySelector<HTMLScriptElement>('script[data-google-identity="true"]');
        if (existingScript) {
            existingScript.addEventListener('load', initGoogleSignIn, { once: true });
            return () => existingScript.removeEventListener('load', initGoogleSignIn);
        }

        const script = document.createElement('script');
        script.src = 'https://accounts.google.com/gsi/client';
        script.async = true;
        script.defer = true;
        script.dataset.googleIdentity = 'true';
        script.onload = initGoogleSignIn;
        document.head.appendChild(script);

        return () => {
            script.onload = null;
        };
    }, [isLogin, googleClientId, loginWithGoogle, theme]);

    return (
        <div className={`auth-container ${embedded ? 'auth-container-embedded' : ''}`}>
            <div className={`auth-card ${embedded ? 'auth-card-embedded' : ''}`}>
                {embedded && onClose && (
                    <button type="button" className="auth-close-button" onClick={onClose} aria-label="Kapat">
                        ×
                    </button>
                )}
                {/* Header */}
                <div className="auth-header">
                    <img src="/favicon.png" alt="18 Mart Portal" className="auth-logo" />
                    <h1 className="auth-title">18 Mart Portal</h1>
                    <p className="auth-subtitle">Çanakkale Onsekiz Mart Üniversitesi Öğrenci Portalı</p>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="auth-form">
                    <h2 className="form-title">
                        {isLogin ? 'Giriş Yap' : 'Kayıt Ol'}
                    </h2>

                    {error && <div className="error-message">{error}</div>}

                    {!isLogin && (
                        <div className="form-group">
                            <label htmlFor="fullName" className="form-label">
                                İsim Soyisim
                            </label>
                            <input
                                type="text"
                                id="fullName"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                className="form-input"
                                placeholder="Ad Soyad"
                                required
                                minLength={3}
                            />
                        </div>
                    )}

                    <div className="form-group">
                        <label htmlFor="email" className="form-label">
                            E-mail
                        </label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="form-input"
                            placeholder="ornek@gmail.com"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password" className="form-label">
                            Şifre
                        </label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="form-input"
                            placeholder="En az 6 karakter"
                            required
                            minLength={6}
                        />
                    </div>

                    {!isLogin && (
                        <div className="form-group">
                            <label htmlFor="confirmPassword" className="form-label">
                                Şifre Tekrar
                            </label>
                            <input
                                type="password"
                                id="confirmPassword"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                className="form-input"
                                placeholder="Şifrenizi tekrar girin"
                                required
                                minLength={6}
                            />
                        </div>
                    )}

                    <button 
                        type="submit" 
                        className="auth-button"
                        disabled={isLoading}
                    >
                        {isLoading ? 'İşleniyor...' : (isLogin ? 'Giriş Yap' : 'Kayıt Ol')}
                    </button>

                    {isLogin && (
                        <>
                            <div className="auth-divider" role="separator" aria-label="veya">
                                <span>veya</span>
                            </div>
                            {googleClientId ? (
                                <div className="google-signin-container" ref={googleButtonContainerRef}></div>
                            ) : (
                                <p className="google-config-note">
                                    Google giriş için VITE_GOOGLE_CLIENT_ID tanımlanmalı.
                                </p>
                            )}
                        </>
                    )}
                </form>

                {/* Toggle */}
                <div className="auth-toggle">
                    <p>
                        {isLogin ? 'Hesabınız yok mu?' : 'Zaten hesabınız var mı?'}
                        <button 
                            type="button" 
                            onClick={toggleMode}
                            className="toggle-button"
                        >
                            {isLogin ? 'Kayıt Ol' : 'Giriş Yap'}
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
};
