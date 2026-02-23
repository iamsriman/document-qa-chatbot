import { useState } from 'react';
import TopicSelector from './TopicSelector';
import DocumentUploader from './DocumentUploader';
import DocumentList from './DocumentList';
import SessionManager from './SessionManager';
import MultiDocChat from './MultiDocChat';
import { createSession } from '../../services/api';

function ChatPage() {
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [showNewSession, setShowNewSession] = useState(true);

  const handleTopicSelect = (topic) => {
    setSelectedTopic(topic);
    setSelectedDocuments([]);
  };

  const handleDocumentToggle = (docId) => {
    setSelectedDocuments((prev) =>
      prev.includes(docId)
        ? prev.filter((id) => id !== docId)
        : [...prev, docId]
    );
  };

  const handleUploadSuccess = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  const handleCreateSession = async () => {
    if (selectedDocuments.length < 2) {
      alert('Please select at least 2 documents');
      return;
    }

    if (selectedDocuments.length > 5) {
      alert('You can select maximum 5 documents');
      return;
    }

    const sessionName = prompt('Enter a name for this chat session:');
    if (!sessionName) return;

    try {
      const result = await createSession(sessionName, selectedDocuments);
      alert('Session created successfully!');
      
      // Switch to session view
      setShowNewSession(false);
      setRefreshTrigger((prev) => prev + 1);
      
      // Clear selections
      setSelectedDocuments([]);
    } catch (error) {
      console.error('Error creating session:', error);
      alert('Failed to create session. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Toggle Button */}
        <div className="flex justify-end mb-4">
          <button
            onClick={() => setShowNewSession(!showNewSession)}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            {showNewSession ? '💬 My Sessions' : '➕ New Session'}
          </button>
        </div>

        {showNewSession ? (
          /* New Session Creation */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="space-y-6">
              <TopicSelector
                onTopicSelect={handleTopicSelect}
                selectedTopicId={selectedTopic?.id}
              />
              <DocumentUploader
                topicId={selectedTopic?.id}
                onUploadSuccess={handleUploadSuccess}
              />
            </div>

            <div className="lg:col-span-2 space-y-6">
              <DocumentList
                topicId={selectedTopic?.id}
                selectedDocuments={selectedDocuments}
                onDocumentToggle={handleDocumentToggle}
                refreshTrigger={refreshTrigger}
              />

              {selectedDocuments.length >= 2 && (
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="text-lg font-bold text-gray-800">
                        Ready to create session
                      </h3>
                      <p className="text-sm text-gray-600">
                        {selectedDocuments.length} documents selected
                      </p>
                    </div>
                    <button
                      onClick={handleCreateSession}
                      className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors font-medium"
                    >
                      Create Chat Session
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          /* Chat Sessions View */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div>
              <SessionManager
                onSessionSelect={setSelectedSession}
                selectedSessionId={selectedSession?.id}
              />
            </div>

            <div className="lg:col-span-2" style={{ height: 'calc(100vh - 200px)' }}>
              <MultiDocChat session={selectedSession} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatPage;