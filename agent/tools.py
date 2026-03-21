from typing import List, Dict
import json
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import os
load_dotenv()  

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")


search_tool = TavilySearch(
    max_results=3,
    topic='general',
    search_depth="basic",
    include_answer=True,

)

@tool
def get_patients_by_(searchTerm: str) :
    """Return a list of patients matching the search term (name or birthdate)"""
    results = []
    # implement the logic to search for patients by name or birthdate and populate the results list

    return json.dumps(results)



@tool
def get_patient_by_id(patient_id: str) -> str:
    """
    Return a patient by id if exists, else return error message. Return all patient info as JSON string.
    """
    # implement the logic to search for a patient by id and return the patient info as a JSON string

    return json.dumps({"error": "PATIENT NOT FOUND"})


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


TOOLS = [search_web, get_patient_by_id, get_patients_by_,get_current_date_time]

NODE_TOOLS=[get_current_date_time]