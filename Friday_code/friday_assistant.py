iimport openai
from friday_voice import FridayVoice
from colorama import Fore
from friday_whisper import FridayListen
from friday_tools import get_organic_results, generate_google_search_query, scrape_website, program_start, fetch_weather_data, computer_status


client = openai.Client(api_key="Your_API_KEY")

assistant = client.beta.assistants.create(
    name="Friday",
    instructions= "Your name is Friday and you are a Google Search Expert. Say sir like you are a servant. You are an assistant capable of fetching and displaying news articles based on user queries.",
    model="gpt-4-1106-preview",
    tools=[
        {
            "type" : "function",
            "function" : {
                "name": "get_organic_results",
                "description": "Fetch news URLs based on a search query",
                "parameters": {
                    "type": "object",
                    "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return"
                    },
                    "location": {
                        "type": "string",
                        "description": "Location for search context"
                    }
                    },
                    "required": [
                    "query"
                    ]
                }
            }},
    
     {
            "type" : "function",
            "function" : {
                "name": "scrape_website",
                "description": "Scrape the textual content from a given URL",
                "parameters": {
                    "type": "object",
                    "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to scrape"
                    }
                    },
                    "required": [
                    "url"
                    ]
                }
            }},
            {
            "type" : "function",
            "function" : {
                "name": "fetch_weather_data",
                "description": "Fetch Weather Data of current position",
                "parameters": {
                    "type": "object",
                    "properties": {
                    "api_key": {
                        "type": "string",
                        "description": "Open Weather Map Api_key"
                    }
                    },
                    "required": [
                    "api_key"
                    ]
                }
            }}
        ]
)
thread = client.beta.threads.create()



while True:
    user_query = str(FridayListen.transcribe_regular_speech())
    prompt = f"Determine if user asked for a command or just a daily talk: '{user_query}'"
    completion = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "Your content goes here"},
                    {"role": "user", "content": prompt}
                ]
            )
    response_message = completion.choices[0].message
    response_content = response_message.content
    print(response_content)
    ADD_YOUR_CUSTOM_FUNTIONS