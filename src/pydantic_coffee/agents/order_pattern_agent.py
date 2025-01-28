import json
from typing import List
from pydantic import BaseModel, Field, model_validator, field_validator
from typing_extensions import Annotated
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.vertexai import VertexAIModel
from pydantic_coffee.models.coffee import CoffeeOrder, Orders
from enum import Enum
from typing import Dict, List

class TimePeriod(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"

class Likelihood(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class DrinkPreference(BaseModel):
    drink_type: str
    milk_type: str
    likelihood: Likelihood
    time_period: TimePeriod

class DayPattern(BaseModel):
    preferences: List[DrinkPreference]

class Pattern(BaseModel):
    monday: DayPattern
    tuesday: DayPattern
    wednesday: DayPattern
    thursday: DayPattern
    friday: DayPattern
    saturday: DayPattern
    sunday: DayPattern

    def create_example(cls):
        return cls(
            monday=DayPattern(
                preferences=[
                    DrinkPreference(
                        drink_type="latte",
                        milk_type="oat",
                        likelihood=Likelihood.HIGH,
                        time_period=TimePeriod.MORNING
                    ),
                    DrinkPreference(
                        drink_type="cortado",
                        milk_type="regular",
                        likelihood=Likelihood.MEDIUM,
                        time_period=TimePeriod.AFTERNOON
                    )
                ]
            ),
            # ... similar for other days
        )

class PatternResponse(BaseModel):
    pattern: Pattern
    confidence: float
    reasoning: str
    

class Response(BaseModel):
    prediction: str
    confidence: float
    reasoning: str

class OrderPatternAgent:
    def __init__(self, model: VertexAIModel):
        self.model = model
        self.agent=Agent(
            model=model,
            deps_type=Orders,
            result_type=PatternResponse,
            retries=2,
            system_prompt=(
            "You are an AI analyzing coffee ordering patterns. Analyze past coffe orders to generate an order pattern."
            "Ignore external factors like weather, holidays, etc."
            "Work only with the historical data provided."
            )
        )
        
        @self.agent.system_prompt
        async def add_past_orders(ctx: RunContext):
            def to_json(orders: List[CoffeeOrder]):
                orders_list = []
                for order in orders.orders:
                    orders_list.append({
                        "order_id": order.order_id,
                        "coffee_type": order.coffee_type,
                        "milk_type": order.milk_type,
                        "cost": order.cost,
                        "order_date": order.time.strftime("%Y-%m-%d %a %I:%M %p"),
                        "server_name": order.server_name
                    })
                return json.dumps(orders_list, indent=2)
            return f" Past Orders: \n{to_json(ctx.deps)}"
            

    async def analyze(self, orders: Orders):
        pattern = await self.agent.run(
            user_prompt=(
                "Based on the historical shift data, analyze all the coffee orders. ?" 
                "Look at their order history and determine preferences r"
                "(morning/evening/overnight) for each day of the week. Rate each as high, medium, "
                "or low preference. Only return high preference patterns."
                
            ),
            deps=orders
        )
        print(f"Order pattern: {pattern}")
        return pattern
			