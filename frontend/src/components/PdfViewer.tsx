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

    useEffect(() => {
        if (wrapperRef.current) {
            setBaseWidth(wrapperRef.current.offsetWidth);
        }
    }, []);

    useEffect(() => {
        setNumPages(0);
        setVisiblePages(1);
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

    // Cihazin gercek DPR'ini kullan — bu mobilde keskin render icin kritik
    const dpr = Math.min(window.devicePixelRatio || 1, 3);

    return (
        <div className="pdf-viewer-wrapper">
            <div className="pdf-scroll-area" ref={wrapperRef}>
                <Document
                    file={url}
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
            </div>
        </div>
    );
};
