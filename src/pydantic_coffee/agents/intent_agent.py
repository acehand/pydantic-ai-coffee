from enum import Enum
from typing import List
from pydantic import BaseModel
from pydantic_ai.models.vertexai import VertexAIModel
from pydantic_ai import RunContext, Agent

class PossibleIntents(str, Enum):
    COUNT = "count"
    PATTERN = "pattern"
    TREND = "trend"
    SUMMARY = "summary"

class IntentData(BaseModel):
    intent: PossibleIntents

class IntentResponse(BaseModel):
    data: IntentData

class IntentAgent:
    def __init__(self, model: VertexAIModel):
        self.model = model
        self.agent = Agent(
            model=model,
            deps_type=PossibleIntents,
            result_type=IntentResponse,
            retries=2,
            system_prompt=(
                "You are an AI agent identifying the intent of the users question. "
                "Respond with the intent of the question from the possible intents provided. "
                "It can be a question about patterns, counts, trends, or summaries."
            )
        )
        
        @self.agent.system_prompt
        async def add_possible_intents(ctx: RunContext):
            intents_list = [intent.value for intent in PossibleIntents]
            return f"Possible Intents: {intents_list}"
            
        @self.agent.result_validator
        async def validate_result(ctx: RunContext, result: IntentResponse):
            if not isinstance(result.data.intent, PossibleIntents):
                raise ValueError(f"Invalid intent: {result.data.intent}")
            return result
        
    async def getIntent(self, user_prompt: str) -> IntentResponse:
        response =  await self.agent.run(user_prompt=user_prompt)
        return response.data
