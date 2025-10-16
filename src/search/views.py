#CHAT GPTed BASIC RENDER

# search/views.py
from django.shortcuts import render
from posts.models import Post
from django.db.models import Q


def search_view(request):
    """Display the search form."""
    query = request.GET.get('q')
    results = []

    if query:
        results = Post.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)).distinct

    else:
        results = Post.objects.all()
    
    print("TEST")

    context = {
        'query': query,
        'results': results
    }


    return render(request, 'search/search.html', context)

