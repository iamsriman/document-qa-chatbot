import { useState } from 'react';

function PaperCard({ paper, onSave, isImportant }) {
  const [saving, setSaving] = useState(false);
  const [showTopicModal, setShowTopicModal] = useState(false);
  const [topicName, setTopicName] = useState('');

  const handleSave = async () => {
    if (!topicName.trim()) {
      alert('Please enter a topic name');
      return;
    }
    
    setSaving(true);
    try {
      await onSave(paper, topicName);
      setShowTopicModal(false);
      setTopicName('');
    } catch (error) {
      console.error('Error saving paper:', error);
      alert('Failed to save paper');
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <div className={`bg-white p-6 rounded-lg shadow-md border-l-4 ${
        isImportant ? 'border-yellow-500 bg-yellow-50' : 'border-blue-500'
      }`}>
        {isImportant && (
          <span className="inline-block bg-yellow-500 text-white text-xs px-2 py-1 rounded mb-2">
            ⭐ Important
          </span>
        )}
        
        <h3 className="text-xl font-bold text-gray-800 mb-2">{paper.title}</h3>
        
        <p className="text-sm text-gray-600 mb-2">
          <span className="font-semibold">Authors:</span> {paper.authors}
        </p>
        
        <p className="text-sm text-gray-700 mb-3 line-clamp-3">{paper.abstract}</p>
        
        <div className="flex items-center gap-4 mb-3 text-sm text-gray-600">
          <span className="font-semibold">Year: {paper.year}</span>
          <span>📊 Citations: {paper.citations}</span>
          {paper.views > 0 && <span>👁️ Views: {paper.views}</span>}
          <span className="text-blue-600">Source: {paper.source}</span>
        </div>
        
        <div className="flex gap-3">
          {paper.pdf_link && paper.pdf_link !== null && (
            <a
              href={paper.pdf_link}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 text-sm"
            >
              📄 PDF
            </a>
          )}
          {paper.publisher_link && paper.publisher_link !== null && (
            <a
              href={paper.publisher_link}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 text-sm"
            >
              🔗 Publisher
            </a>
          )}
          <button
            onClick={() => setShowTopicModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm ml-auto"
          >
            💾 Save
          </button>
        </div>
      </div>

      {showTopicModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full">
            <h3 className="text-xl font-bold mb-4">Save to Topic</h3>
            <input
              type="text"
              value={topicName}
              onChange={(e) => setTopicName(e.target.value)}
              placeholder="Enter topic name (e.g., LLMs, RAG, NLP...)"
              className="w-full p-3 border border-gray-300 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
            />
            <div className="flex gap-3">
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
              <button
                onClick={() => setShowTopicModal(false)}
                className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default PaperCard;