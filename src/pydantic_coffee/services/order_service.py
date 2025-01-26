import pandas as pd
from pathlib import Path
from pydantic_coffee.models.coffee import CoffeeOrder
from typing import List
import os

class OrderService:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.csv_path = self.data_dir / "coffee_orders.csv"
        self._init_csv()

    def _init_csv(self):
        if not self.csv_path.exists():
            pd.DataFrame(columns=[
                'order_id', 'coffee_type', 'milk_type', 
                'cost', 'time', 'server_name'
            ]).to_csv(self.csv_path, index=False)

    def get_orders(self) -> pd.DataFrame:
        return pd.read_csv(self.csv_path, parse_dates=['time'])

    def add_order(self, order: CoffeeOrder) -> None:
        df = pd.read_csv(self.csv_path)
        new_order = pd.DataFrame([order.model_dump()])
        updated_df = pd.concat([df, new_order], ignore_index=True)
        updated_df.to_csv(self.csv_path, index=False)

    def get_order_by_id(self, order_id: int) -> dict:
        df = pd.read_csv(self.csv_path)
        order = df[df['order_id'] == order_id]
        return order.to_dict('records')[0] if not order.empty else None
