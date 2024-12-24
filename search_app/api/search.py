from datetime import datetime

def search_keywords(keywords, limit=10):

    results = []
 
    return results[:limit]


def search_news(limit=10):
 
    results = []

    return results[:limit]


def search_historic(limit=10):

    results = []

    return results[:limit]


def search_combined(start_date, end_date, limit=10):

    results = []
    if start_date and end_date:

        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    return results[:limit]
