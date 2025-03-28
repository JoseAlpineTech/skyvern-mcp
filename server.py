import asyncio
import json
from typing import Any
from mcp.server.fastmcp import FastMCP

from skyvern.agent import SkyvernAgent
from skyvern.forge import app
from skyvern.forge.sdk.schemas.tasks import TaskRequest, TaskResponse
from skyvern.forge.sdk.schemas.task_generations import TaskGenerationBase
from skyvern.forge.prompts import prompt_engine

mcp = FastMCP("Skyvern")
skyvern_agent = SkyvernAgent()

async def _skyvern_run_task_v1(user_prompt: str, url: str) -> dict[str, Any] | None:        
    llm_prompt = prompt_engine.load_prompt("generate-task", user_prompt=user_prompt)
    llm_response = await app.LLM_API_HANDLER(prompt=llm_prompt, prompt_name="generate-task")
    task_generation = TaskGenerationBase.model_validate(llm_response)
    task_request = TaskRequest.model_validate(task_generation, from_attributes=True)
    if url is not None:
        task_request.url = url
    return await skyvern_agent.run_task(task_request=task_request, timeout_seconds=3600)

@mcp.tool()
async def skyvern_v1(user_goal: str, url: str) -> str:
    """Browse the internet using a browser to achieve a user goal.

    Args:
        user_goal: brief description of what the user wants to accomplish
        url: the target website for the user goal
    """
    res = await _skyvern_run_task_v1(user_goal, url)
    return res.model_dump()["extracted_information"]


@mcp.tool()
async def add_two_numbers(a: int, b: int) -> int:
    """Add two numbers provided by the user

    Args:
        a: input number
        b: input number
    """
    return a+b

async def main():
    res = await _skyvern_run_task_v1("Go on wikipedia and find out Jaco Pastorius' date of birth", "https://www.wikipedia.com/")
    print("Final answer:", res.model_dump()["extracted_information"])

if __name__ == "__main__":
    mcp.run(transport='stdio')
    # asyncio.run(main())