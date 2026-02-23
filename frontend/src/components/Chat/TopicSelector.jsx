import { useState, useEffect } from 'react';
import { getTopics } from '../../services/api';

function TopicSelector({ onTopicSelect, selectedTopicId }) {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTopics();
  }, []);

  const fetchTopics = async () => {
    setLoading(true);
    try {
      const data = await getTopics();
      setTopics(data);
    } catch (error) {
      console.error('Error fetching topics:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4">📁 Select Topic</h2>
      
      {loading ? (
        <p className="text-gray-500">Loading topics...</p>
      ) : topics.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">No topics available</p>
          <p className="text-sm text-gray-400">
            Go to Search page to save some papers first
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {topics.map((topic) => (
            <div
              key={topic.id}
              onClick={() => onTopicSelect(topic)}
              className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                selectedTopicId === topic.id
                  ? 'bg-blue-50 border-blue-500'
                  : 'hover:bg-gray-50 border-gray-200'
              }`}
            >
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-semibold text-gray-800">{topic.name}</h3>
                  <p className="text-sm text-gray-500">
                    {topic.paper_count} papers available
                  </p>
                </div>
                {selectedTopicId === topic.id && (
                  <span className="text-blue-600 font-bold">✓</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default TopicSelector;