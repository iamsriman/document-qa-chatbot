import { useState } from 'react';
import SearchPage from './components/Search/SearchPage';
import ChatPage from './components/Chat/ChatPage';

function App() {
  const [activeTab, setActiveTab] = useState('search'); // 'search' or 'chat'

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold">📚 Research Paper Assistant</h1>
              <p className="text-blue-100 mt-2">Search, Save & Chat with Research Papers</p>
            </div>
            
            {/* Tab Navigation */}
            <div className="flex gap-4">
              <button
                onClick={() => setActiveTab('search')}
                className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                  activeTab === 'search'
                    ? 'bg-white text-blue-600 shadow-lg'
                    : 'bg-blue-500 text-white hover:bg-blue-400'
                }`}
              >
                🔍 Search Papers
              </button>
              <button
                onClick={() => setActiveTab('chat')}
                className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                  activeTab === 'chat'
                    ? 'bg-white text-blue-600 shadow-lg'
                    : 'bg-blue-500 text-white hover:bg-blue-400'
                }`}
              >
                💬 RAG Chat
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-6">
        {activeTab === 'search' ? <SearchPage /> : <ChatPage />}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white mt-12">
        <div className="container mx-auto px-6 py-4 text-center">
          <p className="text-sm">
            Built with ❤️ using React, FastAPI, LangChain & Gemini AI
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;