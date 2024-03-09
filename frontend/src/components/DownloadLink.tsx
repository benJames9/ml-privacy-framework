import React from 'react';

interface DownloadLinkProps {
    base64Zip: string;
    fileName: string;
}

const DownloadLink: React.FC<DownloadLinkProps> = ({ base64Zip, fileName }) => {
    const createBlobUrlFromBase64 = (base64Data: string, contentType: string): string => {
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: contentType });
        const blobUrl = URL.createObjectURL(blob);
        return blobUrl;
    };

    const downloadUrl = createBlobUrlFromBase64(base64Zip, 'application/zip');
    const info = `This zip file will contain all true images, their reconstructions as well as metrics in corresponding files`;

    return (
        <div className={`px-8 text-gray-200 rounded-md text-center`}>
            <h1 className="text-md text-white mb-4 p-3">{info}</h1>
            <a href={downloadUrl} download={fileName} className="text-white bg-gradient-to-br from-blue-500 to-purple-800 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-blue-800 font-bold rounded-lg text-2xl px-8 py-4 text-center mx-4">
                Download Zip
            </a>
        </div>
    );
};

export default DownloadLink;
