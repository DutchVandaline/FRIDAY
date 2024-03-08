import openai
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
                    {"role": "system", "content": "Determine whether user is asking. First, there are two big categories. Daily talk and Command. Second, in command there are few categories. Google search command, Run program command, weather command, computer status command, Other command. Also, if user says to quit or sleep, return 'finishing session'  Example1. User: 'Hello' System: 'daily' Example2. User: 'Search about Oscars' System: 'google search command' Example3.User: 'Execute(Run) Chrome' System: 'run program command, Chrome' Example4. User: 'Call me as Stark' System: 'other command' Example5. User: 'How's the weather today?' System: 'weather command' Example5. User: 'How's the battery?' System: 'computer status' Example6. User: 'Go to sleep friday' System: ''finishing session'"},
                    {"role": "user", "content": prompt}
                ]
            )
    response_message = completion.choices[0].message
    response_content = response_message.content
    print(response_content)
    if 'daily' in response_content or 'other command' in response_content:
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=str(user_query)
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            )
        while run.status != "completed":
            keep_retrieving_run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            print(f"Run status: {keep_retrieving_run.status}")

            if keep_retrieving_run.status == "completed":
                print("\n")
                break
            
        all_messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )

        print("###################################################### \n")
        print(f"USER: {message.content[0].text.value}")
        print(f"ASSISTANT: {all_messages.data[0].content[0].text.value}")
        daily_response = all_messages.data[0].content[0].text.value
        FridayVoice.speak_response(daily_response, client)
        for message in all_messages:
            print(message.content)
        
    elif 'google search command' in response_content:
        google_search_query = generate_google_search_query(user_query)
        if google_search_query:
            news_urls = get_organic_results(google_search_query)
            if  news_urls:
                url, news_content = scrape_website(news_urls[0])
                grounding_context = f"Context: {news_content}\nUser Query: {user_query}"
                print(grounding_context)
                
                completion = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "Your name is Friday. Say sir like you are a servant. You are a helpful assistant, always return only the essential parts that answers the USER original USER query. Be terse"},
                    {"role": "user", "content": grounding_context}
                    ]
                ) 
                
                response = completion.choices[0].message.content if completion.choices[0].message else ""
                print(Fore.YELLOW + response)
                FridayVoice.speak_response(response, client)
            
            else:
                print("No news articles found for your query")
                
        else:
            print("Failed to generate a Google search Query")

    elif 'run program command' in response_content:
        index = response_content.index("run program command") + len("run program command")
        program_name = response_content[index:].split(', ')[1].strip()
        print(program_name)
        program_start(program_name)
    
    elif 'weather command' in response_content:
        weather_data = fetch_weather_data("Your_API_KEY")
        if weather_data:
            weather_info = f"Weather in Seoul: {weather_data['weather'][0]['description']}, Temperature: {weather_data['main']['temp']}°C, Feels like: {weather_data['main']['feels_like']}, temp_min: {weather_data['main']['temp_min']}, temp_max: {weather_data['main']['temp_max']}, humidity: {weather_data['main']['humidity']}"

            grounding_context = f"Context: {weather_info}\nWeather Data: {user_query}"
            print("Weather data fetched successfully:")
            print(grounding_context)

            completion = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "Your name is Friday. Say sir like you are a servant. I am giving you a weather data add those data and make a remarkable result to User. Also, recommend some clothes for user. be terse"},
                    {"role": "user", "content": grounding_context}
                    ]
                )
            response = completion.choices[0].message.content if completion.choices[0].message else ""
            print(Fore.YELLOW + response)
            FridayVoice.speak_response(response, client)
            
        else:
            print("Failed to fetch weather data.")
    
    elif 'computer status' in response_content:
        computer_status()

    elif 'finishing session' in response_content:
        print("Finishing session")
        FridayVoice.speak_response("Finishing Session. Call me when needed, sir.", client)
        break
    
