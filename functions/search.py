import requests
import json
from config import SERPER_API_KEY
from models import SearchResult

def google_search(query: str) -> SearchResult:
    """Perform a Google search using Serper.dev API"""
    print("Get result from Google search using google_search")
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, data=payload)
    response.raise_for_status()
    
    results = response.json()
    
    if not results.get('organic'):
        raise ValueError("No search results found.")
    
    first_result = results['organic'][0]
    return SearchResult(
        title=first_result.get('title', 'No title'),
        link=first_result.get('link', 'No link'),
        snippet=first_result.get('snippet', 'No snippet available.')
    )
