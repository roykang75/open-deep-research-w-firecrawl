from planner import generate_research_plan
from task_splitter import split_into_subtasks
from prompts import SUBAGENT_PROMPT_TEMPLATE, COORDINATOR_PROMPT_TEMPLATE
from smolagents import LiteLLMModel, ToolCallingAgent, MCPClient, tool
from serpapi import GoogleSearch
import os
import json

# SerpAPI configuration
SERP_API_KEY = os.environ.get("SERP_API_KEY")

# Scraping MCP configuration
SCRAPING_MCP_URL = "http://localhost:8000/mcp/"

# Models configured via environment variables
COORDINATOR_LLM_URL = os.environ.get("COORDINATOR_LLM_URL", "https://api.openai.com/v1")
COORDINATOR_MODEL = os.environ.get("COORDINATOR_MODEL", "gpt-4o")
SUBAGENT_LLM_URL = os.environ.get("SUBAGENT_LLM_URL", "https://api.openai.com/v1")
SUBAGENT_MODEL = os.environ.get("SUBAGENT_MODEL", "gpt-4o")


def search_google(query: str, num_results: int = 10) -> list:
    """
    Search Google using SerpAPI and return a list of search results.
    
    Args:
        query: The search query string
        num_results: Number of results to return (default: 10)
    
    Returns:
        List of search results with title, link, and snippet
    """
    params = {
        "engine": "google",
        "q": query,
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
        "num": num_results,
        "api_key": SERP_API_KEY
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    organic_results = results.get("organic_results", [])
    
    return [
        {
            "title": r.get("title", ""),
            "link": r.get("link", ""),
            "snippet": r.get("snippet", "")
        }
        for r in organic_results
    ]


def run_deep_research(user_query: str) -> str:
    print("Running the deep research...")

    # 1) Generate research plan
    research_plan = generate_research_plan(user_query)

    # 2) Split into explicit subtasks
    subtasks = split_into_subtasks(research_plan)

    # 3) Coordinator + sub-agents with SerpAPI search and Scraping MCP
    print("Initializing Coordinator")
    print("Coordinator Model: ", COORDINATOR_MODEL)
    print("Coordinator LLM URL: ", COORDINATOR_LLM_URL)
    print("Subagent Model: ", SUBAGENT_MODEL)
    print("Subagent LLM URL: ", SUBAGENT_LLM_URL)

    coordinator_model = LiteLLMModel(
        model_id=f"openai/{COORDINATOR_MODEL}",
        api_key=os.environ.get("OPENAI_API_KEY"),
        api_base=COORDINATOR_LLM_URL,
    )
    subagent_model = LiteLLMModel(
        model_id=f"openai/{SUBAGENT_MODEL}",
        api_key=os.environ.get("OPENAI_API_KEY"),
        api_base=SUBAGENT_LLM_URL,
    )

    # Connect to Scraping MCP server
    with MCPClient({"url": SCRAPING_MCP_URL, "transport": "streamable-http"}) as scraping_tools:
        
        # ---- Search Tool using SerpAPI --------------------------------------
        @tool
        def search_web(query: str) -> str:
            """
            Search the web using Google via SerpAPI.
            
            Args:
                query (str): The search query to find relevant information.
            
            Returns:
                str: JSON string containing search results with titles, links, and snippets.
            """
            print(f"Searching the web for: {query}")
            results = search_google(query)
            return json.dumps(results, indent=2, ensure_ascii=False)

        # Combine search tool with scraping MCP tools
        all_tools = [search_web] + list(scraping_tools)

        # ---- Initialize Subagent TOOL --------------------------------------
        @tool
        def initialize_subagent(subtask_id: str, subtask_title: str, subtask_description: str) -> str:
            """
           Spawn a dedicated research sub-agent for a single subtask.

            Args:
                subtask_id (str): The unique identifier for the subtask.
                subtask_title (str): The descriptive title of the subtask.
                subtask_description (str): Detailed instructions for the sub-agent to perform the subtask.

            The sub-agent:
            - Has access to search_web tool (SerpAPI) for web search.
            - Has access to scraping MCP tools for crawling web pages.
            - Must perform deep research ONLY on this subtask.
            - Returns a structured markdown report with:
              - a clear heading identifying the subtask,
              - a narrative explanation,
              - bullet-point key findings,
              - explicit citations / links to sources.
            """
            print(f"Initializing Subagent for task {subtask_id}...")

            subagent = ToolCallingAgent(
                tools=all_tools,  # SerpAPI search + Scraping MCP tools
                model=subagent_model,
                add_base_tools=False,
                name=f"subagent_{subtask_id}",
            )

            subagent_prompt = SUBAGENT_PROMPT_TEMPLATE.format(
                user_query=user_query,
                research_plan=research_plan,
                subtask_id=subtask_id,
                subtask_title=subtask_title,
                subtask_description=subtask_description,
            )
            
            return subagent.run(subagent_prompt)

        # ---- Coordinator agent ---------------------------------------------
        coordinator = ToolCallingAgent(
            tools=[initialize_subagent],
            model=coordinator_model,
            add_base_tools=False,
            name="coordinator_agent",
        )

        # Coordinator prompt: it gets the list of subtasks and the tool
        subtasks_json = json.dumps(subtasks, indent=2, ensure_ascii=False)

        coordinator_prompt = COORDINATOR_PROMPT_TEMPLATE.format(
            user_query=user_query,
            research_plan=research_plan,
            subtasks_json=subtasks_json,
        )

        final_report = coordinator.run(coordinator_prompt)
        return final_report
