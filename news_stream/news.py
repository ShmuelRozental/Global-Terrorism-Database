import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = os.getenv("NEWS_API_URL")

def get_news():

    news_params = {
        "action": "getArticles",
        "keyword": "terror attack",
        "ignoreSourceGroupUri": "paywall/paywalled_sources",
        "articlesPage": 1,
        "articlesCount": 10, 
        "articlesSortBy": "socialScore",
        "articlesSortByAsc": False,
        "dataType": ["news", "pr"],
        "forceMaxDataTimeWindow": 31,
        "resultType": "articles",
        "apiKey": NEWS_API_KEY,
    }

    response = requests.get(NEWS_API_URL, params=news_params)
    if response.status_code == 200:
        try:
            data = response.json()
            articles = data.get("articles", {}).get("results", [])
            return articles
        except ValueError:
            print("Failed to decode JSON")
    else:
        print(f"Request failed with status code {response.status_code}")
    return []
