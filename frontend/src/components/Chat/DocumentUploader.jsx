import { useState } from 'react';
import { uploadDocument } from '../../services/api';

function DocumentUploader({ topicId, onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a PDF file');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    if (!topicId) {
      setError('Please select a topic first');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const result = await uploadDocument(file, topicId);
      onUploadSuccess(result);
      setFile(null);
      document.getElementById('file-input').value = '';
    } catch (err) {
      setError('Failed to upload document: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">📤 Upload PDF</h2>
      
      {!topicId && (
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg mb-4">
          <p className="text-yellow-800 text-sm">
            ⚠️ Please select a topic first before uploading
          </p>
        </div>
      )}
      
      <div className="mb-4">
        <input
          id="file-input"
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          disabled={!topicId}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50"
        />
      </div>

      {file && (
        <p className="text-sm text-gray-600 mb-4">
          Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
        </p>
      )}

      {error && (
        <p className="text-red-500 text-sm mb-4">{error}</p>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || uploading || !topicId}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {uploading ? 'Uploading...' : 'Upload PDF'}
      </button>
    </div>
  );
}

export default DocumentUploader;