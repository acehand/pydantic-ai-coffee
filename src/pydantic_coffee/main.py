import uvicorn
import logfire
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from pydantic_coffee.models.coffee import CoffeeOrder, CoffeeType, MilkType, Orders
from pydantic_coffee.services.order_service import OrderService
from pydantic_coffee.agents.order_pattern_agent import OrderPatternAgent
from pydantic_coffee.agents.intent_agent import IntentAgent, PossibleIntents
from pydantic_ai.models.vertexai import VertexAIModel

# Initialize logger and service
logfire.configure()
order_service = OrderService()

app = FastAPI(
    title="Pydantic Coffee",
    description="Coffee Order Management API",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint"""
    logfire.info("Health check endpoint called")
    return {
        "status": "healthy",
        "service": "pydantic_coffee",
        "version": "0.1.0"
    }

@app.post("/orders/", response_model=CoffeeOrder)
async def create_order(order: CoffeeOrder):
    """Create a new coffee order"""
    logfire.info(f"Creating new order: {order.dict()}")
    order_service.add_order(order)
    return order

@app.get("/orders/", response_model=Orders)
async def get_orders():
    """Get all coffee orders"""
    logfire.info("Fetching all orders")
    df = order_service.get_orders()
    
    # Convert DataFrame to Orders model and return
    orders = Orders.from_dataframe(df)
    model = VertexAIModel('gemini-1.5-flash-002')
    intent = IntentAgent(model)
    intent_response = await intent.getIntent("how many lattes on Monday?")
    logfire.info(f"Intent;{intent}", intent=intent_response.data.intent)
    
    match intent_response.data.intent:
        case PossibleIntents.COUNT:
            print("Count")
            agent = OrderPatternAgent(model)
            response = await agent.analyze(orders)
    #     case "ORDER_PATTERN":
    #         agent = OrderPatternAgent(model)
    #         response = await agent.analyze_pattern(orders)
    #     case "ORDER_SUMMARY":
    #         agent = OrderPatternAgent(model)
    #         response = await agent.analyze_summary(orders)
    #     case _:
    #         response = await agent.analyze(orders)
    
    # agent = OrderPatternAgent(model)
    # response = await agent.analyze(orders)
    # print(response.data.model_dump_json())
    return orders

@app.get("/orders/{order_id}", response_model=Dict[str, Any])
async def get_order(order_id: str):
    """Get a specific order by ID"""
    order = order_service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=4002, reload=True)