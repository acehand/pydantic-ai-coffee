from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from enum import Enum
from typing import List
import uuid
import pandas as pd


class CoffeeType(str, Enum):
    AMERICANO = "Americano"
    LATTE = "Latte"
    CORTADO = "Cortado"

class MilkType(str, Enum):
    OAT = "Oat"
    REGULAR = "Regular"
    ALMOND = "Almond"

class CoffeeOrder(BaseModel):
    order_id: int 
    coffee_type: CoffeeType
    milk_type: MilkType
    cost: float = Field(..., ge=0)
    time: datetime = Field(default_factory=datetime.utcnow)
    server_name: str
    
    @model_validator(mode='before')
    def calculate_cost(cls, values):
        if isinstance(values, dict):
            coffee_prices = {
                CoffeeType.AMERICANO: 3.50,
                CoffeeType.LATTE: 4.50,
                CoffeeType.CORTADO: 4.00
            }
            coffee_type = values.get('coffee_type')
            milk_type = values.get('milk_type')
            
            if coffee_type:
                base_price = coffee_prices[coffee_type]
                if milk_type in [MilkType.OAT, MilkType.ALMOND]:
                    base_price += 0.50
                values['cost'] = round(base_price, 2)
        return values

class Orders(BaseModel):
    orders: List[CoffeeOrder]
    
    @model_validator(mode='before')
    def validate_orders(cls, values):
        if isinstance(values, dict) and not values.get('orders'):
            raise ValueError("Orders cannot be empty")
        return values

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
            
        orders_list = []
        for _, row in df.iterrows():
            order = CoffeeOrder(
                order_id=int(row['order_id']),
                coffee_type=row['coffee_type'],
                milk_type=row['milk_type'],
                cost=float(row['cost']),
                time=pd.to_datetime(row['time']),
                server_name=str(row['server_name'])
            )
            orders_list.append(order)
        return cls(orders=orders_list)