from groq import Groq
import json
import os
from dotenv import load_dotenv


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def extract_terrorism_event_details(title, content):
    clean_title = title.replace("\\", "")
    clean_content = content.replace("\\", "") if content else ""

    prompt = f"""
    Extract detailed information about the following news article. Please provide all relevant details such as:
    - Date of Event
    - Location (City, Country, Region)
    - Type of Event (e.g., attack, protest, accident)
    - Casualties (if available)
    - Brief Summary

    Respond in this JSON format:
    {{
        "date": {{"yyyy", "mm", "dd"}},
        "location": {{
            "city": "city" or "null",
            "country": "country" or "null",
            "region": "region" or "null"
        }},
        "target_type": "target type" or "null",
        "attack_type": "attack type" or "null",
        "weapon_type": "weapon type" or "null",
        "terrorist_group": "terrorist group" or "null",
        "number_of_terrorists": "number" or "null",
        "casualties": {{
            "dead": "number" or "null",
            "injured": "number" or "null"
        }},
        "summary": "summary" or "null"
    }}

    News Message:
    "{clean_title} {clean_content}"
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )

        response = chat_completion.choices[0].message.content
        response_cleaned = response.strip().strip('()')
        event_details = json.loads(response_cleaned)
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
