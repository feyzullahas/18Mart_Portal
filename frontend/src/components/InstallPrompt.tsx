import { useEffect, useMemo, useState } from 'react';

type BeforeInstallPromptEvent = Event & {
  readonly platforms: string[];
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>;
};

type NavigatorWithStandalone = Navigator & {
  standalone?: boolean;
};

const TOAST_KEY = 'pwa_install_toast_dismissed_v1';
const DEFAULT_TOAST = 'Uygulamayı ana ekrana ekleyerek daha hızlı kullanabilirsiniz.';
const IOS_FALLBACK = 'Safari üzerinden Paylaş > Ana Ekrana Ekle seçeneği ile ekleyebilirsiniz.';
const UNSUPPORTED = 'Bu tarayıcıda kurulum desteklenmiyor.';

const isIosDevice = () => /iphone|ipad|ipod/i.test(navigator.userAgent);
const isSafariBrowser = () => /safari/i.test(navigator.userAgent) && !/chrome|crios|android/i.test(navigator.userAgent);

const isStandaloneMode = () => {
  if (window.matchMedia('(display-mode: standalone)').matches) return true;
  return (navigator as NavigatorWithStandalone).standalone === true;
};

export type InstallPromptState = {
  canInstall: boolean;
  isInstalled: boolean;
  isSupported: boolean;
  isIos: boolean;
  showToast: boolean;
  toastMessage: string;
  promptInstall: () => Promise<void>;
  dismissToast: () => void;
};

export const useInstallPrompt = (): InstallPromptState => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstalled, setIsInstalled] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState(DEFAULT_TOAST);
  const isIos = useMemo(() => isIosDevice(), []);
  const isSafari = useMemo(() => isSafariBrowser(), []);
  const isSupported = useMemo(() => 'BeforeInstallPromptEvent' in window, []);

  useEffect(() => {
    setIsInstalled(isStandaloneMode());
  }, []);

  useEffect(() => {
    const onBeforeInstallPrompt = (event: Event) => {
      event.preventDefault();
      setDeferredPrompt(event as BeforeInstallPromptEvent);
      if (!isInstalled && !sessionStorage.getItem(TOAST_KEY)) {
        setToastMessage(DEFAULT_TOAST);
        setShowToast(true);
      }
    };

    const onInstalled = () => {
      setDeferredPrompt(null);
      setIsInstalled(true);
      setShowToast(false);
    };

    window.addEventListener('beforeinstallprompt', onBeforeInstallPrompt);
    window.addEventListener('appinstalled', onInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', onBeforeInstallPrompt);
      window.removeEventListener('appinstalled', onInstalled);
    };
  }, [isInstalled]);

  useEffect(() => {
    if (!isInstalled && isIos && isSafari && !sessionStorage.getItem(TOAST_KEY)) {
      setToastMessage(DEFAULT_TOAST);
      setShowToast(true);
    }
  }, [isInstalled, isIos, isSafari]);

  const dismissToast = () => {
    sessionStorage.setItem(TOAST_KEY, '1');
    setShowToast(false);
  };

  const promptInstall = async () => {
    if (isInstalled) return;

    if (deferredPrompt) {
      await deferredPrompt.prompt();
      await deferredPrompt.userChoice;
      setDeferredPrompt(null);
      setShowToast(false);
      return;
    }

    if (isIos && isSafari) {
      setToastMessage(IOS_FALLBACK);
      setShowToast(true);
      return;
    }

    setToastMessage(UNSUPPORTED);
    setShowToast(true);
  };

  return {
    canInstall: !!deferredPrompt,
    isInstalled,
    isSupported,
    isIos,
    showToast,
    toastMessage,
    promptInstall,
    dismissToast,
  };
};

export const InstallToast = ({
  isVisible,
  message,
  onDismiss,
}: {
  isVisible: boolean;
  message: string;
  onDismiss: () => void;
}) => {
  useEffect(() => {
    if (!isVisible) return;
    const timer = window.setTimeout(() => onDismiss(), 7000);
    return () => window.clearTimeout(timer);
  }, [isVisible, onDismiss]);

  if (!isVisible) return null;

  return (
    <div className="pwa-toast" role="status" aria-live="polite">
      <span>{message}</span>
      <button type="button" onClick={onDismiss} aria-label="Toast mesajini kapat">
        Kapat
      </button>
    </div>
  );
};
