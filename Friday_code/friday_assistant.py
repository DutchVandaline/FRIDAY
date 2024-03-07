import openai
from friday_voice import FridayVoice
from friday_whisper import FridayListen
from friday_tools import generate_google_search_query, scrape_website, get_organic_results

class FridayAssistant:
    def __init__(self):
        self.client = openai.Client(api_key="Your_api_key")
        self.assistant = self.client.beta.assistants.create(
            name="Friday",
            instructions="Your name is Friday and you are a Google Search Expert. Say sir like you are a servant. You are an assistant capable of fetching and displaying news articles based on user queries.",
            model="gpt-4-1106-preview",
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

    def run_assistant_search(self, user_query):
        google_search_query = generate_google_search_query(user_query)
        print("Google Search Query:", google_search_query)

        if google_search_query:
            news_urls = get_organic_results(google_search_query)
            print("News URLs:", news_urls)

            if news_urls:
                for url in news_urls:
                    try:
                        url, news_content = scrape_website(url)
                        print("URL:", url)
                        print("News Content:", news_content)

                        grounding_context = f"Context: {news_content}\nUser Query: {user_query}"
                        print("Grounding Context:", grounding_context)

                        completion = self.client.chat.completions.create(
                            model="gpt-4-1106-preview",
                            messages=[
                                {"role": "system",
                                "content": "Your name is Friday. Say sir like you are a servant. You are a helpful assistant, always return only the essential parts that answers the USER original USER query. Be terse"},
                                {"role": "user", "content": grounding_context}
                            ]
                        )

                        response = completion.choices[0].message.content if completion.choices[0].message else ""
                        FridayVoice.speak_response(response, self.client)
                        break

                    except Exception as e:
                        print(f"Error scraping website {url}: {e}")

            else:
                print("No news articles found for your query")
        else:
            print("Failed to generate a Google search query")


    def run_assistant_daily(self, user_query):
        prompt = f"Your name is Friday. Say sir like you are a servant. You are an assistant who is similar to JARVIS and FRIDAY from movie \"Ironman\" Be terse: '{user_query}"

        completion = self.client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system",
                     "content": "Your name is Friday. Say sir like you are a servant. You are an assistant who is similar to JARVIS and FRIDAY from movie \"Ironman\" Be terse."},
                    {"role": "user", "content": prompt}
                ]
        )

        response = completion.choices[0].message.content if completion.choices[0].message else ""

        FridayVoice.speak_response(response, self.client)
        return 

    def determin_daily(self):
        user_input = str(FridayListen.listen_continuous())
        prompt = f"Determine if user asked for a command or just a daily talk: '{user_input}'"

        try:
            completion = self.client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "Determine whether user is asking for command or is just a daily talk or answering the previous question that you asked. Example1. User: 'Hello' System: 'daily' Example2. User: 'Check the Weather' System: 'command' Example3. System: 'Did you mean 'Oscars''? User: 'Yes' System: 'answering' "},
                    {"role": "user", "content": prompt}
                ]
            )
            if completion.choices:
                response_message = completion.choices[0].message
                if hasattr(response_message, 'content'):
                    response_content = response_message.content
                    print(response_content)
                    print(user_input)
                    if 'daily' in response_content:
                        self.run_assistant_daily(user_input)
                    elif 'command' in response_content:
                        self.run_assistant_search(user_input)                    
                else:
                    print("No content in response")
            else:
                print("No response from GPT")
        except Exception as e:
            print(f"Error in generating Google search query: {e}")


