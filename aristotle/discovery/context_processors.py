from datetime import datetime

def search_history(request):
    context_extras = {}
    # This dependence on the url is fragile, but necessary to drop the
    # current search when we're on the search page.
    #if '/search' in request.path:
    #    search_hist = request.session.get('search_history')[1:]
    #else:
    search_hist = request.session.get('search_history')
    context_extras['search_history'] = search_hist
    try:
        last_search = search_hist[0][0]
    except TypeError:
        last_search = None
    context_extras['last_search'] = last_search
    return context_extras
