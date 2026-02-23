import PaperCard from './PaperCard';

function SearchResults({ papers, onSave, currentPage, totalPages, onPageChange }) {
  if (papers.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md text-center">
        <p className="text-gray-500">No papers found. Try a different search query.</p>
      </div>
    );
  }

  // Identify important papers (first 2-3 papers)
  const importantCount = Math.min(3, papers.length);

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 p-4 rounded-lg">
        <h3 className="font-bold text-blue-900 mb-2">⭐ Top Results</h3>
        <p className="text-sm text-blue-700">
          Showing {papers.length} papers • Page {currentPage} of {totalPages}
        </p>
      </div>

      {papers.map((paper, index) => (
        <PaperCard
          key={index}
          paper={paper}
          onSave={onSave}
          isImportant={index < importantCount}
        />
      ))}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center gap-2 mt-6">
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="px-4 py-2 bg-gray-200 rounded">
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

export default SearchResults;