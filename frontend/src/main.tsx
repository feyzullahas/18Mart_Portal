import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Analytics } from '@vercel/analytics/react'
import { pdfjs } from 'react-pdf'
import workerSrc from 'pdfjs-dist/build/pdf.worker.min.mjs?url'
import './index.css'
import App from './App.tsx'

const THEME_PREF_KEY = 'themePreference';

const applyInitialTheme = () => {
  const saved = localStorage.getItem(THEME_PREF_KEY);
  const preference = (saved === 'light' || saved === 'dark' || saved === 'system') ? saved : 'system';
  const theme = preference === 'system'
    ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
    : preference;

  document.documentElement.setAttribute('data-theme', theme);
};

applyInitialTheme();

pdfjs.GlobalWorkerOptions.workerSrc = workerSrc;

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
    <Analytics />
  </StrictMode>,
)

if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register('/service-worker.js')
      .then((registration) => {
        registration.update().catch(() => undefined);
      })
      .catch((error) => {
        console.error('Service worker registration failed:', error);
      });
  });
}