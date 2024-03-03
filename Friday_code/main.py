import openai
from colorama import Fore

from friday_voice import FridayVoice
from friday_whisper import FridayListen
from friday_assistant import generate_google_search_query, scrape_website, get_organic_results


client = openai.Client(api_key="Your_API_KEY")

assistant = client.beta.assistants.create(
    name="Friday",
    instructions="Your name is Friday and you are a Google Search Expert. Say sir like you are a servant. You are an assistant capable of fetching and displaying news articles based on user queries.",
    model = "gpt-4-1106-preview",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_organic_results",
                "description": "Fetch news URLs based on a search query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "num_results": {"type": "integer", "description": "Number of results to return"},
                        "location": {"type": "string", "description": "Location for search context"}
                    },
                    "required": ["query"]
                }
            }
        },
         {
            "type": "function",
            "function": {
                "name": "scrape_website",
                "description": "Scrape the textual content from a given URL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to scrape"},
                    },
                    "required": ["url"]
                }
            }
        },
    ]
)

while True:
    user_input = input(Fore.CYAN + "Press Enter to start talking, or type 'exit' to quit: ")
    if user_input.lower() == 'exit':
        break
    else: 
        user_query = str(FridayListen.transcribe_regular_speech())

    if 'search' in user_query.lower():
        google_serach_query = generate_google_search_query(user_query)
        print(f"Converted Google Search Query: {google_serach_query}")

        if google_serach_query:
            news_urls = get_organic_results(google_serach_query)

            if news_urls:
                url, news_content = scrape_website(news_urls[0])

                grounding_context = f"Context: {news_content}\nUserQUery: {user_query}"
                print(grounding_context)

                completion = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=[
                    {"role": "system", "content": "Your name is Friday Say sir like you are a servant. You are a helpful assistant, always return only the essential parts that answers the USER original USER query. Be terse with one backup reason."},
                    {"role": "user", "content": grounding_context}
                    ]
                )

                response = completion.choices[0].message.content if completion.choices[0].message else ""
                FridayVoice.speak_response(response, client)


                
            else:
                print("no news articles found for your query")
        else:
            print("Failed to generate a Google search query")
            
    else:
        prompt = f"Your name is Friday. Say sir like you are a servant. You are a assistant who is similar to JARVIS and FRIDAY from movie \"Ironman\" Be terse :'{user_query}"

        completion = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=[
                    {"role": "system", "content": "Your name is Friday. Say sir like you are a servant. You are a assistant who is similar to JARVIS and FRIDAY from movie \"Ironman\" Be terse."},
                    {"role": "user", "content": prompt}
                    ]
                )

        response = completion.choices[0].message.content if completion.choices[0].message else ""

        FridayVoice.speak_response(response, client)

