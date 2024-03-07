import openai
import requests
from bs4 import BeautifulSoup
from friday_voice import FridayVoice
from colorama import Fore
from friday_whisper import FridayListen


client = openai.Client(api_key="Your_API_KEY")


def GoogleSearch(params):
    url = f"https://www.googleapis.com/customsearch/v1?q={params['q']}&tbm=nws&location={params['location']}&num={params['num']}&key={params['api_key']}&cx={params['cx']}"
    response = requests.get(url)
    data = response.json()
    return data

def generate_google_search_query(user_input):
    prompt = f"Convert the following user query into a optimized Google search query: '{user_input}"

    try:
        completion = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "Your task is to convert unstructured user inputs to optimized Google search queries. Example: USER INPUT: 'Why was Sam Altman fired from OpenAI?' OPTIMIZED Google Search Query: 'Sam Altman Fired OpenAI'"},
                {"role": "user", "content": prompt}
            ]
        )
        if completion.choices:
            response_message = completion.choices[0].message
            if hasattr(response_message, 'content'):
                return response_message.content.strip()
            else:
                return "No content in response"
        else:
            return "No response from GPT"
    except Exception as e:
        print(f"Error in generating Google search query: {e}")
        return None

def get_organic_results(query, num_results=3, location= "United States"):
    FridayVoice.speak_response("Searching in progress", client)
    params={
        "q": query,
        "tbm": "nws",
        "location": location,
        "num": str(num_results),
        "api_key": "Your_Api_key",
        "cx": "363427b9dc4b144e8"
    }

    search = GoogleSearch(params)
    news_results = search.get("items", [])
    urls = [result['link'] for result in news_results]
    return urls

def scrape_website(url):
    headers = {'User-Agent' : 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        page_content = response.content
        soup = BeautifulSoup(page_content, 'html.parser')
        paragraphs = soup.find_all('p')
        scraped_data = [p.get_text() for p in paragraphs]
        formatted_data = "\n".join(scraped_data)
        return url, formatted_data
    else:
        return url, "Failed to retrieve the webpage"
    
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
                    {"role": "system", "content": "Determine whether user is asking for command or is just a daily talk or answering the previous question that you asked. Example1. User: 'Hello' System: 'daily' Example2. User: 'Check the Weather' System: 'command' Example3. System: 'Did you mean 'Oscars''? User: 'Yes' System: 'answering' "},
                    {"role": "user", "content": prompt}
                ]
            )
    response_message = completion.choices[0].message
    response_content = response_message.content
    print(response_content)
    if 'daily' in response_content:
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
        
    elif 'command' in response_content:
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

                
            
            
