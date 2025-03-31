# Travel Assistance AI Agent

## Overview
Travel Assistance is an AI-powered agent designed to help users plan their trips efficiently. It extracts key travel details from user input, refines them through interactive questioning, fetches top destinations and activities using Google Maps API, and generates a well-structured itinerary using Groq's `llama-3.3-70b-specdec` model.

## Features
- Extracts travel details from incomplete user input.
- Suggests destinations if missing, based on user preferences.
- Refines collected details by asking additional questions.
- Fetches top places to visit using Google Maps API.
- Generates a structured travel itinerary using LLM.

## Tech Stack
- **Programming Language**: Python
- **LLM Provider**: Groq API (`llama-3.3-70b-specdec`)
- **APIs Used**:
  - Google Maps API (for finding top places)
  - Groq API (for itinerary generation)
- **Frameworks & Libraries**:
  - `openai` (for Groq API interaction)
  - `requests` (for API calls)
  - `json` (for data processing)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/vipu121/Travel-Assistance.git
   cd Travel-Assistance
   ```
2. Install dependencies:
3. Set up API keys:
   - Obtain Google Maps API Key and Groq API Key.
   - Set them as environment variables:
     ```bash
     export GOOGLE_MAPS_API_KEY="your_google_maps_api_key"
     export GROQ_API_KEY="your_groq_api_key"
     ```

## Usage
Run the AI agent by executing:
```bash
python generate_itinerary.py
```
Follow the interactive prompts to plan your trip efficiently.

## Workflow
1. **Extract Travel Details**:
   - Parses user input to identify key travel details (budget, destination, trip duration, etc.).
2. **Handle Missing Destination**:
   - If missing, asks the user about preferences (country, weather, region) and suggests three best-fit destinations.
3. **Refine Travel Details**:
   - Asks additional questions to clarify budget, trip purpose, starting location, and preferences.
4. **Fetch Best Places to Visit**:
   - Uses Google Maps API to find top attractions in the selected destination.
5. **Generate Itinerary**:
   - Uses `llama-3.3-70b-specdec` via Groq API to generate a structured multi-day itinerary.

## Example Output
```json
{
  "itinerary": {
    "day_1": [
      {"time": "9:00 AM - 10:00 AM", "activity": "Visit Eiffel Tower", "description": "Enjoy the panoramic view of Paris."},
      {"time": "12:00 PM - 1:30 PM", "activity": "Lunch at a local café", "description": "Try authentic French cuisine."}
    ],
    "day_2": [
      {"time": "10:00 AM - 12:00 PM", "activity": "Louvre Museum", "description": "Explore world-famous artworks including the Mona Lisa."}
    ]
  }
}
```

## Contributing
Feel free to open issues and submit pull requests to improve the project.


## Author
Developed by [vipu121](https://github.com/vipu121).

