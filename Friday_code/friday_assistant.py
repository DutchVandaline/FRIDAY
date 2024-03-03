import openai
import requests
from bs4 import BeautifulSoup


client = openai.Client(api_key="YOUR_API_KEY")


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
                {"role": "system", "content": "Your name is Friday and you are a Google Search Expert. Say sir like you are a servant. Your task is to convert unstructured user inputs to optimized Google search queries. Example: USER INPUT: 'Why was Sam Altman fired from OpenAI?' OPTIMIZED Google Search Query: 'Sam Altman Fired OpenAI'"},
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
    params={
        "q": query,
        "tbm": "nws",
        "location": location,
        "num": str(num_results),
        "api_key": "YOUR_API_KEY",
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
    
