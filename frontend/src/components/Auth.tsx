import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import '../styles/Auth.css';

export const Auth = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    
    const { login, register } = useAuth();

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
                
                if (password.length > 6) {
                    setError('Şifre en fazla 6 karakter olmalıdır.');
                    setIsLoading(false);
                    return;
                }

                if (!/\d/.test(password)) {
                    setError('Şifre en az bir rakam içermelidir.');
                    setIsLoading(false);
                    return;
                }
            }

            const success = isLogin 
                ? await login(email, password)
                : await register(email, password);

            if (!success) {
                setError(isLogin ? 'Giriş başarısız. Lütfen bilgilerinizi kontrol edin.' : 'Kayıt başarısız. Lütfen bilgilerinizi kontrol edin.');
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
        setEmail('');
        setPassword('');
        setConfirmPassword('');
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
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

                    <div className="form-group">
                        <label htmlFor="email" className="form-label">
                            E-posta
                        </label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="form-input"
                            placeholder="ornek@comu.edu.tr"
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
