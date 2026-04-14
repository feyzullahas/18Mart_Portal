import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import '../styles/ProfileSettings.css';

export const ProfileSettings = () => {
    const { user, updateProfile } = useAuth();
    const [fullName, setFullName] = useState(user?.fullName || '');
    const [email, setEmail] = useState(user?.email || '');
    const [message, setMessage] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setMessage(null);
        setError(null);

        const result = updateProfile({ fullName, email });
        if (!result.success) {
            setError(result.error || 'Profil güncellenemedi');
            return;
        }

        setMessage('Profil bilgileri güncellendi.');
    };

    return (
        <section className="profile-settings" aria-label="Profil ayarları">
            <h3>Profil Ayarları</h3>
            <p className="profile-settings-note">
                Buradan isim soyisim ve e-mail bilginizi güncelleyebilirsiniz.
            </p>

            <form className="profile-settings-form" onSubmit={handleSubmit}>
                <label htmlFor="profile-full-name">İsim Soyisim</label>
                <input
                    id="profile-full-name"
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Ad Soyad"
                />

                <label htmlFor="profile-email">E-mail</label>
                <input
                    id="profile-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="ornek@gmail.com"
                    required
                />

                <button type="submit" className="profile-settings-save">
                    Kaydet
                </button>
            </form>

            {message && <p className="profile-settings-message">{message}</p>}
            {error && <p className="profile-settings-error">{error}</p>}
        </section>
    );
};
