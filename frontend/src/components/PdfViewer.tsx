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
    // PDF bytes'ı blob URL'e çevir — redirect/CORS/proxy sorunu olmaz
    const [blobUrl, setBlobUrl] = useState<string | null>(null);
    const [fetchError, setFetchError] = useState(false);

    useEffect(() => {
        if (wrapperRef.current) {
            setBaseWidth(wrapperRef.current.offsetWidth);
        }
    }, []);

    // URL değişince önceki blob'u temizle, yenisini çek
    useEffect(() => {
        setNumPages(0);
        setVisiblePages(1);
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

    if (fetchError) {
        return (
            <div className="pdf-viewer-wrapper">
                <div className="pdf-error">⚠️ PDF yüklenemedi.</div>
            </div>
        );
    }

    return (
        <div className="pdf-viewer-wrapper">
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
                                    width={baseWidth > 0 ? baseWidth : undefined}
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
