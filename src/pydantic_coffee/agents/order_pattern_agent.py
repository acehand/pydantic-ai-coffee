import json
from typing import List
from pydantic import BaseModel, Field, model_validator, field_validator
from typing_extensions import Annotated
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.vertexai import VertexAIModel
from pydantic_coffee.models.coffee import CoffeeOrder, Orders


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
            result_type=Response,
            retries=2,
            system_prompt=(
            "You are an AI analyzing coffee ordering patterns. Analyze past coffe orders to answer questions about order patterns."
            "Use simple average based on past orders to predict future orders."
            "Ignore external factors like weather, holidays, etc."
            "Work only with the historical data provided."
            )
        )
        
        @self.agent.system_prompt
        async def add_past_orders(ctx: RunContext):
            def to_json(orders: List[CoffeeOrder]):
                orders_list = []
                for order in orders.orders:
                    print(order)
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
                "how many lattes are expected to be ordered on monday's ?" 
            ),
            deps=orders
        )
        print(f"Order pattern: {pattern}")
        return pattern
			