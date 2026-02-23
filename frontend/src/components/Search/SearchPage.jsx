import { useState } from 'react';
import PaperSearchBar from './PaperSearchBar';
import SearchResults from './SearchResults';
import SavedTopics from './SavedTopics';
import { searchPapers, savePaper } from '../../services/api';

function SearchPage() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [currentQuery, setCurrentQuery] = useState('');
  const [showSaved, setShowSaved] = useState(false);

  const PAPERS_PER_PAGE = 10;

  const handleSearch = async (query, page = 1) => {
    setLoading(true);
    setCurrentQuery(query);
    setCurrentPage(page);
    
    try {
      const offset = (page - 1) * PAPERS_PER_PAGE;
      const data = await searchPapers(query, PAPERS_PER_PAGE, offset);
      setPapers(data.papers);
      
      // Calculate total pages (assuming we can get more results)
      setTotalPages(Math.ceil(data.total / PAPERS_PER_PAGE) || 1);
    } catch (error) {
      console.error('Error searching papers:', error);
      alert('Failed to search papers. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePaper = async (paper, topicName) => {
    try {
      await savePaper(paper, topicName);
      alert(`Paper saved to topic "${topicName}"`);
    } catch (error) {
      console.error('Error saving paper:', error);
      throw error;
    }
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      handleSearch(currentQuery, newPage);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Toggle Button */}
        <div className="flex justify-end mb-4">
          <button
            onClick={() => setShowSaved(!showSaved)}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            {showSaved ? '🔍 Search Papers' : '📚 Saved Papers'}
          </button>
        </div>

        {showSaved ? (
          <SavedTopics />
        ) : (
          <div className="space-y-6">
            <PaperSearchBar onSearch={(q) => handleSearch(q, 1)} loading={loading} />
            
            {loading ? (
              <div className="bg-white p-6 rounded-lg shadow-md text-center">
                <p className="text-gray-500">Searching papers...</p>
              </div>
            ) : papers.length > 0 ? (
              <SearchResults
                papers={papers}
                onSave={handleSavePaper}
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={handlePageChange}
              />
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}

export default SearchPage;