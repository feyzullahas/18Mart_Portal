import '../styles/PdfViewer.css';

interface PdfViewerProps {
    url: string;
    downloadUrl?: string;
}

export const PdfViewer = ({ url }: PdfViewerProps) => (
    <div className="pdf-viewer-wrapper">
        <iframe
            src={`${url}#navpanes=0`}
            className="pdf-frame"
            title="Otobüs Saatleri PDF"
            allow="fullscreen"
        />
    </div>
);
