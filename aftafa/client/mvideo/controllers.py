from itertools import chain
from typing import Union
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from aftafa.client.mvideo.client import ApiClient
from aftafa.client.mvideo.models import engine as db_engine    
from aftafa.client.mvideo.routes import GetCatalog
from aftafa.utils.helpers import to_lower


class FBSStockController:
    def __init__(self) -> None:
        pass

    def get_fbs_warehouses(self) -> list[str]:
        pass
    
    def get_supplier_id(self, supplier: str) -> int:
        stmt = text(
            f"""SELECT id FROM wildberries.supplier WHERE name = '{supplier}'"""
        )
        with db_engine.connect() as conn:
            res = conn.execute(
                stmt
            ).mappings().all()
        return res[0]['id']
    
    def populate_response_chunk(
            self,
            chunk: list[dict[str, Union[str, int]]]
                )  -> list[dict[str, Union[str, int]]]:
        new_chunk = []
        for record in chunk:
            if record.get('stocks'):
                stock_entry: list[dict[str, Union[float, str]]] = record.get('stocks').get('stocks')
                try:
                    assert len(stock_entry) == 1, "Stock entry for FBS stocks in MVM changed its behavior"
                except AssertionError as e:
                    print(e)
                if stock_entry:
                    stock_entry = stock_entry[0]
                    stock_entry_record = {to_lower(k): v for k, v in stock_entry.items() if k != 'history'}
                    stock_entry_record['material_number'] = stock_entry_record['material_code']
                    new_chunk.append(stock_entry_record)
        return new_chunk



    def get_fbs_stock_chunks(self, session: ApiClient) -> list[str]:
        
        chunks = []
        # for warehouse_id in self.get_fbs_warehouses():            # TODO: add warehouses
        for warehouse_code in ['R241']:
            response_generator = GetCatalog(
                                    filter_=f"""archived:false,lifeCycleStatus:VALIDATION_PASSED|PUBLISHED|UNPUBLISHED_CHANGES|CHANGES_IN_VALIDATION|CHANGES_FAILED,productType:MARKETPLACE|VENDOR_CATALOG,warehouseCode:{warehouse_code}""",
                                    fields_="+stocks"
                                ).get_chunks(session)
            for response_chunk in response_generator:
                chunks.append(
                    self.populate_response_chunk(
                            chunk=response_chunk.json()['content']
                        )
                )
        return list(chain(*chunks))

    def load_into_db(self, chunks: list[dict[str, str]]) -> None:
        stmt = text("""
                INSERT INTO mvm.product_stock
                (
                    material_number, warehouse_code, quantity,
                    available, reserved, date_start, date_end,
                    unit, updated_at
                ) 
                VALUES (
                    :material_number, :warehouse_code, :quantity,
                    :available, :reserved, :date_start, :date_end,
                    :unit, (now()::timestamptz)
                )
                ON CONFLICT ON CONSTRAINT uq__product_stock__warehouse_code_material_number
                -- DO NOTHING
                DO UPDATE
                SET
                    available=EXCLUDED.available,
                    quantity=EXCLUDED.quantity,
                    reserved=EXCLUDED.reserved,
                    date_start=EXCLUDED.date_start,
                    date_end=EXCLUDED.date_end,
                    updated_at=EXCLUDED.updated_at""")
        
        with db_engine.connect() as conn:
            for i in range(len(chunks)):
                try:
                    conn.execute(
                        stmt,
                        {
                            'material_number': chunks[i]['material_number'],
                            'warehouse_code': chunks[i]['warehouse_code'],
                            'quantity': chunks[i]['quantity'],
                            'available': chunks[i]['available'],
                            'reserved': chunks[i]['reserved'],
                            'date_start': chunks[i].get('date_start'),
                            'date_end': chunks[i].get('date_end'),
                            'unit': chunks[i]['unit']
                        }
                    )
                except IntegrityError as e:
                    print(e)
                    continue

        print(f"Successfully loaded FBS stocks into the DB for the supplier -> ")