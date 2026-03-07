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
    // visiblePages: önce 1, sonra progressif artar
    const [visiblePages, setVisiblePages] = useState(1);
    const [loadProgress, setLoadProgress] = useState(0);

    useEffect(() => {
        if (wrapperRef.current) {
            setBaseWidth(wrapperRef.current.offsetWidth);
        }
    }, []);

    // URL değişince sıfırla
    useEffect(() => {
        setNumPages(0);
        setVisiblePages(1);
        setLoadProgress(0);
    }, [url]);

    // Doküman yüklenince: 1. sayfa zaten görünecek, geri kalanları kısa gecikmelerle ekle
    useEffect(() => {
        if (numPages <= 1) return;
        let current = 2;
        const step = () => {
            if (current > numPages) return;
            setVisiblePages(current);
            current++;
            // Her sayfayı bir öncekinden 150ms sonra render et
            setTimeout(step, 150);
        };
        setTimeout(step, 100);
    }, [numPages]);

    const dpr = Math.min(window.devicePixelRatio || 1, 2); // 3x DPR'yı 2x ile sınırla — mobilde performans

    return (
        <div className="pdf-viewer-wrapper">
            <div className="pdf-scroll-area" ref={wrapperRef}>
                <Document
                    file={url}
                    onLoadProgress={({ loaded, total }) =>
                        setLoadProgress(total > 0 ? Math.round((loaded / total) * 100) : 0)
                    }
                    onLoadSuccess={({ numPages }) => {
                        setNumPages(numPages);
                        setLoadProgress(100);
                    }}
                    loading={
                        <div className="pdf-loading">
                            <div className="pdf-spinner" />
                            <span>PDF yükleniyor{loadProgress > 0 && loadProgress < 100 ? ` %${loadProgress}` : '…'}</span>
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
            </div>
        </div>
    );
};
