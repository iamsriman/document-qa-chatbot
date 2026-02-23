import { useState, useEffect } from 'react';
import { getDocuments } from '../../services/api';

function DocumentList({ topicId, selectedDocuments, onDocumentToggle, refreshTrigger }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (topicId) {
      fetchDocuments();
    }
  }, [topicId, refreshTrigger]);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const data = await getDocuments(topicId);
      setDocuments(data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const isSelected = (docId) => selectedDocuments.includes(docId);

  const handleToggle = (docId) => {
    // Limit to 5 documents
    if (!isSelected(docId) && selectedDocuments.length >= 5) {
      alert('You can select maximum 5 documents');
      return;
    }
    onDocumentToggle(docId);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">📄 Select Documents</h2>
        <span className="text-sm text-gray-600">
          {selectedDocuments.length}/5 selected
        </span>
      </div>

      {!topicId ? (
        <p className="text-gray-500">Please select a topic first</p>
      ) : loading ? (
        <p className="text-gray-500">Loading documents...</p>
      ) : documents.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500 mb-2">No documents in this topic</p>
          <p className="text-sm text-gray-400">Upload PDFs to get started</p>
        </div>
      ) : (
        <div className="space-y-2">
          <p className="text-sm text-gray-600 mb-3">
            Select 2-5 documents to chat with
          </p>
          {documents.map((doc) => (
            <div
              key={doc.id}
              className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                isSelected(doc.id)
                  ? 'bg-blue-50 border-blue-500'
                  : 'hover:bg-gray-50 border-gray-200'
              }`}
            >
              <label className="flex items-start cursor-pointer">
                <input
                  type="checkbox"
                  checked={isSelected(doc.id)}
                  onChange={() => handleToggle(doc.id)}
                  className="mt-1 mr-3 h-5 w-5 text-blue-600 rounded focus:ring-blue-500"
                />
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-800">{doc.filename}</h3>
                  <p className="text-sm text-gray-500">
                    {new Date(doc.upload_date).toLocaleDateString()} • {doc.chunk_count} chunks
                  </p>
                </div>
              </label>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default DocumentList;