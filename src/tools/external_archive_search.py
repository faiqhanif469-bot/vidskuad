"""
External Archive Search
Search non-YouTube archives: Archive.org, NASA Images, National Archives, etc.
"""

import requests
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ArchiveSource:
    """External archive source information"""
    name: str
    base_url: str
    api_endpoint: str
    search_type: str  # 'api', 'scrape', 'manual'
    license: str
    best_for: List[str]


class ExternalArchiveSearch:
    """Search external archives beyond YouTube"""
    
    def __init__(self):
        self.sources = self._load_sources()
    
    def _load_sources(self) -> List[ArchiveSource]:
        """Load external archive sources"""
        return [
            ArchiveSource(
                name="Internet Archive",
                base_url="https://archive.org",
                api_endpoint="https://archive.org/advancedsearch.php",
                search_type="api",
                license="Public Domain / Creative Commons",
                best_for=["historical footage", "rare content", "diverse topics"]
            ),
            ArchiveSource(
                name="NASA Images",
                base_url="https://images.nasa.gov",
                api_endpoint="https://images.nasa.gov/search",
                search_type="api",
                license="Public Domain",
                best_for=["space", "astronomy", "NASA missions", "science"]
            ),
            ArchiveSource(
                name="National Archives Catalog",
                base_url="https://catalog.archives.gov",
                api_endpoint="https://catalog.archives.gov/api/v1",
                search_type="api",
                license="Public Domain",
                best_for=["US government", "military", "historical events", "politics"]
            ),
            ArchiveSource(
                name="Wikimedia Commons",
                base_url="https://commons.wikimedia.org",
                api_endpoint="https://commons.wikimedia.org/w/api.php",
                search_type="api",
                license="Various (mostly CC)",
                best_for=["general content", "international", "diverse topics"]
            ),
            ArchiveSource(
                name="Critical Past",
                base_url="https://www.criticalpast.com",
                api_endpoint="",
                search_type="manual",  # Requires account/payment
                license="Royalty-free (paid)",
                best_for=["premium historical footage", "high quality"]
            ),
        ]
    
    def search_archive_org(
        self, 
        query: str, 
        media_type: str = "movies",
        max_results: int = 20
    ) -> List[Dict]:
        """
        Search Internet Archive for videos
        
        Args:
            query: Search query
            media_type: Type of media (movies, audio, etc.)
            max_results: Maximum results to return
        
        Returns:
            List of video metadata dicts
        """
        logger.info(f"Searching Archive.org for: {query}")
        
        try:
            # Archive.org Advanced Search API
            params = {
                'q': f'{query} AND mediatype:{media_type}',
                'fl[]': ['identifier', 'title', 'description', 'date', 'creator', 'subject'],
                'rows': max_results,
                'page': 1,
                'output': 'json',
                'sort[]': 'downloads desc'  # Most popular first
            }
            
            response = requests.get(
                "https://archive.org/advancedsearch.php",
                params=params,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Archive.org API error: {response.status_code}")
                return []
            
            data = response.json()
            docs = data.get('response', {}).get('docs', [])
            
            results = []
            for doc in docs:
                identifier = doc.get('identifier', '')
                results.append({
                    'source': 'archive.org',
                    'id': identifier,
                    'title': doc.get('title', ''),
                    'description': doc.get('description', ''),
                    'date': doc.get('date', ''),
                    'creator': doc.get('creator', ''),
                    'subjects': doc.get('subject', []),
                    'url': f"https://archive.org/details/{identifier}",
                    'embed_url': f"https://archive.org/embed/{identifier}",
                    'download_url': f"https://archive.org/download/{identifier}",
                    'license': 'Public Domain / Creative Commons'
                })
            
            logger.info(f"Found {len(results)} results from Archive.org")
            return results
            
        except Exception as e:
            logger.error(f"Error searching Archive.org: {e}")
            return []
    
    def search_nasa_images(
        self, 
        query: str,
        media_type: str = "video",
        max_results: int = 20
    ) -> List[Dict]:
        """
        Search NASA Images API for videos
        
        Args:
            query: Search query
            media_type: Type of media (video, image, audio)
            max_results: Maximum results to return
        
        Returns:
            List of video metadata dicts
        """
        logger.info(f"Searching NASA Images for: {query}")
        
        try:
            params = {
                'q': query,
                'media_type': media_type,
                'page_size': max_results
            }
            
            response = requests.get(
                "https://images-api.nasa.gov/search",
                params=params,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"NASA API error: {response.status_code}")
                return []
            
            data = response.json()
            items = data.get('collection', {}).get('items', [])
            
            results = []
            for item in items:
                item_data = item.get('data', [{}])[0]
                links = item.get('links', [{}])
                
                # Get preview/thumbnail
                preview_url = links[0].get('href', '') if links else ''
                
                nasa_id = item_data.get('nasa_id', '')
                
                results.append({
                    'source': 'nasa',
                    'id': nasa_id,
                    'title': item_data.get('title', ''),
                    'description': item_data.get('description', ''),
                    'date': item_data.get('date_created', ''),
                    'center': item_data.get('center', ''),
                    'keywords': item_data.get('keywords', []),
                    'preview_url': preview_url,
                    'url': f"https://images.nasa.gov/details/{nasa_id}",
                    'license': 'Public Domain'
                })
            
            logger.info(f"Found {len(results)} results from NASA")
            return results
            
        except Exception as e:
            logger.error(f"Error searching NASA: {e}")
            return []
    
    def search_national_archives(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Search National Archives Catalog
        
        Args:
            query: Search query
            max_results: Maximum results to return
        
        Returns:
            List of video metadata dicts
        """
        logger.info(f"Searching National Archives for: {query}")
        
        try:
            # National Archives API v1
            params = {
                'q': query,
                'rows': max_results,
                'type': 'description',
                'resultTypes': 'item',
                'format': 'json'
            }
            
            response = requests.get(
                "https://catalog.archives.gov/api/v1",
                params=params,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"National Archives API error: {response.status_code}")
                return []
            
            data = response.json()
            results_data = data.get('opaResponse', {}).get('results', {}).get('result', [])
            
            results = []
            for item in results_data:
                desc = item.get('description', {})
                
                results.append({
                    'source': 'national_archives',
                    'id': item.get('naId', ''),
                    'title': desc.get('title', ''),
                    'description': desc.get('scopeAndContent', ''),
                    'date': desc.get('productionDate', ''),
                    'creator': desc.get('creator', ''),
                    'url': f"https://catalog.archives.gov/id/{item.get('naId', '')}",
                    'license': 'Public Domain'
                })
            
            logger.info(f"Found {len(results)} results from National Archives")
            return results
            
        except Exception as e:
            logger.error(f"Error searching National Archives: {e}")
            return []
    
    def search_wikimedia_commons(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Search Wikimedia Commons for videos
        
        Args:
            query: Search query
            max_results: Maximum results to return
        
        Returns:
            List of video metadata dicts
        """
        logger.info(f"Searching Wikimedia Commons for: {query}")
        
        try:
            # Wikimedia Commons API
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': f'{query} filetype:video',
                'srnamespace': 6,  # File namespace
                'srlimit': max_results
            }
            
            response = requests.get(
                "https://commons.wikimedia.org/w/api.php",
                params=params,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Wikimedia API error: {response.status_code}")
                return []
            
            data = response.json()
            search_results = data.get('query', {}).get('search', [])
            
            results = []
            for item in search_results:
                title = item.get('title', '')
                page_id = item.get('pageid', '')
                
                results.append({
                    'source': 'wikimedia',
                    'id': page_id,
                    'title': title.replace('File:', ''),
                    'snippet': item.get('snippet', ''),
                    'url': f"https://commons.wikimedia.org/wiki/{title.replace(' ', '_')}",
                    'license': 'Various (check individual file)'
                })
            
            logger.info(f"Found {len(results)} results from Wikimedia Commons")
            return results
            
        except Exception as e:
            logger.error(f"Error searching Wikimedia Commons: {e}")
            return []
    
    def search_all_sources(
        self,
        query: str,
        max_results_per_source: int = 10
    ) -> Dict[str, List[Dict]]:
        """
        Search all external archives
        
        Args:
            query: Search query
            max_results_per_source: Max results per source
        
        Returns:
            Dict mapping source name to results list
        """
        logger.info(f"Searching all external archives for: {query}")
        
        results = {}
        
        # Search Archive.org
        results['archive_org'] = self.search_archive_org(query, max_results=max_results_per_source)
        
        # Search NASA
        results['nasa'] = self.search_nasa_images(query, max_results=max_results_per_source)
        
        # Search National Archives
        results['national_archives'] = self.search_national_archives(query, max_results=max_results_per_source)
        
        # Search Wikimedia Commons
        results['wikimedia'] = self.search_wikimedia_commons(query, max_results=max_results_per_source)
        
        # Summary
        total = sum(len(v) for v in results.values())
        logger.info(f"Total results from all sources: {total}")
        
        return results


if __name__ == '__main__':
    # Test the search
    searcher = ExternalArchiveSearch()
    
    print("Testing Archive.org search...")
    results = searcher.search_archive_org("space race", max_results=5)
    print(f"Found {len(results)} results")
    if results:
        print(f"First result: {results[0]['title']}")
    
    print("\nTesting NASA search...")
    results = searcher.search_nasa_images("apollo moon", max_results=5)
    print(f"Found {len(results)} results")
    if results:
        print(f"First result: {results[0]['title']}")
