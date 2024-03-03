import openai
from friday_voice import FridayVoice
from friday_whisper import FridayListen
from friday_google import generate_google_search_query, scrape_website, get_organic_results

class FridayAssistant:
    def __init__(self):
        self.client = openai.Client(api_key="YOUR_API_KEY")
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

    def run_assistant(self):
        user_query = str(FridayListen.transcribe_regular_speech())

        if 'search' in user_query.lower():
            google_search_query = generate_google_search_query(user_query)

            if google_search_query:
                news_urls = get_organic_results(google_search_query)

                if news_urls:
                    url, news_content = scrape_website(news_urls[0])

                    grounding_context = f"Context: {news_content}\nUser Query: {user_query}"
                    print(grounding_context)

                    completion = self.client.chat.completions.create(
                        model="gpt-4-1106-preview",
                        messages=[
                            {"role": "system",
                             "content": "Your name is Friday. Say sir like you are a servant. You are a helpful assistant, always return only the essential parts that answers the USER original USER query. Be terse with one backup reason."},
                            {"role": "user", "content": grounding_context}
                        ]
                    )

                    response = completion.choices[0].message.content if completion.choices[0].message else ""
                    FridayVoice.speak_response(response, self.client)

                else:
                    print("No news articles found for your query")
            else:
                print("Failed to generate a Google search query")

        else:
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