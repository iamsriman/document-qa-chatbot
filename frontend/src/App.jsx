import { useState } from 'react';
import UploadDocument from './components/UploadDocument';
import DocumentList from './components/DocumentList';
import ChatInterface from './components/ChatInterface';

function App() {
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadSuccess = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  const handleSelectDocument = (document) => {
    setSelectedDocument(document);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <header className="bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg">
        <div className="container mx-auto p-6">
          <h1 className="text-4xl font-bold text-center">📄 Document Q&A Chatbot</h1>
          <p className="text-center text-blue-100 mt-2">Upload PDFs and ask questions using AI</p>
        </div>
      </header>

      <div className="container mx-auto p-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          <div className="lg:col-span-1 space-y-6">
            <UploadDocument onUploadSuccess={handleUploadSuccess} />
            <DocumentList
              onSelectDocument={handleSelectDocument}
              selectedDocumentId={selectedDocument?.id}
              refreshTrigger={refreshTrigger}
            />
          </div>

          <div className="lg:col-span-2" style={{ height: 'calc(100vh - 250px)' }}>
            <ChatInterface document={selectedDocument} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;