"use client";
import React, { useState } from 'react';

interface FileUploadProps {
  expectedFileType: string;
  label?: string;
  onFileChange: (file: File | null) => void;
  nextElement?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
  expectedFileType,
  label = '',
  onFileChange,
  nextElement = "",
}) => {
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (!file) return;

    const fileType: string = file.name.split('.').pop() || '';

    if (fileType === expectedFileType) {
      onFileChange(file);

      if (nextElement === "") return;
      const dataParams = document.getElementById(nextElement);
      dataParams!.scrollIntoView({ behavior: "smooth" });
    } else {
      onFileChange(null);
      console.error('Invalid file type selected');
    }
  };

  return (
    <div>
      <label htmlFor="file-upload" className="block text-sm font-medium text-gray-300 text-left">
        {label}
      </label>
      <input
        type="file"
        id="file-upload"
        accept={`.${expectedFileType}`}
        className="block w-80 p-3 text-sm border border-gray-300 rounded-md cursor-pointer focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
        onChange={handleFileChange}
      />
    </div>
  );
};

export default FileUpload;
