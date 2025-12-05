import os
import json
from typing import List, Dict, Any
from typing import List
from pydantic import BaseModel, Field

from huggingface_hub import InferenceClient
from smolagents import LiteLLMModel, ToolCallingAgent, MCPClient, tool
from prompts import PLANNER_SYSTEM_INSTRUCTIONS

def generate_research_plan(user_query: str) -> str:
    MODEL_ID = "moonshotai/Kimi-K2-Thinking"
    PROVIDER = "auto"

    print("Generating the research plan for the query: ", user_query)
    print("MODEL: ", MODEL_ID)
    print("PROVIDER: ", PROVIDER)

    planner_client = InferenceClient(
        api_key=os.environ["HF_TOKEN"],
        bill_to="huggingface",
        provider=PROVIDER,
    )
    completion = planner_client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": user_query},
        ],
    )

    research_plan = completion.choices[0].message.content
    print("\033[93mGenerated Research Plan\033[0m")
    print(f"\033[93m{research_plan}\033[0m")
    return research_plan
