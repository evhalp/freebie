# search/views.py
from django.shortcuts import render
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from posts.models import Post

def search_view(request):
    """Search posts with text, tag, and sort filters (20 per page)."""
    q = (request.GET.get('q') or '').strip()                # text query
    sort = (request.GET.get('sort') or 'popular').lower()   # 'popular' by default
    tag = (request.GET.get('tag') or 'all').lower()         # tag filter ('all' by default)
    page_raw = request.GET.get('page', '1')

    # Build the base queryset. This is how chatgpt recommends
    qs = (
        Post.objects.all()
        .select_related('user')
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

    # --- Filter by tag ---
    if tag != 'all':
        qs = qs.filter(tags__name__iexact=tag)

    # --- Sorting ---
    now = timezone.now()

    if sort == 'now':
        qs = qs.filter(start_time__lte=now, end_time__gte=now).order_by('-like_count', '-created_at')
    elif sort == 'new':
        qs = qs.order_by('-created_at', '-like_count')
    else:
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
        'tag': tag,               # ✅ pass tag to template
        'page_obj': page_obj,
        'paginator': paginator,
        'now': now,
    }

    return render(request, 'search/search.html', context)

#