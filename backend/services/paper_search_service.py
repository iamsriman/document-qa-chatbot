import requests
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class PaperSearchService:
    def __init__(self):
        self.semantic_scholar_api = "https://api.semanticscholar.org/graph/v1/paper/search"
        self.arxiv_api = "http://export.arxiv.org/api/query"
    
    def search_papers(self, query: str, limit: int = 10, offset: int = 0) -> List[Dict]:
        """
        Search for research papers from multiple sources
        """
        papers = []
        
        # Search Semantic Scholar
        semantic_papers = self._search_semantic_scholar(query, limit, offset)
        papers.extend(semantic_papers)
        
        # If not enough results, search arXiv
        if len(papers) < limit:
            arxiv_papers = self._search_arxiv(query, limit - len(papers))
            papers.extend(arxiv_papers)
        
        return papers[:limit]
    
    def _search_semantic_scholar(self, query: str, limit: int, offset: int) -> List[Dict]:
        """
        Search Semantic Scholar API
        """
        try:
            params = {
                'query': query,
                'limit': limit,
                'offset': offset,
                'fields': 'title,authors,abstract,year,citationCount,openAccessPdf,externalIds,publicationVenue'
            }
            
            response = requests.get(self.semantic_scholar_api, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            papers = []
            
            for paper in data.get('data', []):
                # Get PDF link
                pdf_link = None
                if paper.get('openAccessPdf'):
                    pdf_link = paper['openAccessPdf'].get('url')
                
                # Get publisher link
                publisher_link = None
                if paper.get('externalIds'):
                    doi = paper['externalIds'].get('DOI')
                    if doi:
                        publisher_link = f"https://doi.org/{doi}"
                
                # Get authors
                authors = ", ".join([author.get('name', '') for author in paper.get('authors', [])])
                
                papers.append({
                    'title': paper.get('title', 'No title'),
                    'authors': authors or 'Unknown',
                    'abstract': paper.get('abstract', 'No abstract available')[:500] + '...',
                    'year': paper.get('year', 0),
                    'citations': paper.get('citationCount', 0),
                    'views': 0,  # Semantic Scholar doesn't provide views
                    'pdf_link': pdf_link,
                    'publisher_link': publisher_link,
                    'source': 'Semantic Scholar'
                })
            
            return papers
        
        except Exception as e:
            print(f"Error searching Semantic Scholar: {e}")
            return []
    
    def _search_arxiv(self, query: str, limit: int) -> List[Dict]:
        """
        Search arXiv API
        """
        try:
            params = {
                'search_query': f'all:{query}',
                'start': 0,
                'max_results': limit,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            response = requests.get(self.arxiv_api, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            # Define namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            papers = []
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns).text.strip()
                authors = ", ".join([author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)])
                abstract = entry.find('atom:summary', ns).text.strip()[:500] + '...'
                published = entry.find('atom:published', ns).text[:4]  # Extract year
                
                # Get PDF link
                pdf_link = None
                for link in entry.findall('atom:link', ns):
                    if link.get('title') == 'pdf':
                        pdf_link = link.get('href')
                        break
                
                # Get publisher link
                publisher_link = entry.find('atom:id', ns).text
                
                papers.append({
                    'title': title,
                    'authors': authors,
                    'abstract': abstract,
                    'year': int(published),
                    'citations': 0,  # arXiv doesn't provide citations
                    'views': 0,
                    'pdf_link': pdf_link,
                    'publisher_link': publisher_link,
                    'source': 'arXiv'
                })
            
            return papers
        
        except Exception as e:
            print(f"Error searching arXiv: {e}")
            return []