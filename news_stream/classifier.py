from datetime import datetime
from groq_client import client

def classify_news_message(message):
    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"""
                Classify the following news message into one of the following categories:
                General News
                Historical Terrorism Event
                Current Terrorism Event

                News Message:
                "{message}"

                Provide category text (General News, Historical Terrorism Event or Current Terrorism Event) as the response without extra text."""
            }],
            model="llama3-8b-8192",
        )

        response = chat_completion.choices[0].message.content
        return response

    except Exception as e:
        print(f"Error during classification: {e}")
        return "Unknown"

def classify_event_by_date(date_str: str) -> str:
    try:
        article_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        current_date = datetime.now().date()
        if article_date < current_date:
            return "Historical Terrorism Event"
        else:
            return "Current Terrorism Event"
    except Exception as e:
        print(f"Error in date classification: {e}")
        return "Unknown"


import json


def extract_terrorism_event_details(title, content):
    clean_title = title.replace("\\", "")
    clean_content = content.replace("\\", "") if content else ""
    
    prompt = f"""
      Extract detailed information about the following news article. Please provide all relevant details such as:
#     - Date of Event
#     - Location (City, Country, Region)
#     - Type of Event (e.g., attack, protest, accident)
#     - Casualties (if available)
#     - Brief Summary

#     Respond in this JSON format:
#     {{
#         "date": {{"yyyy", "mm", "dd"}},
#         "location": {{
#             "city": "city" or "null",
#             "country": "country" or "null",
#             "region": "region" or "null"
#         }},
#         "target_type": "target type" or "null",
#         "attack_type": "attack type" or "null",
#         "weapon_type": "weapon type" or "null",
#         "terrorist_group": "terrorist group" or "null",
#         "number_of_terrorists": "number" or "null",
#         "casualties": {{
#             "dead": "number" or "null",
#             "injured": "number" or "null"
#         }},
#         "summary": "summary" or "null"
#     }}

#     News Message:
#     "{clean_title} {clean_content}"
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )

        response = chat_completion.choices[0].message.content
        if response.status_code == 200:
            data = response.json()  # Safely parse the response
        else:
            print(f"Error: {response.status_code}")
        print(f"Groq API Response: {response}") 

       
        response_cleaned = response.strip().strip('()')  
        if not response_cleaned:
            print("Error: No response from GroqAPI")
            return {
                "date": "null",
                "location": {"city": "null", "country": "null", "region": "null"},
                "target_type": "null",
                "attack_type": "null",
                "weapon_type": "null",
                "terrorist_group": "null",
                "number_of_terrorists": "null",
                "casualties": {"dead": "null", "injured": "null"},
                "summary": "null"
            }

        
        try:
            event_details = json.loads(response_cleaned)
        except json.JSONDecodeError:
            print("Error: Invalid JSON response after cleaning")
            event_details = {
                "date": "null",
                "location": {"city": "null", "country": "null", "region": "null"},
                "target_type": "null",
                "attack_type": "null",
                "weapon_type": "null",
                "terrorist_group": "null",
                "number_of_terrorists": "null",
                "casualties": {"dead": "null", "injured": "null"},
                "summary": "null"
            }

        print(f"Extracted Event Details: {json.dumps(event_details, indent=4)}")  # Debugging line
        return event_details

    except Exception as e:
        print(f"Error during event extraction: {e}")
        return {
            "date": "null",
            "location": {"city": "null", "country": "null", "region": "null"},
            "target_type": "null",
            "attack_type": "null",
            "weapon_type": "null",
            "terrorist_group": "null",
            "number_of_terrorists": "null",
            "casualties": {"dead": "null", "injured": "null"},
            "summary": "null"
        }
