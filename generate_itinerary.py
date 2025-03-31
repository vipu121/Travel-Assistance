from config import system_prompt, REQUIRED_FIELDS, FIELD_QUESTIONS
import groq
import json
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# Initialize Groq client

class Generate_Itinerary:
    def __init__(self,model,GROQ_API_KEY,GOOGLE_API_KEY):
        self.model=model
        self.API_KEY=GROQ_API_KEY
        self.GOOGLE_API_KEY=GOOGLE_API_KEY
        self.client = groq.Client(api_key=GROQ_API_KEY)

    def get_user_details(self,user_message):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )

        extracted_text = response.choices[0].message.content.strip()

        try:
            extracted_text = extracted_text.split("```json")[-1].split("```")[0].strip()
            extracted_data = json.loads(extracted_text)
        except json.JSONDecodeError:

            extracted_data = {"error": "Could not parse response. Received: " + extracted_text}
        # Ensure required fields are present
        # print(extracted_data)
        required_fields = ["destination", "trip_duration"]
        missing_fields = [field for field in required_fields if not extracted_data.get(field)]
        print("a",extracted_data)
        if missing_fields:
            extracted_data = self.ask_for_missing_details(extracted_data, missing_fields)
        # print(extracted_data)
        return extracted_data
    
    def ask_for_missing_details(self,details, missing_fields):
        """
        If any required information is missing, ask the user for clarification.
        """
        # print("Some details are missing:", missing_fields)
        
        if "destination" in missing_fields:
            country = input("Which country do you prefer to visit? ")
            weather = input("Do you prefer warm, cold, or moderate weather? ")
            region = input("Do you prefer a coastal, mountain, urban, or rural area? ")
            
            prompt = f"""
            The user has the following travel preferences:
            - Country: {country or "Any"}
            - Weather: {weather or "Any"}
            - Region: {region or "Any"}
            
            Suggest **exactly 3** best destinations that match these preferences.
            For each suggestion, include:
            - "destination": Name of the place
            - "trip_duration": Recommended number of days
            - "reason": A short reason why it fits the user’s preferences
            
            **Return only a JSON array** formatted as follows (without any explanation or text outside JSON):
            ```json
            [
                {{"destination": "Place1", "trip_duration": "X days", "reason": "Reason1"}},
                {{"destination": "Place2", "trip_duration": "Y days", "reason": "Reason2"}},
                {{"destination": "Place3", "trip_duration": "Z days", "reason": "Reason3"}}
            ]
            ```
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}]
            )

            response_text = response.choices[0].message.content.strip()


            try:
                suggested_destinations = json.loads(response_text)
                if isinstance(suggested_destinations, list) and len(suggested_destinations) == 3:
                    print("\nHere are 3 suggested destinations based on your preferences:")
                    
                    choices = []
                    for i, option in enumerate(suggested_destinations, start=1):
                        choice_text = f"{i}. {option['destination']} ({option['trip_duration']} days) - {option['reason']}"
                        print(choice_text)
                        choices.append(choice_text)

                    # Show options inside input prompt
                    user_input = input(f"\nWhich destination do you prefer? Choose 1, 2, or 3:\n{choices[0]}\n{choices[1]}\n{choices[2]}\nYour choice: ")
                    
                    try:
                        choice = int(user_input) - 1
                        if 0 <= choice < len(suggested_destinations):
                            details["destination"] = suggested_destinations[choice]["destination"]
                            details["trip_duration"] = suggested_destinations[choice]["trip_duration"]
                        else:
                            print("Invalid choice. Keeping destination empty.")
                    except ValueError:
                        print("Invalid input. Keeping destination empty.")
                else:
                    print("Unexpected response format. Keeping destination empty.")

            except json.JSONDecodeError:
                print("Failed to parse destination suggestions. Keeping destination empty.")

        # for field in missing_fields:
        #     if field not in ["destination", "trip_duration"]:
        #         details[field] = None
        if "trip_duration" in missing_fields and "destination" in details and details["destination"]:
            details["trip_duration"] = input(f"How many days do you plan to stay in {details['destination']}? ")
        print("b",details)
        return details
    
    def refine_user_details(self,user_details):
        """Manually ask missing questions (for use in Jupyter notebooks)."""
        
        for field in REQUIRED_FIELDS:
            if field not in user_details or user_details[field]=="":
                user_details[field] = input(FIELD_QUESTIONS[field] + " ")
        
        return user_details
    
    def get_top_attractions(self,destination):
        """Fetches top attractions for a given destination using Google Places API."""
  
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": f"Top attractions in {destination}",
            "key": self.GOOGLE_API_KEY
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            return [place["name"] for place in results]
        else:
            return {"error": "Failed to fetch attractions", "status_code": response.status_code}
        
    def refine_activities_with_llm(self,complete_details):
        """
        Uses LLM to filter attractions based on the user's complete travel details.
        """
        destination = complete_details.get("destination", "unknown")
        preferences = complete_details.get("preferences", [])
        budget = complete_details.get("budget", "moderate")
        dietary = complete_details.get("dietary_preferences", "none")
        accommodation = complete_details.get("accommodation_preferences", "any")
        
        search_results = self.get_top_attractions(destination)
        
        prompt = f"""
        You are a travel assistant. Below are the user's details:

        - Destination: {destination}
        - Budget: {budget}
        - Dietary preferences: {dietary}
        - Accommodation: {accommodation}
        - Travel preferences: {preferences}

        Here is a list of popular attractions in {destination}:
        {search_results}

        Please filter and suggest only the activities that best match the user's preferences.
        If the user prefers "hidden gems," prioritize lesser-known experiences.

        Return the response in structured JSON format.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}]
        )

        # Extract LLM response
        extracted_text = response.choices[0].message.content.strip()

        # Try to parse JSON response
        try:
            extracted_text = extracted_text.split("```json")[-1].split("```")[0].strip()
            filtered_activities = json.loads(extracted_text)
        except json.JSONDecodeError:

            filtered_activities = {"error": "Could not parse response", "raw_text": extracted_text}
        print("c",filtered_activities)
        return filtered_activities
    
    def generate_itinerary(self, complete_details, suggested_activities):
        """
        Generates a structured itinerary using the Groq API.
        """

        prompt = f"""
        You are a professional travel planner. Create a structured {complete_details['trip_duration']}-day itinerary for the user
        based on their preferences and the suggested activities.

        User details:
        - Destination: {complete_details['destination']}
        - Budget: {complete_details['budget']}
        - Dietary preferences: {complete_details['dietary_preferences']}
        - Accommodation: {complete_details['accommodation_preferences']}

        Suggested activities:
        {json.dumps(suggested_activities, indent=2)}

        Generate a detailed travel itinerary in the following JSON format:

        ```json
        {{
            "itinerary": {{
                "day_1": [
                    {{
                        "time": "",
                        "activity": "",
                        "description": ""
                    }},
                    {{
                        "time": "",
                        "activity": "",
                        "description": ""
                    }}
                ],
                "day_2": [
                    {{
                        "time": "",
                        "activity": "",
                        "description": ""
                    }},
                    {{
                        "time": "",
                        "activity": "",
                        "description": ""
                    }}
                ]
            }}
        }}
        ```

        - Include dining recommendations and breaks.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}]
        )

        extracted_text = response.choices[0].message.content.strip()

        # Try to parse JSON response
        try:
            extracted_text = extracted_text.split("```json")[-1].split("```")[0].strip()
            generated_itinerary = json.loads(extracted_text)
        except json.JSONDecodeError:
            generated_itinerary = {"error": "Could not parse response", "raw_text": extracted_text}

        return generated_itinerary

        
    def get_itinerary(self,user_message):
        get_user_details=self.get_user_details(user_message)
        complete_details=self.refine_user_details(get_user_details)
        suggested_activities=self.refine_activities_with_llm(complete_details)
        itinerary=self.generate_itinerary(complete_details,suggested_activities)

        return itinerary



                
            
if __name__ == "__main__":
    # Create an instance of the class

    travel_assistant = Generate_Itinerary(model="llama-3.3-70b-specdec", GROQ_API_KEY=GROQ_API_KEY,GOOGLE_API_KEY=GOOGLE_API_KEY)

    # Example user message (you can replace this with actual user input)
    user_message = input("Enter your travel request: ")

    # Get user details from the class method
    detailed_itinerary = travel_assistant.get_itinerary(user_message)

    # Print extracted details

    for day, activities in detailed_itinerary.get("itinerary", {}).items():
        print(f"\n{day.upper()} Itinerary:")
        for activity in activities:
            print(f"- {activity['time']}: {activity['activity']}")
            print(f"  {activity['description']}\n")

