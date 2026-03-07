import '../styles/PdfViewer.css';

interface PdfViewerProps {
    url: string;
    downloadUrl?: string;
}

export const PdfViewer = ({ url }: PdfViewerProps) => {
    return (
        <div className="pdf-viewer-wrapper">
            <iframe
                src={`${url}#navpanes=0&view=FitH`}
                className="pdf-embed"
                title="Otobüs Saatleri PDF"
            />
        </div>
    );
};
