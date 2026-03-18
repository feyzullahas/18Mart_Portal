import { useState, useRef, useEffect, useMemo } from 'react';
import { Document, Page } from 'react-pdf';
import '../styles/PdfViewer.css';

interface PdfViewerProps {
    url: string;
    downloadUrl?: string;
}

export const PdfViewer = ({ url }: PdfViewerProps) => {
    const wrapperRef = useRef<HTMLDivElement>(null);
    const contentShellRef = useRef<HTMLDivElement>(null);
    const scaleLayerRef = useRef<HTMLDivElement>(null);
    const documentRef = useRef<HTMLDivElement>(null);
    const pinchStartDistanceRef = useRef<number | null>(null);
    const pinchStartZoomRef = useRef(1);
    const pinchStartContentXRef = useRef(0);
    const pinchStartContentYRef = useRef(0);
    const pinchCurrentZoomRef = useRef(1);
    const rafRef = useRef<number | null>(null);
    const qualityRestoreTimerRef = useRef<number | null>(null);
    const highResWarmupTimerRef = useRef<number | null>(null);
    const zoomRef = useRef(1);
    const isPinchingRef = useRef(false);
    const docSizeRef = useRef({ width: 0, height: 0 });
    const [baseWidth, setBaseWidth] = useState(0);
    const [docSize, setDocSize] = useState({ width: 0, height: 0 });
    const [numPages, setNumPages] = useState(0);
    const [visiblePages, setVisiblePages] = useState(1);
    const [zoom, setZoom] = useState(1);
    const [isPinching, setIsPinching] = useState(false);
    const [highResCacheEnabled, setHighResCacheEnabled] = useState(false);
    const [preferHighRes, setPreferHighRes] = useState(false);
    // PDF bytes'ı blob URL'e çevir — redirect/CORS/proxy sorunu olmaz
    const [blobUrl, setBlobUrl] = useState<string | null>(null);
    const [fetchError, setFetchError] = useState(false);

    const ZOOM_STEP = 0.1;
    const ZOOM_MIN = 1;
    const ZOOM_MAX = 2.5;
    const isCoarsePointer = useMemo(() => {
        if (typeof window === 'undefined' || !window.matchMedia) return false;
        return window.matchMedia('(pointer: coarse)').matches;
    }, []);
    const lowDpr = useMemo(() => {
        const base = Math.min(window.devicePixelRatio || 1, 2);
        return isCoarsePointer ? Math.min(base * 1.1, 2.2) : Math.min(base * 1.15, 2.4);
    }, [isCoarsePointer]);

    const highDpr = useMemo(() => {
        const base = Math.min(window.devicePixelRatio || 1, 2);
        return isCoarsePointer ? Math.min(base * 1.7, 3.1) : Math.min(base * 1.8, 3.2);
    }, [isCoarsePointer]);

    const clearQualityRestoreTimer = () => {
        if (qualityRestoreTimerRef.current !== null) {
            window.clearTimeout(qualityRestoreTimerRef.current);
            qualityRestoreTimerRef.current = null;
        }
    };

    const scheduleHighQuality = (delay = 160) => {
        if (!highResCacheEnabled) return;
        clearQualityRestoreTimer();
        qualityRestoreTimerRef.current = window.setTimeout(() => {
            setPreferHighRes(true);
            qualityRestoreTimerRef.current = null;
        }, delay);
    };

    const applyShellSize = (targetZoom: number) => {
        const shell = contentShellRef.current;
        const size = docSizeRef.current;
        if (!shell || size.width <= 0 || size.height <= 0) return;

        const width = Math.max(baseWidth, size.width * targetZoom);
        const height = size.height * targetZoom;

        shell.style.width = `${Math.round(width)}px`;
        shell.style.height = `${Math.round(height)}px`;
    };

    const applyScale = (targetZoom: number) => {
        const layer = scaleLayerRef.current;
        if (!layer) return;
        layer.style.transform = `scale(${targetZoom})`;
    };

    const getTouchDistance = (touches: TouchList) => {
        if (touches.length < 2) return 0;
        const t1 = touches[0];
        const t2 = touches[1];
        return Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY);
    };

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

    useEffect(() => {
        zoomRef.current = zoom;
    }, [zoom]);

    useEffect(() => {
        setPreferHighRes(!isCoarsePointer);
    }, [isCoarsePointer]);

    useEffect(() => {
        if (highResWarmupTimerRef.current !== null) {
            window.clearTimeout(highResWarmupTimerRef.current);
            highResWarmupTimerRef.current = null;
        }

        setHighResCacheEnabled(false);

        if (!blobUrl) return;

        // PDF açıldıktan hemen sonra yüksek çözünürlüklü katmanı hazırlamaya başla.
        highResWarmupTimerRef.current = window.setTimeout(() => {
            setHighResCacheEnabled(true);
            if (!isPinchingRef.current) {
                scheduleHighQuality(60);
            }
            highResWarmupTimerRef.current = null;
        }, 220);

        return () => {
            if (highResWarmupTimerRef.current !== null) {
                window.clearTimeout(highResWarmupTimerRef.current);
                highResWarmupTimerRef.current = null;
            }
        };
    }, [blobUrl]);

    useEffect(() => {
        if (isPinching) return;
        scheduleHighQuality(140);
    }, [zoom, isPinching, highResCacheEnabled]);

    useEffect(() => {
        const docEl = documentRef.current;
        if (!docEl) return;

        const observer = new ResizeObserver(() => {
            const width = docEl.offsetWidth;
            const height = docEl.offsetHeight;
            docSizeRef.current = { width, height };
            setDocSize({ width, height });
        });

        observer.observe(docEl);
        return () => observer.disconnect();
    }, [blobUrl, visiblePages]);

    useEffect(() => {
        if (isPinchingRef.current) return;
        applyScale(zoom);
        applyShellSize(zoom);
    }, [zoom, baseWidth, docSize.width, docSize.height]);

    useEffect(() => {
        const el = wrapperRef.current;
        if (!el) return;

        const scheduleScrollAndTransform = (nextZoom: number, midClientX: number, midClientY: number) => {
            if (rafRef.current !== null) {
                cancelAnimationFrame(rafRef.current);
            }

            rafRef.current = requestAnimationFrame(() => {
                const target = wrapperRef.current;
                if (!target) return;

                applyScale(nextZoom);
                applyShellSize(nextZoom);

                const rect = target.getBoundingClientRect();
                const localX = midClientX - rect.left;
                const localY = midClientY - rect.top;
                const scaleRatio = nextZoom / pinchStartZoomRef.current;

                target.scrollLeft = Math.max(0, pinchStartContentXRef.current * scaleRatio - localX);
                target.scrollTop = Math.max(0, pinchStartContentYRef.current * scaleRatio - localY);
            });
        };

        const onTouchStart = (e: TouchEvent) => {
            if (e.touches.length === 2) {
                const rect = el.getBoundingClientRect();
                const midClientX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
                const midClientY = (e.touches[0].clientY + e.touches[1].clientY) / 2;

                isPinchingRef.current = true;
                setIsPinching(true);
                setPreferHighRes(false);
                pinchStartDistanceRef.current = getTouchDistance(e.touches);
                pinchStartZoomRef.current = zoomRef.current;
                pinchCurrentZoomRef.current = zoomRef.current;
                pinchStartContentXRef.current = el.scrollLeft + (midClientX - rect.left);
                pinchStartContentYRef.current = el.scrollTop + (midClientY - rect.top);

                const layer = scaleLayerRef.current;
                if (layer) {
                    layer.style.willChange = 'transform';
                }
                if (e.cancelable) {
                    e.preventDefault();
                }
            }
        };

        const onTouchMove = (e: TouchEvent) => {
            if (!isPinchingRef.current || e.touches.length !== 2 || !pinchStartDistanceRef.current) {
                return;
            }

            const distance = getTouchDistance(e.touches);
            if (distance <= 0) return;

            const scale = distance / pinchStartDistanceRef.current;
            const nextZoom = Math.min(
                ZOOM_MAX,
                Math.max(ZOOM_MIN, +(pinchStartZoomRef.current * scale).toFixed(2))
            );

            const midClientX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
            const midClientY = (e.touches[0].clientY + e.touches[1].clientY) / 2;

            pinchCurrentZoomRef.current = nextZoom;
            scheduleScrollAndTransform(nextZoom, midClientX, midClientY);
            if (e.cancelable) {
                e.preventDefault();
            }
        };

        const onTouchEndOrCancel = () => {
            if (isPinchingRef.current) {
                const finalZoom = pinchCurrentZoomRef.current;
                isPinchingRef.current = false;
                setIsPinching(false);
                pinchStartDistanceRef.current = null;

                const layer = scaleLayerRef.current;
                if (layer) {
                    layer.style.willChange = '';
                }

                setZoom(prev => (Math.abs(prev - finalZoom) >= 0.01 ? finalZoom : prev));
                scheduleHighQuality();
            }
        };

        el.addEventListener('touchstart', onTouchStart, { passive: false });
        el.addEventListener('touchmove', onTouchMove, { passive: false });
        el.addEventListener('touchend', onTouchEndOrCancel);
        el.addEventListener('touchcancel', onTouchEndOrCancel);

        return () => {
            if (rafRef.current !== null) {
                cancelAnimationFrame(rafRef.current);
                rafRef.current = null;
            }
            clearQualityRestoreTimer();
            if (highResWarmupTimerRef.current !== null) {
                window.clearTimeout(highResWarmupTimerRef.current);
                highResWarmupTimerRef.current = null;
            }
            el.removeEventListener('touchstart', onTouchStart);
            el.removeEventListener('touchmove', onTouchMove);
            el.removeEventListener('touchend', onTouchEndOrCancel);
            el.removeEventListener('touchcancel', onTouchEndOrCancel);
        };
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

    const pageWidth = baseWidth > 0 ? baseWidth : undefined;

    const pageNodes = useMemo(() => {
        return Array.from({ length: visiblePages }, (_, i) => (
            <div key={i} className={`pdf-page-wrap ${preferHighRes ? 'show-high' : 'show-low'}`}>
                <div className="pdf-page-layer pdf-page-layer-low" aria-hidden={preferHighRes}>
                    <Page
                        pageNumber={i + 1}
                        width={pageWidth}
                        devicePixelRatio={lowDpr}
                        renderTextLayer={false}
                        renderAnnotationLayer={false}
                        loading={null}
                    />
                </div>
                {highResCacheEnabled && (
                    <div className="pdf-page-layer pdf-page-layer-high" aria-hidden={!preferHighRes}>
                        <Page
                            pageNumber={i + 1}
                            width={pageWidth}
                            devicePixelRatio={highDpr}
                            renderTextLayer={false}
                            renderAnnotationLayer={false}
                            loading={null}
                        />
                    </div>
                )}
            </div>
        ));
    }, [visiblePages, pageWidth, lowDpr, highDpr, highResCacheEnabled, preferHighRes]);

    const zoomIn = () => {
        setPreferHighRes(false);
        setZoom(prev => Math.min(ZOOM_MAX, +(prev + ZOOM_STEP).toFixed(2)));
        scheduleHighQuality();
    };

    const zoomOut = () => {
        setPreferHighRes(false);
        setZoom(prev => Math.max(ZOOM_MIN, +(prev - ZOOM_STEP).toFixed(2)));
        scheduleHighQuality();
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
                    <div className="pdf-content-shell" ref={contentShellRef}>
                        <div className={`pdf-scale-layer ${isPinching ? 'pinching' : ''}`} ref={scaleLayerRef}>
                            <div className="pdf-document" ref={documentRef}>
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
                                    {pageNodes}
                                </Document>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
