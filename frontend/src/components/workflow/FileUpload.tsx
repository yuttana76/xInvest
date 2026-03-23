import React, { useRef } from 'react';
import { Upload, X, FileText, Image as ImageIcon } from 'lucide-react';

interface FileUploadProps {
  files: File[];
  onChange: (files: File[]) => void;
  maxFiles?: number;
}

export const FileUpload: React.FC<FileUploadProps> = ({ files, onChange, maxFiles = 5 }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      const combinedFiles = [...files, ...newFiles].slice(0, maxFiles);
      onChange(combinedFiles);
    }
  };

  const removeFile = (index: number) => {
    const updatedFiles = files.filter((_, i) => i !== index);
    onChange(updatedFiles);
  };

  const isImage = (file: File) => file.type.startsWith('image/');

  return (
    <div className="space-y-4">
      <div
        onClick={() => fileInputRef.current?.click()}
        className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-6 flex flex-col items-center justify-center cursor-pointer hover:border-blue-500 transition-colors"
      >
        <Upload className="w-10 h-10 text-gray-400 mb-2" />
        <p className="text-sm text-gray-600 dark:text-gray-400">Click or drag files here</p>
        <p className="text-xs text-gray-500 mt-1">Max {maxFiles} files</p>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          multiple
          className="hidden"
        />
      </div>

      {files.length > 0 && (
        <ul className="space-y-2">
          {files.map((file, idx) => (
            <li
              key={idx}
              className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded border border-gray-100 dark:border-gray-700"
            >
              <div className="flex items-center space-x-3 overflow-hidden">
                {isImage(file) ? (
                  <ImageIcon className="w-5 h-5 text-blue-500" />
                ) : (
                  <FileText className="w-5 h-5 text-gray-500" />
                )}
                <span className="text-sm truncate max-w-[200px]">{file.name}</span>
                <span className="text-xs text-gray-400">({(file.size / 1024).toFixed(1)} KB)</span>
              </div>
              <button
                type="button"
                onClick={() => removeFile(idx)}
                className="p-1 hover:bg-red-100 hover:text-red-500 rounded text-gray-400 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
