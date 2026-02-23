import { useState, useEffect } from 'react';
import { getSessions, deleteSession } from '../../services/api';

function SessionManager({ onSessionSelect, selectedSessionId }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const data = await getSessions();
      setSessions(data);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (sessionId, e) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this chat session?')) {
      try {
        await deleteSession(sessionId);
        setSessions(sessions.filter(s => s.id !== sessionId));
        if (selectedSessionId === sessionId) {
          onSessionSelect(null);
        }
      } catch (error) {
        console.error('Error deleting session:', error);
      }
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4">💬 My Chat Sessions</h2>
      
      {loading ? (
        <p className="text-gray-500">Loading sessions...</p>
      ) : sessions.length === 0 ? (
        <p className="text-gray-500">No chat sessions yet. Create one to get started!</p>
      ) : (
        <div className="space-y-2">
          {sessions.map((session) => (
            <div
              key={session.id}
              onClick={() => onSessionSelect(session)}
              className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                selectedSessionId === session.id
                  ? 'bg-blue-50 border-blue-500'
                  : 'hover:bg-gray-50 border-gray-200'
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-800">{session.name}</h3>
                  <p className="text-sm text-gray-500">
                    {new Date(session.created_date).toLocaleDateString()} • {session.document_count} documents
                  </p>
                </div>
                <button
                  onClick={(e) => handleDelete(session.id, e)}
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

export default SessionManager;