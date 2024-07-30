from pathlib import Path
from datetime import datetime
from typing import Union
import json

from sqlalchemy import text

import aftafa.client.wildberries.models as wb_models
import aftafa.client.wildberries.schemas as wb_schemas
from aftafa.client.wildberries.schema.website import V2CatalogResponse
from aftafa.client.wildberries.client import ClientSession
from aftafa.common.dal import session as db_session, engine as db_engine
from aftafa.utils.helpers import bcolors


class WebCatalogFileHandler:
    SCRAPED_FILES_DIR: str = r'E:\shoptalk\localpipeline_\scraper\WB\{}'

    def __init__(self, supplier: str) -> None:
        self.supplier = supplier
        self.seller_id = self._get_seller_id()
        self.loadables = []
    
    def _get_seller_id(self) -> int:
        stmt = text(f"""
                select
                    t2.id
                from
                    wildberries.supplier t1
                    left join wildberries.web_seller t2 on t1.id = t2.supplier_id
                where
                    t1.name = '{self.supplier}'
                """)
        with db_engine.connect() as conn:
            res = conn.execute(stmt).mappings().all()

        if len(res) == 0:
            return 0
        elif len(res) > 1:
            return 0
        return res[0].get('id')
    
    def _get_loaded_files(self) -> list[Path]:
        pth: Path = Path(self.SCRAPED_FILES_DIR.format(str(self.seller_id)))
        files: list[Path] = [file_ for file_ in list(pth.glob('*.json')) if file_.stem.split('_')[2] == datetime.now().strftime('%Y-%m-%d')]
        return files
    
    def _get_loadables(self) -> None:
        loaded_files = self._get_loaded_files()
        if not loaded_files:
            return None
        
        for file_ in self._get_loaded_files():
            with open(file_, 'rb') as f:
                json_ = json.loads(f.read())
                catalog_response_schema = V2CatalogResponse(**json_).dict(by_alias=False)
                catalog_response_schema['report_date'] = file_.stem.split('_')[2]
                self.loadables.append(catalog_response_schema)
        return None
    
    def prepare_loadables(self) -> list[dict[str, str]]:
        prepared_loadables = []
        self._get_loadables()
        for loadable in self.loadables:
            for product_ in loadable.get('data').get('products'):
                product_['meta_seller_id'] = str(self.seller_id)
                product_['meta_state'] = loadable.get('state')
                product_['meta_version'] = loadable.get('version')
                product_['meta_payload_version'] = loadable.get('payload_version')
                product_['meta_report_date'] = loadable['report_date']
                prepared_loadables.append(product_)
        return prepared_loadables
    
    def load_loadables_into_db(self) -> None:
        loadables = self.prepare_loadables()
        extraction_ts = datetime.now()
        updater = DBWebCatalogUpdater(extraction_ts=extraction_ts)

        for loadable_entry in loadables:
            updater.refresh(web_catalog_product_schema_=loadable_entry)

        print(f"Successfully updated loadables into db")

    

class DBWebCatalogUpdater:
    """
    """
    def __init__(self, extraction_ts: datetime) -> None:
        self.db_session = db_session
        self.extraction_ts = extraction_ts

    def prep_model(self, schema_: dict) -> wb_models.WebCatalogProduct:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in wb_models.WebCatalogProduct.__dict__ if not i.startswith('_')]
        web_catalog_schema: dict[str, str] = schema_
        web_catalog_schema['extracted_at'] = self.extraction_ts
        web_catalog_schema = {key: value for key, value in web_catalog_schema.items() if key in req_fields}
        return wb_models.WebCatalogProduct(**web_catalog_schema)

    def check_integrity(self, web_catalog_product_model: wb_models.WebCatalogProduct) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        web_catalog_in_db: wb_models.WebCatalogProduct = self.db_session.query(wb_models.WebCatalogProduct).filter(
            wb_models.WebCatalogProduct.meta_seller_id == str(web_catalog_product_model.meta_seller_id),
            wb_models.WebCatalogProduct.meta_report_date == web_catalog_product_model.meta_report_date,
            wb_models.WebCatalogProduct.id_ == str(web_catalog_product_model.id_)
        ).first()
        if web_catalog_in_db:
            return True
        return False

    def update(self, web_catalog_product_model: wb_models.WebCatalogProduct) -> None:
        """Updates Product entity"""
        web_catalog_product_model: wb_models.WebCatalogProduct = self.db_session.query(wb_models.WebCatalogProduct).filter(
            wb_models.WebCatalogProduct.meta_seller_id == str(web_catalog_product_model.meta_seller_id),
            wb_models.WebCatalogProduct.meta_report_date == web_catalog_product_model.meta_report_date,
            wb_models.WebCatalogProduct.id_ == str(web_catalog_product_model.id_)
        ).first()

        web_catalog_product_model.rating = web_catalog_product_model.rating

        self.db_session.commit()
        return web_catalog_product_model.id

    def create(self, web_catalog_product_model: wb_models.WebCatalogProduct) -> int:
        """Creates Product entity"""
        self.db_session.add(web_catalog_product_model)
        self.db_session.commit()
        return web_catalog_product_model.id
      
    def populate_web_catalog_product(self, schema_: dict[str, str], web_catalog_product_id_in_db: int) -> None:
        if schema_.get("sizes"):
            for size_ in schema_.get('sizes'):
                size_['price_basic'] = size_.get('price')['basic']
                size_['price_product'] = size_.get('price')['product']
                size_['price_total'] = size_.get('price')['total']
                size_['price_logistics'] = size_.get('price')['logistics']
                size_['price_return_'] = size_.get('price')['return_']

                DBWebCatalogProductSizeUpdater(extraction_ts=self.extraction_ts).refresh(
                    web_catalog_product_size_schema_=size_,
                    web_catalog_product_id_in_db=web_catalog_product_id_in_db
                )
        # if catalog_item_schema.get("suggested_goods")[0]:
        #     DBSuggestedGoodsUpdater(client_session=self.sesh).refresh(
        #         suggested_goods_schema=catalog_item_schema
        #     )

    def refresh(self, web_catalog_product_schema_: dict) -> None:
        web_catalog_product_model = self.prep_model(schema_=web_catalog_product_schema_)
        if self.check_integrity(web_catalog_product_model=web_catalog_product_model):
            web_catalog_product_id: int = self.update(web_catalog_product_model=web_catalog_product_model)
            self.populate_web_catalog_product(schema_=web_catalog_product_schema_, web_catalog_product_id_in_db=web_catalog_product_id)
            return None
        web_catalog_product_id: int = self.create(web_catalog_product_model=web_catalog_product_model)
        self.populate_web_catalog_product(schema_=web_catalog_product_schema_, web_catalog_product_id_in_db=web_catalog_product_id)
        return None
    

class DBWebCatalogProductSizeUpdater:
    """
    """
    def __init__(self, extraction_ts: datetime) -> None:
        self.db_session = db_session
        self.extraction_ts = extraction_ts

    def prep_model(self, schema_: dict, web_catalog_product_id_in_db: int) -> wb_models.WebCatalogProductSize:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in wb_models.WebCatalogProductSize.__dict__ if not i.startswith('_')]
        web_catalog_schema: dict[str, str] = schema_
        
        web_catalog_schema['web_catalog_product_id'] = web_catalog_product_id_in_db
        web_catalog_schema['extracted_at'] = self.extraction_ts

        web_catalog_schema = {key: value for key, value in web_catalog_schema.items() if key in req_fields}
        return wb_models.WebCatalogProductSize(**web_catalog_schema)

    def check_integrity(self, web_catalog_product_size_model: wb_models.WebCatalogProductSize) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        web_catalog_product_size_in_db: wb_models.WebCatalogProductSize = self.db_session.query(wb_models.WebCatalogProductSize).filter(
            wb_models.WebCatalogProductSize.web_catalog_product_id == web_catalog_product_size_model.web_catalog_product_id
        ).first()
        if web_catalog_product_size_in_db:
            return True
        return False

    def update(self, web_catalog_product_size_model: wb_models.WebCatalogProductSize) -> None:
        """Updates Product entity"""
        web_catalog_product_size_model_in_db: wb_models.WebCatalogProductSize = self.db_session.query(wb_models.WebCatalogProductSize).filter(
            wb_models.WebCatalogProductSize.web_catalog_product_id == web_catalog_product_size_model.web_catalog_product_id
        ).first()

        web_catalog_product_size_model_in_db.price_basic = web_catalog_product_size_model.price_basic
        web_catalog_product_size_model_in_db.price_product = web_catalog_product_size_model.price_product
        web_catalog_product_size_model_in_db.price_total = web_catalog_product_size_model.price_total
        web_catalog_product_size_model_in_db.price_logistics = web_catalog_product_size_model.price_logistics
        web_catalog_product_size_model_in_db.price_return_ = web_catalog_product_size_model.price_return_

        self.db_session.commit()

    def create(self, web_catalog_product_size_model: wb_models.WebCatalogProductSize) -> None:
        """Creates Product entity"""
        self.db_session.add(web_catalog_product_size_model)
        self.db_session.commit()

    def refresh(self, web_catalog_product_size_schema_: dict, web_catalog_product_id_in_db: int) -> None:
        web_catalog_product_model = self.prep_model(schema_=web_catalog_product_size_schema_, web_catalog_product_id_in_db=web_catalog_product_id_in_db)
        if self.check_integrity(web_catalog_product_size_model=web_catalog_product_model):
            self.update(web_catalog_product_size_model=web_catalog_product_model)
            return None
        self.create(web_catalog_product_size_model=web_catalog_product_model)
        return None
    
