import openai
import requests
from bs4 import BeautifulSoup
from friday_voice import FridayVoice
import subprocess
import webbrowser
import geocoder
import psutil



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
        "api_key": "YOUR_API_KEY",
        "cx": "YOUR_CX"
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

def fetch_weather_data(api_key):
    location = get_location()
    if location:
        latitude, longitude = location
        print("Your current latitude:", latitude)
        print("Your current longitude:", longitude)
    else:
        print("Failed to fetch your current location.")

    url = f"http://api.openweathermap.org/data/2.5/weather?lat=37.523663842914&lon=126.87147199816&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        weather_data = response.json()
        return weather_data
    else:
        return None
    
def get_location():
    g = geocoder.ip('me')
    return g.latlng

#basically, it's chrome. 
#TODO: Add more programs. 
def program_start(program_name):
    FridayVoice.speak_response(f"Initiating {program_name}", client)
    program_name_lower = str(program_name).lower()
    print(program_name_lower)
    if 'chrome' in program_name_lower:
        subprocess.call(['YOUR_PATH_TO_CHROME'])
    else:
        FridayVoice.speak_response("Sorry, sir. There are no such Program found.", client)

def computer_status():
    battery = psutil.sensors_battery()
    plugged = battery.power_plugged
    percent = str(battery.percent)
    plugged = "Plugged In" if plugged else "Not Plugged In"
    
    print(percent+'% | '+plugged)
    print(f"CPU utilization: {psutil.cpu_percent()}%")
    print(f"Memory utilization: {psutil.virtual_memory().percent}%") 
    FridayVoice.speak_response(f"Battery {percent}%. {plugged}, sir. CPU utilization {psutil.cpu_percent()}% and Memory utilization: {psutil.virtual_memory().percent}%, sir", client)
    

def show_chrome_with_url(inputurl):
    url = inputurl

    chrome_path = 'YOUR_PATH_TO_CHROME'
    webbrowser.get(chrome_path).open(url)

