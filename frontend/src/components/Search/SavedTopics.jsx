import { useState, useEffect } from 'react';
import { getTopics, getTopicPapers, deletePaper } from '../../services/api';

function SavedTopics() {
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTopics();
  }, []);

  const fetchTopics = async () => {
    try {
      const data = await getTopics();
      setTopics(data);
    } catch (error) {
      console.error('Error fetching topics:', error);
    }
  };

  const handleTopicClick = async (topic) => {
    setSelectedTopic(topic);
    setLoading(true);
    try {
      const data = await getTopicPapers(topic.id);
      setPapers(data);
    } catch (error) {
      console.error('Error fetching papers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePaper = async (paperId) => {
    if (window.confirm('Are you sure you want to delete this paper?')) {
      try {
        await deletePaper(paperId);
        setPapers(papers.filter(p => p.id !== paperId));
      } catch (error) {
        console.error('Error deleting paper:', error);
      }
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4">📚 Saved Topics</h2>
      
      {topics.length === 0 ? (
        <p className="text-gray-500">No saved topics yet. Start searching and saving papers!</p>
      ) : (
        <div className="space-y-2">
          {topics.map((topic) => (
            <div
              key={topic.id}
              onClick={() => handleTopicClick(topic)}
              className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                selectedTopic?.id === topic.id
                  ? 'bg-blue-50 border-blue-500'
                  : 'hover:bg-gray-50 border-gray-200'
              }`}
            >
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-semibold text-gray-800">{topic.name}</h3>
                  <p className="text-sm text-gray-500">{topic.paper_count} papers saved</p>
                </div>
                <span className="text-blue-600">→</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedTopic && (
        <div className="mt-6 border-t pt-6">
          <h3 className="text-xl font-bold mb-4">
            Papers in "{selectedTopic.name}" ({papers.length})
          </h3>
          
          {loading ? (
            <p className="text-gray-500">Loading papers...</p>
          ) : papers.length === 0 ? (
            <p className="text-gray-500">No papers in this topic.</p>
          ) : (
            <div className="space-y-4">
              {papers.map((paper) => (
                <div key={paper.id} className="p-4 border rounded-lg bg-gray-50">
                  <h4 className="font-semibold text-gray-800 mb-2">{paper.title}</h4>
                  <p className="text-sm text-gray-600 mb-2">{paper.authors}</p>
                  <p className="text-sm text-gray-700 mb-3 line-clamp-2">{paper.abstract}</p>
                  
                  <div className="flex items-center gap-3 text-sm text-gray-600 mb-3">
                    <span>Year: {paper.year}</span>
                    <span>📊 {paper.citations} citations</span>
                  </div>
                  
                  <div className="flex gap-2">
                    {paper.pdf_link && paper.pdf_link !== null && (
                      <a
                        href={paper.pdf_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                      >
                        📄 PDF
                      </a>
                    )}
                    {paper.publisher_link && paper.publisher_link !== null && (
                      <a
                        href={paper.publisher_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                      >
                        🔗 Link
                      </a>
                    )}
                    <button
                      onClick={() => handleDeletePaper(paper.id)}
                      className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600 ml-auto"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default SavedTopics;