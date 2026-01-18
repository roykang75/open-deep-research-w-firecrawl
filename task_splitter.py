import os
import json
from typing import List
from pydantic import BaseModel, Field

from huggingface_hub import InferenceClient
from prompts import TASK_SPLITTER_SYSTEM_INSTRUCTIONS

class Subtask(BaseModel):
    id: str = Field(
        ...,
        description="Short identifier for the subtask (e.g. 'A', 'history', 'drivers').",
    )
    title: str = Field(
        ...,
        description="Short descriptive title of the subtask.",
    )
    description: str = Field(
        ...,
        description="Clear, detailed instructions for the sub-agent that will research this subtask.",
    )

class SubtaskList(BaseModel):
    subtasks: List[Subtask] = Field(
        ...,
        description="List of subtasks that together cover the whole research plan.",
    )

TASK_SPLITTER_JSON_SCHEMA = {
    "name": "subtaskList",
    "schema": SubtaskList.model_json_schema(),
    "strict": True,
}

def split_into_subtasks(research_plan: str) -> List[dict]:

    MODEL_ID = "deepseek-ai/DeepSeek-V3.2-Exp"
    PROVIDER = "novita"
    
    print("Splitting the research plan into subtasks...")
    print("MODEL: ", MODEL_ID)
    print("PROVIDER: ", PROVIDER)
    
    client = InferenceClient(
        api_key=os.environ["HF_TOKEN"],
        #bill_to="huggingface",
        provider=PROVIDER,
    )
    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": TASK_SPLITTER_SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": research_plan},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": TASK_SPLITTER_JSON_SCHEMA,
            }
        )
        content = completion.choices[0].message.content
        if not content:
            raise ValueError("LLM returned empty content")
            
        # Parse and validate using Pydantic
        subtask_list = SubtaskList.model_validate_json(content)
        subtasks = [t.model_dump() for t in subtask_list.subtasks]

    except Exception as e:
        print(f"\033[91mError during subtask generation: {e}\033[0m")
        if 'content' in locals() and content:
            print(f"Raw content: {content}")
        # Fallback: try manual extraction if JSON schema fails but content exists
        try:
            if 'content' in locals() and content:
                data = json.loads(content)
                if 'subtasks' in data:
                    subtasks = data['subtasks']
                else:
                    raise ValueError("No 'subtasks' key in JSON")
            else:
                raise e
        except Exception as fallback_e:
            print(f"\033[91mFallback also failed: {fallback_e}\033[0m")
            raise e

    print("\033[93mGenerated The Following Subtasks\033[0m")
    for task in subtasks:
      print(f"\033[93m{task['title']}\033[0m")
      print(f"\033[93m{task['description']}\033[0m")
      print()
    return subtasks
