from datetime import datetime, date

from aftafa.common.dal import engine, session as db_session
import aftafa.client.ozon.models as mod
import aftafa.client.ozon.schemas as val

        
class DBv2AnalyticsStockOnWarehousesUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(
            self, client_session,
            db_session = db_session, db_engine = engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def check_product_source(self, product_source_: int, product_offer_id_: str, supplier_id_: int) -> int:
        product_source_in_db: mod.ProductSource = (
            db_session.query(mod.ProductSource)
                    .filter(
                        mod.ProductSource.sku == int(product_source_)
                    )
                    .first()
                )
        if product_source_in_db:
            return 0
        else:
            product_in_db: mod.Product = (
                db_session.query(mod.Product)
                    .filter(
                        mod.Product.supplier_id == supplier_id_,
                        mod.Product.offer_id == product_offer_id_
                    )
            )
            if product_in_db.first():
                if product_in_db.count() > 1:
                    print(f"Failed to check this product it has duplicates --> {product_offer_id_}")
            else:
                print(f"Failed to find this product by offer id it doesn't exist ==> {product_offer_id_}")
                return -1
            
            product_source_to_add: mod.ProductSource = mod.ProductSource(
                product_id=product_in_db.first().product_id,
                is_enabled=True,
                sku=product_source_,
                source='discounted'
            )
            db_session.add(product_source_to_add)
            return 0


    def prep_model(self, schema_: val.analyticsStockOnWarehouseResultRows) -> mod.AnalyticsStockOnWarehouses:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in mod.AnalyticsStockOnWarehouses.__dict__ if not i.startswith('_')]
        stock_on_warehouses_schema: dict[str, str] = schema_.dict()
        
        stock_on_warehouses_schema['supplier_id'] = int(self.sesh.supplier.id)
        if stock_on_warehouses_schema['item_code'] == 'Не удалось найти артикул товара, обратитесь в поддержку с ID данного товара':
            stock_on_warehouses_schema['item_code'] = ''
            print(f"For this SKU {stock_on_warehouses_schema['sku']} there is no offer_id unfortunately")
        product_source_check: int = self.check_product_source(stock_on_warehouses_schema['sku'], stock_on_warehouses_schema['item_code'], int(self.sesh.supplier.id))
        if product_source_check == -1:
            return -1
        stock_on_warehouses_schema['updated_at'] = date.today()
        stock_on_warehouses_schema = {key: value for key, value in stock_on_warehouses_schema.items() if key in req_fields}
        
        return mod.AnalyticsStockOnWarehouses(**stock_on_warehouses_schema)
    
    def check_integrity(self, stock_on_warehouses_model: mod.AnalyticsStockOnWarehouses) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        stock_on_warehouses_queried: mod.AnalyticsStockOnWarehouses = self.db_session.query(mod.AnalyticsStockOnWarehouses).filter(
            mod.AnalyticsStockOnWarehouses.sku == stock_on_warehouses_model.sku,
            mod.AnalyticsStockOnWarehouses.warehouse_name == stock_on_warehouses_model.warehouse_name,
            mod.AnalyticsStockOnWarehouses.updated_at == stock_on_warehouses_model.updated_at
        )
        if stock_on_warehouses_queried.count() > 1:
            print(f"This stock on warehouses {stock_on_warehouses_model.sku} for this date {stock_on_warehouses_model.updated_at} has duplicates")
        stock_on_warehouses_in_db = stock_on_warehouses_queried.first()
        if stock_on_warehouses_in_db:
            return True
        return False
    
    def update(self, stock_on_warehouses_model: mod.AnalyticsStockOnWarehouses) -> None:
        """Updates Product entity"""
        stock_on_warehouses_in_db: mod.AnalyticsStockOnWarehouses = self.db_session.query(mod.AnalyticsStockOnWarehouses).filter(
            mod.AnalyticsStockOnWarehouses.sku == stock_on_warehouses_model.sku,
            mod.AnalyticsStockOnWarehouses.warehouse_name == stock_on_warehouses_model.warehouse_name,
            mod.AnalyticsStockOnWarehouses.updated_at == stock_on_warehouses_model.updated_at
        ).first()

        stock_on_warehouses_in_db.promised_amount = stock_on_warehouses_model.promised_amount
        stock_on_warehouses_in_db.free_to_sell_amount = stock_on_warehouses_model.free_to_sell_amount
        stock_on_warehouses_in_db.reserved_amount = stock_on_warehouses_model.reserved_amount
        stock_on_warehouses_in_db.item_name = stock_on_warehouses_model.item_name

        self.db_session.commit()

    def create(self, stock_on_warehouses_model: mod.AnalyticsStockOnWarehouses) -> None:
        """Creates Order entity"""
        self.db_session.add(stock_on_warehouses_model)
        self.db_session.commit()

    def refresh(self, stock_on_warehouses_schema_: dict) -> None:
        stock_on_warehouses_model_ = self.prep_model(schema_=stock_on_warehouses_schema_)
        if stock_on_warehouses_model_ == -1:
            return None
        if self.check_integrity(stock_on_warehouses_model=stock_on_warehouses_model_):
            self.update(stock_on_warehouses_model=stock_on_warehouses_model_)
            return None
        self.create(stock_on_warehouses_model=stock_on_warehouses_model_)
        return None
        

class DBDescriptionCategoryTreeUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(
            self,
            db_session = db_session, db_engine = engine,
            extraction_ts: datetime = datetime.now()
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        # self.sesh = client_session
        self.extraction_ts = extraction_ts


    def prep_model(self, schema_: dict) -> mod.CategoryTreeItem:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in mod.CategoryTreeItem.__dict__ if not i.startswith('_')]
        category_tree_schema = {key: value for key, value in schema_.items() if key in req_fields}
        category_tree_schema['_parent_id'] = schema_.get('_parent_id')          # might be null
        category_tree_schema['_extracted_at'] = self.extraction_ts

        return mod.CategoryTreeItem(**category_tree_schema)
    
    def check_integrity(self, category_tree_item_model: mod.CategoryTreeItem) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        category_tree_item_queried: mod.CategoryTreeItem = self.db_session.query(mod.CategoryTreeItem).filter(
            mod.CategoryTreeItem._parent_id == category_tree_item_model._parent_id,
            mod.CategoryTreeItem.description_category_id == category_tree_item_model.description_category_id,
            mod.CategoryTreeItem.type_id == category_tree_item_model.type_id
        )
        if category_tree_item_queried.count() > 1:
            print(f"This category_tree_item {category_tree_item_model.description_category_id} has duplicates")
        category_tree_item_in_db = category_tree_item_queried.first()
        if category_tree_item_in_db:
            return True
        return False
    
    def update(self, category_tree_item_model: mod.CategoryTreeItem) -> None:
        """Updates Product entity"""
        category_tree_item_in_db: mod.CategoryTreeItem = self.db_session.query(mod.CategoryTreeItem).filter(
            mod.CategoryTreeItem._parent_id == category_tree_item_model._parent_id,
            mod.CategoryTreeItem.description_category_id == category_tree_item_model.description_category_id,
            mod.CategoryTreeItem.type_id == category_tree_item_model.type_id
        ).first()

        category_tree_item_in_db.category_name = category_tree_item_model.category_name
        category_tree_item_in_db.type_name = category_tree_item_model.type_name
        category_tree_item_in_db.disabled = category_tree_item_model.disabled

        self.db_session.commit()

    def create(self, category_tree_item_model: mod.CategoryTreeItem) -> None:
        """Creates Order entity"""
        self.db_session.add(category_tree_item_model)
        self.db_session.commit()

    def refresh(self, category_tree_item_schema_: dict) -> None:
        category_tree_item_model_ = self.prep_model(schema_=category_tree_item_schema_)
        if self.check_integrity(category_tree_item_model=category_tree_item_model_):
            self.update(category_tree_item_model=category_tree_item_model_)
            return None
        self.create(category_tree_item_model=category_tree_item_model_)
        return None


def main():
    pass


if __name__ == "__main__":
    main()
