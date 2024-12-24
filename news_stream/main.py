import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

url = "https://eventregistry.org/api/v1/article/getArticles"
params ={
    "action": "getArticles",
    "keyword": "terror attack",
    "ignoreSourceGroupUri": "paywall/paywalled_sources",
    "articlesPage": 1,
    "articlesCount": 1,
    "articlesSortBy": "socialScore",
    "articlesSortByAsc": False,
    "dataType": ["news", "pr"],
    "forceMaxDataTimeWindow": 31,
    "resultType": "articles",
    "apiKey": API_KEY,
}
def get_news():
    response = requests.get(url, params=params)
    print(f"HTTP Status Code: {response.status_code}")
    print(f"Response content: {response.text}")  # הדפסת תוכן התגובה
    
    if response.status_code == 200:
        try:
            data = response.json()
            if "articles" in data:
                return data["articles"]
            else:
                print(f"Error: {data.get('message', 'No articles found')}")
        except ValueError:
            print("Failed to decode JSON")
    else:
        print(f"Request failed with status code {response.status_code}")
    return []




while True:
    articles = get_news()
    for article in articles:
        print(article)
    time.sleep(120)
  
