# search/views.py
from django.shortcuts import render
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from posts.models import Post, Tag

def search_view(request):
    """Search posts with text, tag, and sort filters (20 per page)."""
    q = (request.GET.get('q') or '').strip()                # text query
    # Default to 'for_you' which orders results by author credibility
    sort = (request.GET.get('sort') or 'for_you').lower()
    tag = (request.GET.get('tag') or 'all').lower()         # tag filter ('all' by default)
    page_raw = request.GET.get('page', '1')

    # Build the base queryset. This is how chatgpt recommends
    qs = (
        Post.objects.all()
        # include user and user profile so we can sort by credibility efficiently
        .select_related('user', 'user__userprofile')
        .prefetch_related('tags')
        .annotate(
            like_count=Count(
                'reactions',
                filter=Q(reactions__sentiment='LIKE'),
                distinct=True
            )
        )
    )

    # Apply search (title or description)
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
            | Q(tags__name__icontains=q) | Q(tags__slug__icontains=q)
        ).distinct()                            # stops duplicates

    # --- Tags ---
    if tag != 'all':
        qs = qs.filter(tags__slug__iexact=tag)

    tags = Tag.objects.all().order_by('name')

    # --- Sorting ---
    now = timezone.now()

    if sort == 'now':
        # happening now: show events happening now ordered by author credibility first
        qs = qs.filter(start_time__lte=now, end_time__gte=now).order_by(
            '-user__userprofile__credibility', '-like_count', '-created_at'
        )
    elif sort == 'new':
        qs = qs.order_by('-created_at', '-like_count')
    elif sort == 'for_you':
        # For You: default ranking by author credibility, then popularity, then recency
        qs = qs.order_by('-user__userprofile__credibility', '-like_count', '-created_at')
    else:
        # fallback to popular
        qs = qs.order_by('-like_count', '-created_at')

    # 20 results per page
    paginator = Paginator(qs, 20)                     # Built in django page separation. 20 per page
    try:
        page_number = int(page_raw)
    except ValueError:
        page_number = 1

    try:
        page_obj = paginator.page(page_number)        # the current page object
    except PageNotAnInteger:
        page_obj = paginator.page(1)                  # if not an integer, fallback to page 1
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)  # if out of page range, fallback to last page

    # --- Context ---
    context = {
        'query': q,
        'sort': sort,
        'tag': tag,
        'page_obj': page_obj,
        'paginator': paginator,
        'now': now,
        'tags': tags
    }

    return render(request, 'search/search.html', context)

#