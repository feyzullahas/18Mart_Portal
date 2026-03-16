import { useState, useRef, useEffect } from 'react';
import { Document, Page } from 'react-pdf';
import '../styles/PdfViewer.css';

interface PdfViewerProps {
    url: string;
    downloadUrl?: string;
}

export const PdfViewer = ({ url }: PdfViewerProps) => {
    const wrapperRef = useRef<HTMLDivElement>(null);
    const [baseWidth, setBaseWidth] = useState(0);
    const [numPages, setNumPages] = useState(0);
    const [visiblePages, setVisiblePages] = useState(1);
    const [zoom, setZoom] = useState(1);
    // PDF bytes'ı blob URL'e çevir — redirect/CORS/proxy sorunu olmaz
    const [blobUrl, setBlobUrl] = useState<string | null>(null);
    const [fetchError, setFetchError] = useState(false);

    const ZOOM_STEP = 0.1;
    const ZOOM_MIN = 0.6;
    const ZOOM_MAX = 2.5;

    useEffect(() => {
        if (wrapperRef.current) {
            setBaseWidth(wrapperRef.current.offsetWidth);
        }
    }, []);

    useEffect(() => {
        const onResize = () => {
            if (wrapperRef.current) {
                setBaseWidth(wrapperRef.current.offsetWidth);
            }
        };

        window.addEventListener('resize', onResize);
        return () => window.removeEventListener('resize', onResize);
    }, []);

    // URL değişince önceki blob'u temizle, yenisini çek
    useEffect(() => {
        setNumPages(0);
        setVisiblePages(1);
        setZoom(1);
        setBlobUrl(null);
        setFetchError(false);

        let objectUrl: string;
        const controller = new AbortController();

        fetch(url, { signal: controller.signal })
            .then(r => {
                if (!r.ok) throw new Error(`HTTP ${r.status}`);
                return r.blob();
            })
            .then(blob => {
                objectUrl = URL.createObjectURL(blob);
                setBlobUrl(objectUrl);
            })
            .catch(err => {
                if (err.name !== 'AbortError') setFetchError(true);
            });

        return () => {
            controller.abort();
            if (objectUrl) URL.revokeObjectURL(objectUrl);
        };
    }, [url]);

    useEffect(() => {
        if (numPages <= 1) return;
        let current = 2;
        const step = () => {
            if (current > numPages) return;
            setVisiblePages(current);
            current++;
            setTimeout(step, 150);
        };
        setTimeout(step, 100);
    }, [numPages]);

    const dpr = Math.min(window.devicePixelRatio || 1, 3);
    const pageWidth = baseWidth > 0 ? Math.round(baseWidth * zoom) : undefined;

    const zoomIn = () => {
        setZoom(prev => Math.min(ZOOM_MAX, +(prev + ZOOM_STEP).toFixed(2)));
    };

    const zoomOut = () => {
        setZoom(prev => Math.max(ZOOM_MIN, +(prev - ZOOM_STEP).toFixed(2)));
    };

    if (fetchError) {
        return (
            <div className="pdf-viewer-wrapper">
                <div className="pdf-error">⚠️ PDF yüklenemedi.</div>
            </div>
        );
    }

    return (
        <div className="pdf-viewer-wrapper">
            <div className="pdf-toolbar" aria-label="PDF yakınlaştırma kontrolleri">
                <button
                    type="button"
                    className="pdf-zoom-btn"
                    onClick={zoomOut}
                    disabled={zoom <= ZOOM_MIN}
                    aria-label="Uzaklaştır"
                >
                    -
                </button>
                <span className="pdf-zoom-value">%{Math.round(zoom * 100)}</span>
                <button
                    type="button"
                    className="pdf-zoom-btn"
                    onClick={zoomIn}
                    disabled={zoom >= ZOOM_MAX}
                    aria-label="Yakınlaştır"
                >
                    +
                </button>
            </div>
            <div className="pdf-scroll-area" ref={wrapperRef}>
                {!blobUrl ? (
                    <div className="pdf-loading">
                        <div className="pdf-spinner" />
                        <span>En güncel PDF yükleniyor...</span>
                    </div>
                ) : (
                    <Document
                        file={blobUrl}
                        onLoadSuccess={({ numPages }) => setNumPages(numPages)}
                        loading={
                            <div className="pdf-loading">
                                <div className="pdf-spinner" />
                                <span>En güncel PDF yükleniyor...</span>
                            </div>
                        }
                        error={<div className="pdf-error">⚠️ PDF yüklenemedi.</div>}
                    >
                        {Array.from({ length: visiblePages }, (_, i) => (
                            <div key={i} className="pdf-page-wrap">
                                <Page
                                    pageNumber={i + 1}
                                    width={pageWidth}
                                    devicePixelRatio={dpr}
                                    renderTextLayer={false}
                                    renderAnnotationLayer={false}
                                    loading={null}
                                />
                            </div>
                        ))}
                    </Document>
                )}
            </div>
        </div>
    );
};
