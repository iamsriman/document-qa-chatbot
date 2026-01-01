import { useState, useEffect } from 'react';
import { getDocuments, deleteDocument } from '../services/api';

function DocumentList({ onSelectDocument, selectedDocumentId, refreshTrigger }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDocuments();
  }, [refreshTrigger]);

  const fetchDocuments = async () => {
    try {
      const docs = await getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (documentId, e) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await deleteDocument(documentId);
        fetchDocuments();
        if (selectedDocumentId === documentId) {
          onSelectDocument(null);
        }
      } catch (error) {
        console.error('Failed to delete document:', error);
      }
    }
  };

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="text-center py-4">Loading documents...</div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">My Documents</h2>
      
      {documents.length === 0 ? (
        <p className="text-gray-500">No documents uploaded yet</p>
      ) : (
        <div className="space-y-2">
          {documents.map((doc) => (
            <div
              key={doc.id}
              onClick={() => onSelectDocument(doc)}
              className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                selectedDocumentId === doc.id 
                  ? 'bg-blue-50 border-blue-500' 
                  : 'border-gray-200 hover:bg-gray-50'
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-800">{doc.filename}</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {new Date(doc.upload_date).toLocaleDateString()} • {doc.chunk_count} chunks
                  </p>
                </div>
                <button
                  onClick={(e) => handleDelete(doc.id, e)}
                  className="text-red-500 hover:text-red-700 ml-2 font-medium"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default DocumentList;