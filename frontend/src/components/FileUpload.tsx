"use client";
import React, { useState } from 'react';

interface FileUploadProps {
  expectedFileType: string;
  label?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
  expectedFileType,
  label = '',
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (!file) return;

    const fileType: string = file.name.split('.').pop() || '';

    if (fileType === expectedFileType) {
      setSelectedFile(file);
    } else {
      setSelectedFile(null);
      console.error('Invalid file type selected');
    }
  };

  return (
    <div className="mb-4">
      <label htmlFor="file-upload" className="block text-sm font-medium text-gray-300">
        {label}
      </label>
      <input
        type="file"
        id="file-upload"
        accept={`.${expectedFileType}`}
        className="block w-full p-3 text-sm border border-gray-300 rounded-md cursor-pointer focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
        onChange={handleFileChange}
      />
      {selectedFile && (
        <p className="mt-2 text-sm text-gray-400">{selectedFile.name}</p>
      )}
    </div>
  );
};

export default FileUpload;
