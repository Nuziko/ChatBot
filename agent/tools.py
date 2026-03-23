from typing import List, Dict
import json
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
import os
import requests
load_dotenv()  

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")


search_tool = TavilySearch(
    max_results=3,
    topic='general',
    search_depth="basic",
    include_answer=True,

)

@tool
def search_patient_by (searchTerm: str,config:RunnableConfig) -> str:
    """Return a list of patients matching the search term .
    The search term can be a patient first name , last name , full name, date of birth, telephone number, national identification number (NIN), or email address."""
    searchTerm=searchTerm.strip().replace(" ","+")# to handle names with spaces and ensure the search term is URL-friendly for example "John Doe" becomes "John+Doe"
    print(f"Searching for patients with term: {searchTerm}")
    thread_id = config.get("configurable", {}).get("thread_id")
    headers={
     "x-service-api-key": os.getenv("CHATBOT_API_KEY"),
     "x-user-id":str(thread_id)
     }
    try:
        response = requests.get(f"{os.getenv('BACKEND_URL')}/patient/search?searchTerm={searchTerm}&&limit=3&&includeAll=\"true\"",headers=headers)
        results = response.json()
        return json.dumps(results)
    except Exception as e:
        print(f"Error searching for patients: {e}")
        return json.dumps({"error": "An error occurred while searching for patients."})
   



@tool
def get_patient_by_id(patient_id: str,config:RunnableConfig) -> str:
    """
    Return a patient by id if exists, else return error message. Return all patient info as JSON string.
    """
    thread_id = config.get("configurable", {}).get("thread_id")
    headers={
     "x-service-api-key": os.getenv("CHATBOT_API_KEY"),
     "x-user-id":str(thread_id)
     }
    try:
        response = requests.get(f"{os.getenv('BACKEND_URL')}/patient/{patient_id}",headers=headers)
        results = response.json()
        return json.dumps(results)
    except Exception as e:
        print(f"Error fetching patient by ID: {e}")
        return json.dumps({"error": "An error occurred while fetching patient information."})


@tool 
def search_web(query: str) -> List[Dict]:
    """
    Search the web for current medical information, drug interactions, 
    clinical guidelines, symptoms, or any health-related topic that requires 
    up-to-date information. Use this for questions about recent treatments, 
    medications, or when the patient asks about specific medical conditions.
    """
    results = search_tool.run(query)
    return results

@tool
def get_current_date_time() -> str:
    """
    Return the current date and time as a string.
    """
    return datetime.now(ZoneInfo("Africa/Algiers")).ctime()


TOOLS = [search_web, get_patient_by_id, search_patient_by ,get_current_date_time]

NODE_TOOLS=[get_current_date_time]