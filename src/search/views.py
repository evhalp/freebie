# search/views.py
from django.shortcuts import render
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from posts.models import Post


def search_view(request):
    """Search posts with optional text + sort filters and 20 posts per page ."""
    q = (request.GET.get('q') or '').strip()                # text query ('' if empty search)
    sort = (request.GET.get('sort') or 'popular').lower()   # 'popular' by default | 'now' | 'new'
    page_raw = request.GET.get('page', '1')                 # page number as string. default is '1'

    # --- Build the base queryset, how chatgpt recommends ---
    qs = (
        Post.objects.all()                            # searches all posts
        .select_related('user')                       # pull user in same query for speed
        .prefetch_related('tags')                     # fetch tags efficiently
        .annotate(                                    # creates like_count in SQL that can be used like a variable.
            like_count=Count(
                'reactions',
                filter=Q(reactions__sentiment='LIKE'),
                distinct=True
            )
        )
    )

    # --- Apply search (title or description) ---
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        ).distinct()                            # stops duplicates

    # --- Filters/sorting ---
    now = timezone.now()

    if sort == 'now':
        # Only events happening now: start_time <= now <= end_time
        qs = qs.filter(start_time__lte=now, end_time__gte=now) \
               .order_by('-like_count', '-created_at')      # sort by like count and break ties with time created
    elif sort == 'new':
        # Newest posts first
        qs = qs.order_by('-created_at', '-like_count')      # sort by time created and break ties with like count
    else:
        # Default 'popular'
        qs = qs.order_by('-like_count', '-created_at')      # sort by like count and break ties with time created

    # --- 20 results per page ---
    paginator = Paginator(qs, 20)                     # Built in django page separation. 20 per page
    try:
        page_number = int(page_raw)                   # get page number
    except ValueError:
        page_number = 1                               # if getting page number errors, it's the first page

    try:
        page_obj = paginator.page(page_number)        # the current page object
    except PageNotAnInteger:
        page_obj = paginator.page(1)                  # if not an integer,y fallback to page 1
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)  # if out of page range, fallback to last page

    # --- Render template with everything the UI needs ---
    context = {
        'query': q,             # the search text the user typed in the box
        'sort': sort,           # how we’re sorting results (popular, now, or new)
        'page_obj': page_obj,   # the current page of results (20 posts per page)
        'paginator': paginator, # helper object that knows total pages & results
        'now': now,             # the current time (used for "happening now" logic)
    }

    return render(request, 'search/search.html', context)
