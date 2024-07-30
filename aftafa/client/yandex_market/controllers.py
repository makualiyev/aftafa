import json
from datetime import datetime
from typing import Optional, List
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from aftafa.client.yandex_market.client import ClientSession
from aftafa.client.yandex_market.routes import PostStocksOnWarehousesGenerate, GetReportsInfo
from aftafa.client.yandex_market.schema.website import WebCatalogProduct
from aftafa.client.yandex_market.crud import DBWebCatalogUpdater
from aftafa.client.yandex_market.models import engine as db_engine


class WebCatalogFileHandler:
    SCRAPED_FILES_DIR: str = r'E:\shoptalk\localpipeline_\scraper\YA\{}'

    def __init__(self, supplier: str) -> None:
        self.supplier = supplier
        # self.seller_id = self._get_seller_id()
        self.loadables: list[WebCatalogProduct | dict[str, Any] | None] = []
    
    # def _get_seller_id(self) -> int:
    #     stmt = text(f"""
    #             select
    #                 t2.id
    #             from
    #                 wildberries.supplier t1
    #                 left join wildberries.web_seller t2 on t1.id = t2.supplier_id
    #             where
    #                 t1.name = '{self.supplier}'
    #             """)
    #     with db_engine.connect() as conn:
    #         res = conn.execute(stmt).mappings().all()

    #     if len(res) == 0:
    #         return 0
    #     elif len(res) > 1:
    #         return 0
    #     return res[0].get('id')
    
    def _get_loaded_files(self, date: str | None = None) -> list[Path]:
        pth: Path = Path(self.SCRAPED_FILES_DIR.format(str(self.supplier)))
        if date:
            date = date
        else:
            date = datetime.now().strftime('%Y-%m-%d')

        files: list[Path] = [file_ for file_ in list(pth.glob('*.json')) if file_.stem.split('_')[1] == date]
        return files
    
    def _get_loadables(self, date: str | None = None, with_validation: bool = True) -> None:
        loaded_files = self._get_loaded_files(date=date)
        if not loaded_files:
            return None
        
        for file_ in self._get_loaded_files():
            with open(file_, 'rb') as f:
                json_ = json.loads(f.read())
                for json_entry in json_:
                    if with_validation:
                        catalog_response_schema = WebCatalogProduct(**json_entry).dict(by_alias=False)
                        catalog_response_schema['report_date'] = file_.stem.split('_')[1]
                        self.loadables.append(catalog_response_schema)
                    else:
                        json_entry['report_date'] = file_.stem.split('_')[1]
                        self.loadables.append(json_entry)

        return None
    
    def prepare_loadables(self, date: str | None = None) -> list[dict[str, str]]:
        prepared_loadables = []
        self._get_loadables(date=date)
        for loadable in self.loadables:
            loadable['meta_supplier'] = str(self.supplier)
            loadable['meta_report_date'] = loadable['report_date']
            prepared_loadables.append(loadable)
        return prepared_loadables
    
    def load_loadables_into_db(self) -> None:
        loadables = self.prepare_loadables()
        extraction_ts = datetime.now()
        updater = DBWebCatalogUpdater(extraction_ts=extraction_ts)

        for loadable_entry in loadables:
            updater.refresh(web_catalog_product_schema_=loadable_entry)

        print(f"Successfully updated loadables into db")


class FBSStocksController:
    def __init__(self) -> None:
        pass
    
    def get_raw_report(self, session: ClientSession, warehouse_ids: Optional[List[int]] = None) -> str:
        response = PostStocksOnWarehousesGenerate(warehouse_ids=warehouse_ids).make_request(session)
        report_id: str = response.json()['result']['reportId']
        GetReportsInfo(report_id=report_id).get_report(session)
        return report_id
    
    def get_shop_sku_id_mapping(self) -> int | None:
        shop_sku_mapping: pd.DataFrame = pd.read_sql_query(
                sql="""SELECT id AS shop_sku_id, shop_sku, supplier_id FROM yandex.shop_sku""",
                con=db_engine
            )
        return shop_sku_mapping
    

    def process_raw_report(self, report_id: str, session: ClientSession) -> dict[str, str]:
        FILE_DIR: str = r'E:\shoptalk\marketplaceapi_\loads\YA\reports\{}.xlsx'.format(report_id)
        # NEEDED_COLS: list[str] = ['Ваш SKU', 'SKU на Яндексе', 'Доступно для заказа', 'Склад', 'Статус продаж']
        REN_COLS = {
            'Ошибки': 'errors',
            'Предупреждения': 'warnings',
            'Ваш SKU *': 'shop_sku',
            'Название товара': 'shop_sku_name',
            'Доступное количество товара *': 'available'
        }
        df = (
                pd.read_excel(FILE_DIR, sheet_name='Список товаров', header=1)[list(REN_COLS.keys())].iloc[1:, :]
                    .reset_index(drop=True)
                    .rename(columns=REN_COLS)
        )
        df['supplier_id'] = int(session.supplier.id)
        df['shop_sku'] = df['shop_sku'].map(str)
        df[['errors', 'warnings']] = df[['errors', 'warnings']].fillna('')
        df['available'] = df['available'].fillna(0.0).map(int)
        # df['market_sku'] = df['market_sku'].map(lambda x: str(int(x)))
        df = pd.merge(
                    df,
                    self.get_shop_sku_id_mapping(),
                    left_on=['supplier_id', 'shop_sku'],
                    right_on=['supplier_id', 'shop_sku'],
                    how='left',
                    validate='m:1'
                )
        try:
            assert set(df[df['shop_sku_id'].isna()]['shop_sku']) == set(), 'Some empty shop sku ids'
        except AssertionError as e:
            print(e)
        return df.to_dict(orient='records')
    
    def process_to_db(self, records: dict) -> None:
        stmt = text("""
                    INSERT INTO yandex.ut_fbs_stocks_v2
                    (
                        supplier_id, shop_sku_id, shop_sku_name, available,
                        errors, warnings,
                        updated_at
                    ) 
                    VALUES (
                        :supplier_id, :shop_sku_id, :shop_sku_name, :available,
                        :errors, :warnings,
                        (now()::date)
                    )
                    ON CONFLICT ON CONSTRAINT ut_fbs_stocks_v2_supplier_id_shop_sku_id_updated_at_key
                    -- DO NOTHING
                    DO UPDATE
                    SET
                        available=EXCLUDED.available,
                        errors=EXCLUDED.errors,
                        warnings=EXCLUDED.warnings,
                        updated_at=EXCLUDED.updated_at;
                """)

        with db_engine.connect() as conn:
            for i in range(len(records)):
                try:
                    conn.execute(
                        stmt,
                        supplier_id=records[i]['supplier_id'],
                        shop_sku_id=records[i]['shop_sku_id'],
                        shop_sku_name=records[i]['shop_sku_name'],
                        available=records[i]['available'],
                        warnings=records[i]['warnings'],
                        errors=records[i]['errors']
                    )
                    conn.commit()
                except IntegrityError as e:
                    print(e)
                    continue
        print(f"Successfully loaded FBS stocks for this supplier ->")
