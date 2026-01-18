import os
from openai import OpenAI
from prompts import PLANNER_SYSTEM_INSTRUCTIONS

def generate_research_plan(user_query: str) -> str:
    PLANNER_LLM_URL = os.environ.get("PLANNER_LLM_URL", "https://api.openai.com/v1")
    PLANNER_MODEL = os.environ.get("PLANNER_MODEL", "gpt-4o")

    print("Generating the research plan for the query: ", user_query)
    print("MODEL: ", PLANNER_MODEL)
    print("LLM_URL: ", PLANNER_LLM_URL)

    planner_client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=PLANNER_LLM_URL,
    )
    completion = planner_client.chat.completions.create(
        model=PLANNER_MODEL,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": user_query},
        ],
        stream=True,
    )

    print("\033[93mGenerated Research Plan:\033[0m")
    research_plan = ""

    def _content(obj):
        try:
            return obj.choices[0].delta.content
        except Exception:
            try:
                return obj.choices[0].message.content
            except Exception:
                return None

    try:
        for chunk in completion:
            c = _content(chunk)
            if c:
                research_plan += c
                print(c, end="")
    except TypeError:
        c = _content(completion)
        if c:
            research_plan = c
            print(c, end="")

    return research_plan
