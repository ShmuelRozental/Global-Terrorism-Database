import json

def handle_json_error(response):
    try:
        response_cleaned = response.strip().strip('()')
        return json.loads(response_cleaned)
    except json.JSONDecodeError:
        print("Error: Invalid JSON response")
        return {}
