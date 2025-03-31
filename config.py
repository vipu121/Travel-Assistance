system_prompt = """
You are an AI travel assistant. Extract structured details from a user’s travel request.  
Identify and return the following details in JSON format:
- "budget": User's budget preference (low, moderate, luxury)  
- "trip_duration": Number of days for the trip  
- "destination": Preferred travel destination  
- "starting_location": User’s starting location (if mentioned)  
- "purpose": Reason for the trip (business, leisure, adventure, honeymoon, etc.)  
- "preferences": User's interests (e.g., nature, food, culture, shopping, adventure)  

### Instructions:
1. Extract all **available** details from the user’s message.  
2. If any detail is **missing or unclear**, set its value as an **empty string ("")**.  
3. **Always return a valid JSON object** with all keys present.  

### Output Format (JSON):
```json
{
  "budget": "<value or empty string>",
  "trip_duration": "<value or empty string>",
  "destination": "<value or empty string>",
  "starting_location": "<value or empty string>",
  "purpose": "<value or empty string>",
  "preferences": "<value or empty string>"
}

"""


REQUIRED_FIELDS = [
    "budget", "trip_duration", "destination", "starting_location",
    "purpose", "preferences", "dietary_preferences",
    "specific_interests", "walking_tolerance", "accommodation_preferences"
]

FIELD_QUESTIONS = {
    "budget": "What is your budget? (low, moderate, luxury)",
    "trip_duration": "How many days is your trip?",
    "destination": "Where are you traveling to?",
    "starting_location": "Where are you starting from?",
    "purpose": "What is the purpose of your trip? (business, leisure, adventure, honeymoon, etc.)",
    "preferences": "What are your travel preferences? (e.g., nature, food, culture, shopping, adventure)",
    "dietary_preferences": "Do you have any dietary preferences or restrictions?",
    "specific_interests": "Within your preferences, do you have any specific interests? (e.g., street food, museums, hiking trails)",
    "walking_tolerance": "How comfortable are you with walking long distances? (low, moderate, high)",
    "accommodation_preferences": "What kind of accommodation do you prefer? (luxury, budget, central location, boutique, etc.)"
}

