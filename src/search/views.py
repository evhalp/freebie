#CHAT GPTed BASIC RENDER

# search/views.py
from django.shortcuts import render

# pretend we have a database of items
ITEMS = [
    {"name": "Apple", "description": "A red fruit"},
    {"name": "Banana", "description": "A yellow fruit"},
    {"name": "Carrot", "description": "An orange vegetable"},
]

def search_view(request):
    """Display the search form."""
    return render(request, 'search/search.html')

def results_view(request):
    """Show results based on search query."""
    query = request.GET.get('q', '')  # get ?q= from URL
    results = [item for item in ITEMS if query.lower() in item["name"].lower()] if query else []
    return render(request, 'search/results.html', {"query": query, "results": results})