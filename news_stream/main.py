from classifier import classify_news_message, classify_event_by_date
from groq_client import extract_terrorism_event_details
import json

from news import get_news

def process_news_articles():
    articles = get_news()
    processed_articles = []

    for article in articles:
        title = article.get("title", "No Title")
        body = article.get("body", "")
        date = article.get("date", "")

        category = classify_news_message(body)
        date_category = classify_event_by_date(date)
        event_details = extract_terrorism_event_details(title, body)

        processed_articles.append({
            "title": title,
            "url": article.get("url", "No URL"),
            "category": category,
            "date_category": date_category,
            "location": event_details.get("location", {}),
            "target_type": event_details.get("target_type", "null"),
            "attack_type": event_details.get("attack_type", "null"),
            "weapon_type": event_details.get("weapon_type", "null"),
            "terrorist_group": event_details.get("terrorist_group", "null"),
            "number_of_terrorists": event_details.get("number_of_terrorists", "null"),
            "casualties": event_details.get("casualties", {}),
            "summary": event_details.get("summary", "null"),
            "date": event_details.get("date", "null")
        })

    return processed_articles

if __name__ == "__main__":
    results = process_news_articles()
    for result in results:
        print(json.dumps(result, indent=4))
