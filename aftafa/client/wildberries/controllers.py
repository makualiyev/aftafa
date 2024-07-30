from itertools import chain
from typing import Union
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from aftafa.client.wildberries.client import ClientSession
from aftafa.client.wildberries.models import engine as db_engine    
from aftafa.client.wildberries.routes import PostStocksByWarehouse


class FBSStockUpdater:
    def __init__(self, supplier: str) -> None:
        self.supplier = supplier

    def get_fbs_warehouses(self) -> list[str]:
        stmt = text(
                f"""
                select t1.id::varchar
                from wildberries.warehouse t1
                left join wildberries.supplier t2 ON t1.supplier_id = t2.id
                where t2.name = '{self.supplier}' 
                and is_active = true
            """)
        with db_engine.connect() as conn:
            res = conn.execute(
                    stmt
                ).mappings().all()
        return [record['id'] for record in res]
        
    def get_barcodes(self, with_var_ids: bool = False) -> list[str]:
        stmt = text(
            f"""
            select 
                t1.id AS variation_id,
                t1.barcode::varchar
            from wildberries.variation t1
            left join wildberries.nomenclature t2 on t1.nomenclature_id = t2.id
            left join wildberries.supplier t3 on t2.supplier_id = t3.id
            where t1.barcode != '' and
                t3.name = '{self.supplier}'
            """
        )
        with db_engine.connect() as conn:
            res = conn.execute(
                    stmt
                ).mappings().all()
        if not with_var_ids:
            return [record['barcode'] for record in res]
        return {record['barcode']: record['variation_id'] for record in res}
    
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
            self, warehouse_id: str, supplier: str, chunk: list[dict[str, Union[str, int]]]
                )  -> list[dict[str, Union[str, int]]]:
        variation_mappings: dict[str, int] = self.get_barcodes(with_var_ids=True)
        for record in chunk:
            record['warehouse_id'] = warehouse_id
            record['supplier_id'] = self.get_supplier_id(supplier=supplier)
            record['variation_id'] = variation_mappings.get(record['sku'])
            record['updated_at'] = datetime.today()
            record['barcode'] = record['sku']

        return chunk



    def get_fbs_stock_chunks(self, session: ClientSession) -> list[str]:
        skus_list: list[str] = self.get_barcodes()
        chunks = []
        for warehouse_id in self.get_fbs_warehouses():
            response_generator = PostStocksByWarehouse(warehouse_id=warehouse_id).get_chunks(session, load=skus_list)
            for response_chunk in response_generator:
                if not response_chunk.json()['stocks']:
                    continue
                chunks.append(self.populate_response_chunk(
                    warehouse_id=warehouse_id,
                    supplier=session.supplier.name,
                    chunk=response_chunk.json()['stocks']
                ))
        return list(chain(*chunks))

    def load_into_db(self, chunks: list[dict[str, str]]) -> None:
        stmt = text("""
                INSERT INTO wildberries.stocks_on_warehouses
                (
                    supplier_id, variation_id, warehouse_id,
                    barcode, amount,
                    updated_at
                ) 
                VALUES (
                    :supplier_id, :variation_id, :warehouse_id,
                    :barcode, :amount,
                    (now()::timestamptz)
                )
                ON CONFLICT ON CONSTRAINT uq__stocks_on_warehouses__variation_id_warehouse_id
                -- DO NOTHING
                DO UPDATE
                SET
                    amount=EXCLUDED.amount,
                    updated_at=EXCLUDED.updated_at""")
        
        with db_engine.connect() as conn:
            for i in range(len(chunks)):
                try:
                    conn.execute(
                        stmt,
                        {
                            'supplier_id': chunks[i]['supplier_id'],
                            'variation_id': chunks[i]['variation_id'],
                            'warehouse_id': chunks[i]['warehouse_id'],
                            'barcode': chunks[i]['barcode'],
                            'amount': chunks[i]['amount'],
                            'updated_at': chunks[i]['updated_at']
                        }                
                    )
                    conn.commit()
                except IntegrityError as e:
                    print(e)
                    continue

        print(f"Successfully loaded FBS stocks into the DB for the supplier -> {self.supplier}")


    

    

if __name__ == '__main__':
    pass