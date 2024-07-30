from base64 import standard_b64decode
from datetime import datetime, date, timedelta
import time
from typing import Optional, Tuple, Generator, Union

from sqlalchemy import exc, select
from pydantic import UUID4, ValidationError
from requests.models import Response

from aftafa.client.ozon.models import (
    session as db_session,
    Supplier,
    AnalyticsData,
    CampaignObjects,
    CampaignPlacement,
    CampaignProductPhrases,
    CampaignProductStopWords,
    CampaignProducts,
    CampaignSearchPromoProducts,
    Campaigns,
    Product,
    ProductAttributes,
    TSProductPrices,
    TSProductStocks,
    WarehouseFirstMileTypes,
    Category,
    Actions,
    ActionCandidates,
    ActionProducts,
    Warehouses,
    WarehouseDeliveryMethods,
    FBOPostings,
    FBOPostingsProducts,
    ProductSource,
    FBOPostingsPostingServices,
    ProductStocks,
    ProductPrices,
    ProductCommissions,
    SupplierActions,
    FBOPostingsProductsFinData,
    FBOPostingsProductsFinDataActions,
    FBOPostingsProductsFinDataItemServices,
    FBSPostings,
    FBSPostingsAnalyticsData,
    FBSPostingsDeliveryMethod,
    FBSPostingsPostingServices,
    FBSPostingsProducts,
    FBSPostingsProductsFinData,
    FBSPostingsProductsFinDataActions,
    FBSPostingsProductsFinDataItemServices,
    FBSPostingsProductsMandatoryMarks,
    FBOReturns,
    FBSReturns,
    FBOPostingsAnalyticsData,
    FinanceTransactions,
    FinanceTransactionsOperationPosting,
    FinanceTransactionsOperationItems,
    FinanceTransactionsOperationServices,
    AnalyticsItemTurnover,
    AnalyticsData,
    ProductRatings,
    ProductStocksFBS,
    SupplyOrders,
    SupplyOrderItems,
    CategoryTreeItem
)
from aftafa.client.ozon.handlers import (
    MPmethod,
    MPsesh,
    bcolors,
    UtlOrderReturn,
    UtlPostingReturn
)
import aftafa.client.ozon.schemas as schemas
from aftafa.client.ozon.crud import (
    DBv2AnalyticsStockOnWarehousesUpdater,
    DBDescriptionCategoryTreeUpdater
)


class GetCategoriesTree(MPmethod):
    def __init__(self, category_id: int = None, language: str = None) -> None:
        MPmethod.__init__(self, "GET", "/v1/categories/tree")
        self.category_id = category_id
        self.language = language
        self.params = {
                "category_id" : self.category_id,
                "language" : self.language or "DEFAULT"
            }

    def make_request(self, session: MPsesh) -> Response:
        with session.get(self.url, params=self.params) as response:
            if response.status_code == 200:
                self.validate_response(response=response.json())
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response: Response):
        try:
            schemas.GetCategoriesTree_Response(**response)
        except ValidationError as e:
            print('Validation failed ->', e.json())


class PostCategoryTree(MPmethod):
    def __init__(self, category_id: int = None, language: str = None) -> None:
        MPmethod.__init__(self, "POST", "/v2/category/tree")
        self.category_id = category_id
        self.language = language
        self.payload = {
                "category_id" : self.category_id,
                "language" : self.language or "DEFAULT"
            }

    def make_request(self, session : MPsesh, **kwargs) -> Response: 
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response.json())
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            schemas.GetCategoriesTree_Response(**response)
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session : MPsesh) -> None:
        """Handler of this method"""
        def process_entries(dict_entry : dict, parent_id : int = None) -> None:
            """Processes each entry of the 'categories' field in a response"""
            cat_id, cat_title, cat_parent_id = dict_entry['category_id'], dict_entry['title'], parent_id
            category_in_db = db_session.query(Category).filter_by(category_id=cat_id).first()
            if category_in_db:
                category_in_db.title = cat_title
                try:
                    assert category_in_db.parent_id == cat_parent_id
                except AssertionError:
                    print(f"This category's parents in the DB and via API don't match,  id - {cat_id}")
                    category_in_db.parent_id = cat_parent_id
            else:
                db_session.add(Category(
                    category_id=cat_id,
                    title=cat_title,
                    parent_id=cat_parent_id
                ))
            if dict_entry['children']:
                for cat in dict_entry['children']:
                    process_entries(dict_entry=cat, parent_id=dict_entry['category_id'])
            
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()
        
        for category_entry in self.make_request(session=session).json()['result']:
            process_entries(dict_entry=category_entry)


class PostDescriptionCategoryTree(MPmethod):
    """
    "https://api-seller.ozon.ru/v1/description-category/tree"
    """
    def __init__(self, language: str = "DEFAULT") -> None:
        MPmethod.__init__(self, "POST", "/v1/description-category/tree")
        self.language = language
        self.payload = {
                "language" : self.language
            }

    def make_request(self, session : MPsesh, **kwargs) -> Response: 
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response.json())
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            schemas.PostDescriptionCategoryTreeResponse(**response)
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session : MPsesh) -> None:
        """Handler of this method"""
        updater = DBDescriptionCategoryTreeUpdater()
        response = self.make_request(session=session)
        categories_dump = schemas.PostDescriptionCategoryTreeResponse(**response.json()).dict()

        for categories_dump_entry in categories_dump:
            updater.refresh(category_tree_item_schema_=categories_dump_entry)

        print(bcolors.OKCYAN + f'Successfully transitioned description categories to the db for {session.supplier.name}' + bcolors.ENDC)
        



class PostProductList(MPmethod):
    def __init__(
        self, 
        offer_id: list = None, 
        product_id: list = None, 
        visibility: str = "ALL", 
        limit: int = 1000,
        last_id: str = None
    ) -> None:

        MPmethod.__init__(self, "POST", "/v2/product/list")
        self.payload: dict = {
                "filter": {
                    "offer_id": offer_id,
                    "product_id": product_id,
                    "visibility": visibility
                },
                "limit": limit,
                "last_id": last_id
            }

    def make_request(self, session: MPsesh, **kwargs) -> Response: 
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')
    
    def validate_response(self,  response : Response):
        try:
            schemas.PostProductList_Response(**response.json()['result'])
            for product_json in response.json()['result']['items']:
                schemas.PostProductList_Product(**product_json)
        except ValidationError as e:
            print('Validation failed ->', e.json())
        
    def process_to_db(self, session : MPsesh) -> None:
        """Handler of this method"""
        def process_entries(dict_entry : dict) -> None:
            """Processes each entry of the 'items' field in a response"""
            product_in_db = db_session.query(Product).filter_by(product_id=dict_entry['product_id']).first()
            if product_in_db:
                product_in_db.offer_id = dict_entry['offer_id']
            else:
                db_session.add(Product(
                    product_id=dict_entry['product_id'],
                    offer_id=dict_entry['offer_id'],
                    supplier_id=int(session.supplier.id)
                ))

            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()
            
        with self.make_request(session) as response:
            while not response.json()['result']['total'] < self.payload['limit']:
                for item in response.json['result']['items']:
                    process_entries(item)
                last_id = response.json()['result']['last_id']
                response = self.make_request(session, **{"last_id" : last_id})
            else:
                for item in response.json()['result']['items']:
                    process_entries(item)        


class PostProductInfo(MPmethod):
    def __init__(self, offer_id : str = None, product_id : int = None, sku : int = None) -> None:

        MPmethod.__init__(self, "POST", "/v2/product/info")
        self.payload = {
                    "offer_id" : offer_id,
                    "product_id" : product_id,
                    "sku" : sku
                }

    def make_request(self, session : MPsesh) -> Response: 
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
    
    def validate_response(self, response : Response):
        try:
            schemas.PostProductInfo(**response.json()['result'])
        except ValidationError as e:
            print('Validation failed ->', e.json())


class PostProductInfoList(MPmethod):
    def __init__(self, offer_id : list[str] = None, product_id : list[int] = None, sku : list[int] = None) -> None:

        MPmethod.__init__(self, "POST", "/v2/product/info/list")
        self.payload = {
                    "offer_id" : offer_id,
                    "product_id" : product_id,
                    "sku" : sku
                }

    def make_request(self, session : MPsesh, **kwargs) -> Response: 
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response)
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
    
    def validate_response(self, response : Response):
        try:
            schemas.PostProductInfoList(**response.json()['result'])
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session : MPsesh) -> None:
        """first we get all the product ids for a given supplier"""
        def split_into_chunks(lst : list, n_size : int) -> Generator[Response, None, None]:
            """Used to split product ids into small chunks of a size 100"""                         #TODO: it was 1000 till recently, but it provoked 
            for i in range(0, len(lst), n_size):                                                    # inadequate behaviour from the server, so changed it to 100
                yield lst[i:i + n_size]
        
        def process_entries(dict_entry : dict) -> None:
            """Processes each entry of the 'items' field in a response"""
            # def check_category_integrity(dict_entry: dict, db_item: Product) -> Product:
            #     """Checks whether the category fetched from API is compliant with our
            #     base or not"""
            #     category_in_db: Category = db_session.query(Category).filter_by(category_id=dict_entry['category_id']).first()
            #     if not category_in_db:
            #         print(
            #             bcolors.FAIL,
            #             f"Couldn't match this category {dict_entry['category_id']} of product {dict_entry['offer_id']} in the DB :/",
            #             bcolors.ENDC
            #         )
            #         return db_item
            #     db_item.category_id = dict_entry['category_id']
            #     return db_item

            def check_category_integrity(dict_entry: dict, db_item: Product) -> Optional[Product]:
                """Checks whether the category fetched from API is compliant with our
                base or not"""
                category_in_db: CategoryTreeItem = db_session.query(CategoryTreeItem).filter_by(
                                                _parent_id=dict_entry['description_category_id'],
                                                type_id=dict_entry['type_id']
                                            ).first()
                if not category_in_db:
                    print(
                        bcolors.FAIL,
                        f"Couldn't match this category {dict_entry['description_category_id']} / {dict_entry['type_id']} \
                            of product {dict_entry['offer_id']} in the DB :/",
                        bcolors.ENDC
                    )
                    return db_item
                db_item.category_tree_item_id = category_in_db._id
                return db_item


            
            item_in_db = db_session.query(Product).filter_by(product_id=dict_entry['id']).first()
            if item_in_db:
                item_in_db = check_category_integrity(dict_entry=dict_entry, db_item=item_in_db)
                item_in_db.description_category_id = dict_entry['description_category_id']
                item_in_db.type_id = dict_entry['type_id']
                item_in_db.barcode = dict_entry['barcode']
                item_in_db.is_kgt = dict_entry['is_kgt']
                item_in_db.name = dict_entry['name']
                item_in_db.created_at = datetime.strptime(dict_entry['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                item_in_db.visible = dict_entry['visible']
                item_in_db.color_image = dict_entry['color_image']
                item_in_db.primary_image = dict_entry['primary_image']
                if dict_entry.get('sku'):
                    item_in_db.sku = dict_entry.get('sku')
                    item_srcs_in_db = db_session.query(ProductSource).filter_by(product_id=dict_entry['id'], sku=dict_entry['sku']).first()
                    if item_srcs_in_db:
                        item_srcs_in_db.source = 'fbo'
                        item_srcs_in_db.is_enabled = True
                    else:
                        db_session.add(ProductSource(
                            product_id=dict_entry['id'],
                            sku=dict_entry['sku'],
                            source='fbo',
                            is_enabled=True
                        ))



            for source in dict_entry['sources']:
                item_srcs_in_db = db_session.query(ProductSource).filter_by(product_id=dict_entry['id'], sku=source['sku']).first()
                if item_srcs_in_db:
                    item_srcs_in_db.source = source['source']
                    item_srcs_in_db.is_enabled = source['is_enabled']
                else:
                    db_session.add(ProductSource(
                        product_id=dict_entry['id'],
                        sku=source['sku'],
                        source=source['source'],
                        is_enabled=source['is_enabled']
                    ))
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()

        product_ids = [
            db_item.product_id for db_item in
            db_session.query(Product).filter_by(supplier_id=session.supplier.id).all()
        ]
        
        # this procedure is needed for payloads to be less than maximum of 1000 entries
        for chunk in split_into_chunks(lst=product_ids, n_size=100):
            with self.make_request(session=session, **{"product_id" : chunk}) as response:
                for item_entry in response.json()['result']['items']:
                    process_entries(item_entry)


class PostProductInfoAttributesList(MPmethod):
    def __init__(
        self,
        offer_id : list[str] = None,
        product_id : list[int] = None,
        visibility : str = None,
        last_id : str = None,
        limit : int = 100,
        sort_by : str = None,
        sort_dir : str = None
    ) -> None:

        MPmethod.__init__(self, "POST", "/v3/products/info/attributes")
        self.payload : dict = {
            "filter" : {
                "offer_id" : offer_id,
                "product_id" : product_id,
                "visibility" : visibility
            },
            "limit" : limit,
            "last_id" : last_id,
            "sort_by" : sort_by,
            "sort_dir" : sort_dir
        }

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
    
    def validate_response(self, response : Response):
        try:
            for attributes_entry in response.json()['result']:
                schemas.PostProductInfoAttributesList(**attributes_entry)
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session : MPsesh) -> None:
        """This method is for getting result as json str"""
        
        # first we need to define what are product ids to know whaat to fetch
        if self.payload['filter']['product_id']:
            product_ids : list[int] = self.payload['filter']['product_id']
        else:
            product_ids : list[int] = [
                db_item.product_id for db_item in
                db_session.query(Product).filter_by(supplier_id=session.supplier.id).all()
            ]
        def set_counter(**kwargs) -> Tuple[int]:
            """This function counts how many requests are needed to fetch all the products'
                attributes."""
            self.payload.update(**kwargs)
            limit : int = self.payload['limit']
            if (len(product_ids) // limit) and (len(product_ids) % limit):
                return ((len(product_ids) // limit) + 1, limit)
            elif (len(product_ids) // limit) and not (len(product_ids) % limit):
                return ((len(product_ids) // limit), limit)
            else:
                return (1, limit)
        
        counter, limit = set_counter()
        chunks : list[int] = []
        for i in range(counter):
            chunks.append(product_ids[(i*limit):(i*limit + limit)])
        
        for chunk in chunks:
            with self.make_request(session=session, **{"filter" : {"product_id" : chunk}}) as response:
                yield response.json()

    def process_to_db(self, session : MPsesh) -> None:
        """Handler of this route to the DB"""
        def process_entries(dict_entry : dict) -> None:
            """Processes each entry of the 'attributes' field in a response"""
            def process_complex_attrs(complex_attr_entry : dict) -> Tuple[str]:
                # First we have to check if there 
                attr_ids : list[int] = [attr['attribute_id'] for attr in complex_attr_entry]
                if 85 in attr_ids:
                    try:
                        _brand : str = complex_attr_entry[attr_ids.index(85)]['values'][0]['value']
                    except IndexError as e:
                        print(f"Tracing error with complex attrs - {complex_attr_entry[attr_ids.index(85)]['values']}")
                        _brand : str = 'no_brand'
                elif 31 in attr_ids:
                    try:
                        _brand : str = complex_attr_entry[attr_ids.index(31)]['values'][0]['value']
                    except IndexError as e:
                        print(f"Tracing error with complex attrs - {complex_attr_entry[attr_ids.index(31)]['values']}")
                        _brand : str = 'no_brand'
                else:
                    _brand : str = 'no_brand'
                    
                if 9048 in attr_ids:
                    try:
                        _model : str = complex_attr_entry[attr_ids.index(9048)]['values'][0]['value']
                    except IndexError as e:
                        print(f"Tracing error with complex attrs - {complex_attr_entry[attr_ids.index(9048)]['values']}")
                        _model : str = 'no_model'
                else:
                    _model : str = 'no_model'
                if 9461 in attr_ids:
                    if complex_attr_entry[attr_ids.index(9461)]['values']:
                        _commercial_type : str = complex_attr_entry[attr_ids.index(9461)]['values'][0]['value']
                    else:
                        _commercial_type : str = 'no_commercial_type'
                else:
                    _commercial_type : str = 'no_commercial_type'

                return _brand, _model, _commercial_type

            prod_attr_in_db = db_session.query(ProductAttributes).filter_by(product_id=dict_entry['id']).first()
            _brand, _model, _commercial_type = process_complex_attrs(complex_attr_entry=dict_entry['attributes'])
            
            if prod_attr_in_db:
                prod_attr_in_db.height = dict_entry['height']
                prod_attr_in_db.depth = dict_entry['depth']
                prod_attr_in_db.width = dict_entry['width']
                prod_attr_in_db.weight = dict_entry['weight']
                prod_attr_in_db.weight_unit = dict_entry['weight_unit']
                prod_attr_in_db.dimension_unit = dict_entry['dimension_unit']
                prod_attr_in_db.brand = _brand
                prod_attr_in_db.model = _model
                prod_attr_in_db.commercial_type = _commercial_type
            else:
                db_session.add(ProductAttributes(
                    product_id=dict_entry['id'],
                    height=dict_entry['height'],
                    depth=dict_entry['depth'],
                    width=dict_entry['width'],
                    weight=dict_entry['weight'],
                    weight_unit=dict_entry['weight_unit'],
                    dimension_unit=dict_entry['dimension_unit'],
                    brand=_brand,
                    model=_model,
                    commercial_type=_commercial_type
                ))
            
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()
        
        for chunk in self.get_chunks(session=session):
            assert chunk.get('result') != None
            for attr_entry in chunk['result']:
                process_entries(attr_entry)


class PostProductRatingBySKU(MPmethod):
    def __init__(self, skus : list[str]) -> None:

        MPmethod.__init__(self, "POST", "/v1/product/rating-by-sku")
        # self.cont: Optional[list[tuple[str, str]]] = None
        # self.sku_mapping: dict[str, int] = None
        self.payload : dict = {
            'skus': skus
        }

    def sku_list(self, session: MPsesh) -> Optional[list[tuple[str, str]]]:
        stmt = (
                    select(Product.product_id, ProductSource.sku)
                        .join(ProductSource, Product.product_id == ProductSource.product_id)
                        .where(Product.supplier_id == session.supplier.id)
                        .where(Product.visible == True)
                        .where(ProductSource.source == 'fbo')
                        .where(ProductSource.is_enabled == True)
                )
        self.cont = db_session.execute(stmt).fetchall()
        return self.cont

    # def sku_mapping(self) -> dict[str, int]:
    #     return {str(k): v for k, v in self.sku_list}

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
    
    def validate_response(self, response : Response):
        try:
            schemas.PostProductRatingBySKU(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session : MPsesh) -> None:
        """This method is for getting result as json str"""
        def split_into_chunks(lst : list, n_size : int) -> Generator[Response, None, None]:
            """Used to split product ids into small chunks of a size 100"""                         #TODO: it was 1000 till recently, but it provoked 
            for i in range(0, len(lst), n_size):                                                    # inadequate behaviour from the server, so changed it to 100
                yield lst[i:i + n_size]

        for chunk in split_into_chunks(
                    lst=[str(prod_row[1]) for prod_row in self.sku_list(session=session)],
                    n_size=100
                ):
            resp = self.make_request(session=session, **{"skus": chunk})
            yield resp

    def process_to_db(self, session: MPsesh) -> None:
        """Handler of this route to the DB"""
        def add_rating(sku_entry: dict, prod_id: int) -> None:
            rating_in_db: Optional[ProductRatings] = db_session.query(ProductRatings).filter(ProductRatings.product_id == prod_id).first()
            if not rating_in_db:
                db_session.add(
                    ProductRatings(
                        product_id=prod_id,
                        rating=sku_entry['rating']
                    )
                )
                db_session.commit()
                return True
            rating_in_db.rating = sku_entry['rating']
            db_session.commit()
            

        sku_mapping: dict[str, int] = {str(v): k for k, v in self.sku_list(session=session)}

        for chunk in self.get_chunks(session=session):
            for prod_rating in chunk.json()['products']:
                add_rating(sku_entry=prod_rating, prod_id=sku_mapping[str(prod_rating['sku'])])


class PostProductInfoStocksByWarehouseFBS(MPmethod):
    def __init__(
        self,
        fbs_sku: list[str] = None
    ) -> None:

        MPmethod.__init__(self, "POST", "/v1/product/info/stocks-by-warehouse/fbs")
        self.payload : dict = {
            "sku": fbs_sku
        }

    def sku_list(self, session: MPsesh) -> Optional[list[tuple[str, str]]]:
        stmt = (
                    select(Product.product_id, ProductSource.sku)
                        .join(ProductSource, Product.product_id == ProductSource.product_id)
                        .where(Product.supplier_id == session.supplier.id)
                        .where(Product.visible == True)
                        .where(ProductSource.source == 'fbo')
                        .where(ProductSource.is_enabled == True)
                )
        self.cont = db_session.execute(stmt).fetchall()
        return self.cont

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
    
    def validate_response(self, response : Response):
        try:
            schemas.PostProductInfoStocksByWarehouseFBS(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session : MPsesh) -> None:
        """This method is for getting result as json str"""
        def split_into_chunks(lst : list, n_size : int) -> Generator[Response, None, None]:
            """Used to split product ids into small chunks of a size 500"""                         #TODO: it was 1000 till recently, but it provoked 
            for i in range(0, len(lst), n_size):                                                    # inadequate behaviour from the server, so changed it to 100
                yield lst[i:i + n_size]

        for chunk in split_into_chunks(
                    lst=[str(prod_row[1]) for prod_row in self.sku_list(session=session)],
                    n_size=500
                ):
            resp = self.make_request(session=session, **{"sku": chunk})
            yield resp

    def process_to_db(self, session : MPsesh) -> None:
        """Handler of this route to the DB"""
        def add_fbs_stock(fbs_stock_entry: dict) -> None:
            fbs_stock_in_db: Optional[ProductStocksFBS] = db_session.query(ProductStocksFBS).filter(
                ProductStocksFBS.fbs_sku == fbs_stock_entry['fbs_sku'],
                ProductStocksFBS.fbs_warehouse == fbs_stock_entry['warehouse_id']
            ).first()
            if not fbs_stock_in_db:
                db_session.add(
                    ProductStocksFBS(
                        fbs_sku=fbs_stock_entry['fbs_sku'],
                        fbs_warehouse=fbs_stock_entry['warehouse_id'],
                        present=fbs_stock_entry['present'],
                        reserved=fbs_stock_entry['reserved'],
                    )
                )
                db_session.commit()
                return True
            fbs_stock_in_db.present = fbs_stock_entry['present']
            fbs_stock_in_db.reserved = fbs_stock_entry['reserved']
            db_session.commit()

        for chunk in self.get_chunks(session=session):
            for fbs_stock_entry in chunk.json()['result']:
                add_fbs_stock(fbs_stock_entry=fbs_stock_entry)
        
          
class PostProductInfoStocksList(MPmethod):
    def __init__(
        self,
        offer_id : str = None,
        product_id : int = None,
        visibility : str = "ALL",
        limit : int = 1000
    ) -> None:

        MPmethod.__init__(self, "POST", "/v3/product/info/stocks")
        self.payload : dict = {
            "filter" : {
                "offer_id" : offer_id,
                "product_id" : product_id,
                "visibility" : visibility
            },
            "limit" : limit
        }

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
    
    def validate_response(self, response : Response):
        try:
            schemas.PostProductInfoStocksList(**response.json()['result'])
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session : MPsesh) -> None:
        """Handler of this route to the DB"""
        def process_entries_as_ts(dict_entry : dict) -> None:
            """Processes each entry of stocks and adds it into the DB for time series, granularity - day"""
            for stock_entry in dict_entry['stocks']:
                if not stock_entry['type'] == 'fbo':
                    continue
                stocks_ts_in_db = db_session.query(TSProductStocks).filter_by(
                                                product_id=dict_entry['product_id'], updated_at=datetime.now().date()
                                                                         ).first()
                if stocks_ts_in_db:
                    stocks_ts_in_db.present = stock_entry['present']
                    stocks_ts_in_db.reserved = stock_entry['reserved']
                else:
                    db_session.add(TSProductStocks(
                        product_id=dict_entry['product_id'],
                        present=stock_entry['present'],
                        reserved=stock_entry['reserved']
                    ))
                    try:
                        db_session.commit()
                    except exc.IntegrityError as e:
                        print('Committing failed -> ', e)
                        db_session.rollback()


        def process_entries(dict_entry : dict) -> None:
            """Processes each entry of the 'attributes' field in a response"""
            for stock_entry in dict_entry['stocks']:
                prod_in_db = db_session.query(ProductStocks).filter_by(product_id=dict_entry['product_id'], type=stock_entry['type']).first()
                if prod_in_db:
                    prod_in_db.present = stock_entry['present']
                    prod_in_db.reserved = stock_entry['reserved']
                else:
                    db_session.add(ProductStocks(
                        product_id=dict_entry['product_id'],
                        type=stock_entry['type'],
                        present=stock_entry['present'],
                        reserved=stock_entry['reserved']
                    ))
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()

        with self.make_request(session=session) as response:
            last_id = response.json()['result']['last_id']
            last_id : str = response.json()['result']['last_id']
            last_id_decoded : str = standard_b64decode(last_id).decode('utf-8')
            if standard_b64decode(last_id).decode('utf-8') != "null":
                print(bcolors.WARNING + f"There is another last id for stocks in this one {session.supplier.name}, look at it \
                \n so here is what it says {last_id_decoded}" + bcolors.ENDC)
            for item in response.json()['result']['items']:
                process_entries(item)
                process_entries_as_ts(item)

                
class PostProductInfoPricesList(MPmethod):
    def __init__(
        self,
        offer_id : str = None,
        product_id : int = None,
        visibility : str = "ALL",
        limit : int = 1000,
        last_id: str = None
    ) -> None:

        MPmethod.__init__(self, "POST", "/v4/product/info/prices")
        self.payload : dict = {
            "filter" : {
                "offer_id" : offer_id,
                "product_id" : product_id,
                "visibility" : visibility
            },
            "last_id" : last_id,
            "limit" : limit
        }
    
    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)                       # TODO : // think about addind validators right after getting the response from the server
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")

    def validate_response(self, response : Response):
        try:
            schemas.PostProductInfoPricesList(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session : MPsesh) -> None:
        """Handler of this route to the DB"""
        def process_entries_as_ts(dict_entry : dict) -> None:
            """Processes each entry of prices and adds it into the DB for time series, granularity - day"""
            price_item = dict_entry['price']
            prices_ts_in_db = db_session.query(TSProductPrices).filter_by(
                                            product_id=dict_entry['product_id'], updated_at=datetime.now().date()
                                                                        ).first()
            if prices_ts_in_db:
                prices_ts_in_db.marketing_price = int(price_item['marketing_price'][:-5]) if price_item['marketing_price'] else None
                prices_ts_in_db.price = int(price_item['price'][:-5]) if price_item['price'] else None
                prices_ts_in_db.old_price = int(price_item['old_price'][:-5]) if price_item['old_price'] else None
            else:
                db_session.add(TSProductPrices(
                    product_id=dict_entry['product_id'],
                    marketing_price=int(price_item['marketing_price'][:-5]) if price_item['marketing_price'] else None,
                    price=int(price_item['price'][:-5]) if price_item['price'] else None,
                    old_price=int(price_item['old_price'][:-5]) if price_item['old_price'] else None
                ))
                try:
                    db_session.commit()
                except exc.IntegrityError as e:
                    print('Committing failed -> ', e)
                    db_session.rollback()

        def process_entries(dict_entry : dict) -> None:
            """Processes each entry of the 'attributes' field in a response"""
            prod_attr_in_db = db_session.query(ProductAttributes).filter_by(product_id=dict_entry['product_id']).first()
            if prod_attr_in_db:
                prod_attr_in_db.volume_weight = dict_entry['volume_weight']

            price_item = dict_entry['price']
            prod_price_in_db = db_session.query(ProductPrices).filter_by(product_id=dict_entry['product_id']).first()
            if prod_price_in_db:
                    # prod_price_in_db.buybox_price = int(price_item['buybox_price'][:-5]) if price_item['buybox_price'] else None
                prod_price_in_db.marketing_price = int(price_item['marketing_price'][:-5]) if price_item['marketing_price'] else None
                prod_price_in_db.marketing_seller_price = int(price_item['marketing_seller_price'][:-5]) if price_item['marketing_seller_price'] else None
                prod_price_in_db.min_ozon_price = int(price_item['min_ozon_price'][:-5]) if price_item['min_ozon_price'] else None
                prod_price_in_db.old_price = int(price_item['old_price'][:-5]) if price_item['old_price'] else None
                prod_price_in_db.premium_price = int(price_item['premium_price'][:-5]) if price_item['premium_price'] else None
                prod_price_in_db.price = int(price_item['price'][:-5]) if price_item['price'] else None
                prod_price_in_db.recommended_price = int(price_item['recommended_price'][:-5]) if price_item['recommended_price'] else None
                # prod_price_in_db.min_price = int(price_item['min_price'][:-5]) if price_item['min_price'] else None
                prod_price_in_db.vat = float(price_item['vat']) if price_item['vat'] else None
                prod_price_in_db.price_index = float(dict_entry['price_index']) if dict_entry['price_index'] else None
            else:
                db_session.add(ProductPrices(
                    product_id=dict_entry['product_id'],
                    # buybox_price = int(price_item['buybox_price'][:-5]) if price_item['buybox_price'] else None,
                    marketing_price = int(price_item['marketing_price'][:-5]) if price_item['marketing_price'] else None,
                    marketing_seller_price = int(price_item['marketing_seller_price'][:-5]) if price_item['marketing_seller_price'] else None,
                    min_ozon_price = int(price_item['min_ozon_price'][:-5]) if price_item['min_ozon_price'] else None,
                    old_price = int(price_item['old_price'][:-5]) if price_item['old_price'] else None,
                    premium_price = int(price_item['premium_price'][:-5]) if price_item['premium_price'] else None,
                    price = int(price_item['price'][:-5]) if price_item['price'] else None,
                    recommended_price = int(price_item['recommended_price'][:-5]) if price_item['recommended_price'] else None,
                    # min_price = int(price_item['min_price'][:-5]) if price_item['min_price'] else None,
                    vat = float(price_item['vat']) if price_item['vat'] else None,
                    price_index = float(dict_entry['price_index']) if dict_entry['price_index'] else None
                ))
            comm_item = dict_entry['commissions']
            prod_comm_in_db = db_session.query(ProductCommissions).filter_by(product_id=dict_entry['product_id']).first()
            if prod_comm_in_db:
                prod_comm_in_db.fbo_deliv_to_customer_amount = comm_item['fbo_deliv_to_customer_amount']
                prod_comm_in_db.fbo_direct_flow_trans_max_amount = comm_item['fbo_direct_flow_trans_max_amount']
                prod_comm_in_db.fbo_direct_flow_trans_min_amount = comm_item['fbo_direct_flow_trans_min_amount']
                prod_comm_in_db.fbo_fulfillment_amount = comm_item['fbo_fulfillment_amount']
                prod_comm_in_db.fbo_return_flow_amount = comm_item['fbo_return_flow_amount']
                prod_comm_in_db.fbo_return_flow_trans_min_amount = comm_item['fbo_return_flow_trans_min_amount']
                prod_comm_in_db.fbo_return_flow_trans_max_amount = comm_item['fbo_return_flow_trans_max_amount']
                prod_comm_in_db.fbs_deliv_to_customer_amount = comm_item['fbs_deliv_to_customer_amount']
                prod_comm_in_db.fbs_direct_flow_trans_max_amount = comm_item['fbs_direct_flow_trans_max_amount']
                prod_comm_in_db.fbs_direct_flow_trans_min_amount = comm_item['fbs_direct_flow_trans_min_amount']
                prod_comm_in_db.fbs_first_mile_min_amount = comm_item['fbs_first_mile_min_amount']
                prod_comm_in_db.fbs_first_mile_max_amount = comm_item['fbs_first_mile_max_amount']
                prod_comm_in_db.fbs_return_flow_amount = comm_item['fbs_return_flow_amount']
                prod_comm_in_db.fbs_return_flow_trans_max_amount = comm_item['fbs_return_flow_trans_max_amount']
                prod_comm_in_db.fbs_return_flow_trans_min_amount = comm_item['fbs_return_flow_trans_min_amount']
                prod_comm_in_db.sales_percent = comm_item['sales_percent']
            else:
                db_session.add(ProductCommissions(
                    product_id=dict_entry['product_id'],
                    fbo_deliv_to_customer_amount=comm_item['fbo_deliv_to_customer_amount'],
                    fbo_direct_flow_trans_max_amount=comm_item['fbo_direct_flow_trans_max_amount'],
                    fbo_direct_flow_trans_min_amount=comm_item['fbo_direct_flow_trans_min_amount'],
                    fbo_fulfillment_amount=comm_item['fbo_fulfillment_amount'],
                    fbo_return_flow_amount=comm_item['fbo_return_flow_amount'],
                    fbo_return_flow_trans_min_amount=comm_item['fbo_return_flow_trans_min_amount'],
                    fbo_return_flow_trans_max_amount=comm_item['fbo_return_flow_trans_max_amount'],
                    fbs_deliv_to_customer_amount=comm_item['fbs_deliv_to_customer_amount'],
                    fbs_direct_flow_trans_max_amount=comm_item['fbs_direct_flow_trans_max_amount'],
                    fbs_direct_flow_trans_min_amount=comm_item['fbs_direct_flow_trans_min_amount'],
                    fbs_first_mile_min_amount=comm_item['fbs_first_mile_min_amount'],
                    fbs_first_mile_max_amount=comm_item['fbs_first_mile_max_amount'],
                    fbs_return_flow_amount=comm_item['fbs_return_flow_amount'],
                    fbs_return_flow_trans_max_amount=comm_item['fbs_return_flow_trans_max_amount'],
                    fbs_return_flow_trans_min_amount=comm_item['fbs_return_flow_trans_min_amount'],
                    sales_percent=comm_item['sales_percent']
            ))

            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()

        with self.make_request(session=session) as response:
            last_id : str = response.json()['result']['last_id']
            last_id_decoded : str = standard_b64decode(last_id).decode('utf-8')
            if standard_b64decode(last_id).decode('utf-8') != "null":
                print(bcolors.WARNING + f"There is another last id for prices in this one {session.supplier.name}, look at it \
                \n so here is what it says {last_id_decoded}" + bcolors.ENDC)
            if response.json()['result']['total'] >= 1000:
                print(bcolors.WARNING + f"There is another page for prices for this one {session.supplier.name}, look at it" + bcolors.ENDC)
            for item in response.json()['result']['items']:
                process_entries(item)
                process_entries_as_ts(item)


class GetActionsList(MPmethod):
    def __init__(
        self,
        page : int = 1,
        page_size : int = 1000
    ) -> None:

        MPmethod.__init__(self, "GET", "/v1/actions")

        self.payload : dict = {
            "page" : page,
            "page_size" : page_size
        }
    
    def make_request(self, session : MPsesh) -> Response:
        with session.get(self.url) as response:
            if response.status_code == 200:
                self.validate_response(response=response)                       # TODO : // think about addind validators right after getting the response from the server
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")

    def validate_response(self, response : Response):
        try:
            for entry in response.json()['result']:
                schemas.GetActionsList(**entry)
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session : MPsesh) -> None:
        """Handler of this route to the DB"""
        def process_entries(dict_entry : dict) -> None:
            """Processes each entry of the 'attributes' field in a response"""
            action_in_db = db_session.query(Actions).filter_by(action_id=dict_entry['id']).first()
            if action_in_db:
                action_in_db.action_type = dict_entry['action_type']
                action_in_db.title = dict_entry['title']
                action_in_db.description = dict_entry['description']
                action_in_db.date_start = dict_entry['date_start']
                action_in_db.date_end = dict_entry['date_end']
                action_in_db.with_targeting = dict_entry['with_targeting']
                action_in_db.discount_type = dict_entry['discount_type']
                action_in_db.discount_value = dict_entry['discount_value']
                action_in_db.order_amount = dict_entry['order_amount']
                action_in_db.is_voucher_action = dict_entry['is_voucher_action']
            else:
                db_session.add(Actions(
                    action_id=dict_entry['id'],
                    action_type=dict_entry['action_type'],
                    title=dict_entry['title'],
                    description=dict_entry['description'],
                    date_start=dict_entry['date_start'],
                    date_end=dict_entry['date_end'],
                    with_targeting=dict_entry['with_targeting'],
                    discount_type=dict_entry['discount_type'],
                    discount_value=dict_entry['discount_value'],
                    order_amount=dict_entry['order_amount'],
                    is_voucher_action=dict_entry['is_voucher_action']
                ))
            
            supp_action_in_db = db_session.query(SupplierActions).filter_by(action_id=dict_entry['id'], supplier_id=int(session.supplier.id)).first()
            if supp_action_in_db:
                supp_action_in_db.freeze_date = dict_entry['freeze_date'] if dict_entry['freeze_date'] != '' else None
                supp_action_in_db.potential_products_count = dict_entry['potential_products_count']
                supp_action_in_db.participating_products_count = dict_entry['participating_products_count']
                supp_action_in_db.is_participating = dict_entry['is_participating']
                supp_action_in_db.banned_products_count = dict_entry['banned_products_count']
            else:
                db_session.add(SupplierActions(
                    action_id=dict_entry['id'],
                    freeze_date=(dict_entry['freeze_date'] if dict_entry['freeze_date'] != '' else None),
                    potential_products_count=dict_entry['potential_products_count'],
                    participating_products_count=dict_entry['participating_products_count'],
                    is_participating=dict_entry['is_participating'],
                    banned_products_count=dict_entry['banned_products_count'],
                    supplier_id=int(session.supplier.id)
                ))

            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()

        with self.make_request(session=session) as response:
            for action_entry in response.json ()['result']:
                process_entries(action_entry)


class PostActionsCandidates(MPmethod):
    def __init__(
        self,
        action_id : int = None,
        limit : int = 1000,
        offset : int = 0
    ) -> None:

        MPmethod.__init__(self, "POST", "/v1/actions/candidates")
        self.payload : dict = {
            "action_id" : action_id,
            "limit" : limit,
            "offset" : offset
        }
    
    def make_request(self, session : MPsesh, action_id : int = None) -> Response:
        if action_id:
            self.actions_list = [action_id]
        else:
            stmt = (
                            select(SupplierActions)
                                .where(SupplierActions.supplier_id == session.supplier.id)
                                .join(Actions, SupplierActions.action_id == Actions.action_id)
                                .where(Actions.date_end >= datetime.today())
                        )
            self.actions_list = [action_entry.action_id for action_entry in db_session.execute(stmt).scalars().all()]

        payload = lambda action_id, limit = 1000, offset = 0 : {
            "action_id" : action_id,  
            "limit" : limit,
            "offset" : offset
        }

        for action_ in self.actions_list:
            with session.post(self.url, json=payload(action_)) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)                       # TODO : // think about addind validators right after getting the response from the server
                    yield (action_, response)
                elif response.status_code == 404 and response.json()['message'] == 'Resource not found':
                    pass
                else:
                    print(f"Couldn\'t make it for this action - {action_}, status code -> {response.status_code} \n \
                        with content -> {response.content}")

    def validate_response(self, response : Response):
        try:
            schemas.PostActionsCandidates(**response.json()['result'])
        except ValidationError as e:
            print('Validation failed ->', e.json())
        
    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched date on an action's candidates for a given supplier"""

        for action_id_, action_entry in self.make_request(session=session):
            if action_entry.json()['result']['total']:
                for prod_in_action_entry in action_entry.json()['result']['products']:
                    candidate_in_db = (db_session.query(ActionCandidates)
                            .filter_by(action_id=action_id_, product_id=prod_in_action_entry['id'])
                            .first()
                    )
                    if candidate_in_db:
                        candidate_in_db.price = prod_in_action_entry['price']
                        candidate_in_db.action_price = prod_in_action_entry['action_price']
                        candidate_in_db.max_action_price = prod_in_action_entry['max_action_price']
                        candidate_in_db.add_mode = prod_in_action_entry['add_mode']
                        candidate_in_db.stock = prod_in_action_entry['stock']
                        candidate_in_db.min_stock = prod_in_action_entry['min_stock']
                    else:
                        if (db_session.query(Product).filter_by(product_id=prod_in_action_entry['id']).first() 
                                        and
                                    db_session.query(Actions).filter_by(action_id=action_id_).first()):
                            db_session.add(ActionCandidates(
                                action_id=action_id_,
                                product_id=prod_in_action_entry['id'],
                                price=prod_in_action_entry['price'],
                                action_price=prod_in_action_entry['action_price'],
                                max_action_price=prod_in_action_entry['max_action_price'],
                                add_mode=prod_in_action_entry['add_mode'],
                                stock=prod_in_action_entry['stock'],
                                min_stock=prod_in_action_entry['min_stock']
                            ))
                        else:
                            print('this product : {} or action : {} is not in the DB '.format(
                                prod_in_action_entry['id'], action_id_
                            ))
        db_session.commit()
        print(bcolors.OKCYAN + f'Successfully transitioned to the db for {session.supplier.name}' + bcolors.ENDC)


class PostActionsProducts(MPmethod):
    """ #TODO : think how we can remake this one with ActionsCandidates, as they have the same structure, and supposedly just are switching their state on and off
        on OZON servers. 
    """
    def __init__(
        self,
        action_id : int = None,
        limit : int = 1000,
        offset : int = 0
    ) -> None:

        MPmethod.__init__(self, "POST", "/v1/actions/products")
        self.payload : dict = {
            "action_id" : action_id,
            "limit" : limit,
            "offset" : offset
        }
    
    def make_request(self, session : MPsesh, action_id : int = None) -> Response:
        if action_id:
            self.actions_list = [action_id]
        else:
            stmt = (
                            select(SupplierActions)
                                .where(SupplierActions.supplier_id == session.supplier.id)
                                .join(Actions, SupplierActions.action_id == Actions.action_id)
                                .where(Actions.date_end >= datetime.today())
                        )
            self.actions_list = [action_entry.action_id for action_entry in db_session.execute(stmt).scalars().all()]

        payload = lambda action_id, limit = 1000, offset = 0 : {
            "action_id" : action_id,  
            "limit" : limit,
            "offset" : offset
        }

        for action_ in self.actions_list:
            with session.post(self.url, json=payload(action_)) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)                       # TODO : // think about addind validators right after getting the response from the server
                    yield (action_, response)
                elif response.status_code == 404 and response.json()['message'] == 'Resource not found':
                    pass
                else:
                    print(f"Couldn\'t make it for this action - {action_}, status code -> {response.status_code} \n \
                        with content -> {response.content}")

    def validate_response(self, response : Response):
        """ Yes, we use the actioncandidates' validator for this one"""
        try:
            schemas.PostActionsCandidates(**response.json()['result'])
        except ValidationError as e:
            print('Validation failed ->', e.json())
        
    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched date on an action's candidates for a given supplier"""

        for action_id_, action_entry in self.make_request(session=session):
            if action_entry.json()['result']['total']:
                for prod_in_action_entry in action_entry.json()['result']['products']:
                    candidate_in_db = (db_session.query(ActionProducts)
                            .filter_by(action_id=action_id_, product_id=prod_in_action_entry['id'])
                            .first()
                    )
                    if candidate_in_db:
                        candidate_in_db.price = prod_in_action_entry['price']
                        candidate_in_db.action_price = prod_in_action_entry['action_price']
                        candidate_in_db.max_action_price = prod_in_action_entry['max_action_price']
                        candidate_in_db.add_mode = prod_in_action_entry['add_mode']
                        candidate_in_db.stock = prod_in_action_entry['stock']
                        candidate_in_db.min_stock = prod_in_action_entry['min_stock']
                    else:
                        if (db_session.query(Product).filter_by(product_id=prod_in_action_entry['id']).first() 
                                        and
                                    db_session.query(Actions).filter_by(action_id=action_id_).first()):
                            db_session.add(ActionProducts(
                                action_id=action_id_,
                                product_id=prod_in_action_entry['id'],
                                price=prod_in_action_entry['price'],
                                action_price=prod_in_action_entry['action_price'],
                                max_action_price=prod_in_action_entry['max_action_price'],
                                add_mode=prod_in_action_entry['add_mode'],
                                stock=prod_in_action_entry['stock'],
                                min_stock=prod_in_action_entry['min_stock']
                            ))
                        else:
                            print('this product : {} or action : {} is not in the DB '.format(
                                prod_in_action_entry['id'], action_id_
                            ))
        db_session.commit()
        print(bcolors.OKCYAN + f'Successfully transitioned action products to the db for {session.supplier.name}' + bcolors.ENDC)


class PostWarehouseList(MPmethod):
    """ #fill this
    """
    def __init__(self) -> None:

        MPmethod.__init__(self, "POST", "/v1/warehouse/list")
        self.payload : dict = {}
    
    def make_request(self, session : MPsesh) -> Response:
        
        with session.post(self.url) as response:
            if response.status_code == 200:
                self.validate_response(response=response)                       # TODO : // think about addind validators right after getting the response from the server
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")

    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.PostWarehouseList(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())
        
    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched warehouses list for a given supplier"""
        def process_general(dict_entry : dict) -> None:
            """Processing each entry generally"""
            warehouse_in_db = db_session.query(Warehouses).filter_by(warehouse_id=dict_entry['warehouse_id']).first()
            if warehouse_in_db:
                warehouse_in_db.name = dict_entry['name']
                warehouse_in_db.is_rfbs = dict_entry['is_rfbs']
                warehouse_in_db.is_able_to_set_price = dict_entry['is_able_to_set_price']
                warehouse_in_db.has_entrusted_acceptance = dict_entry['has_entrusted_acceptance']
                warehouse_in_db.can_print_act_in_advance = dict_entry['can_print_act_in_advance']
                warehouse_in_db.has_postings_limit = dict_entry['has_postings_limit']
                warehouse_in_db.is_karantin = dict_entry['is_karantin']
                warehouse_in_db.is_kgt = dict_entry['is_kgt']
                warehouse_in_db.is_timetable_editable = dict_entry['is_timetable_editable']
                warehouse_in_db.min_postings_limit = dict_entry['min_postings_limit']
                warehouse_in_db.postings_limit = dict_entry['postings_limit']
                warehouse_in_db.min_working_days = dict_entry['min_working_days']
                warehouse_in_db.supplier_id = int(session.supplier.id)
            else:
                db_session.add(Warehouses(
                    warehouse_id=dict_entry['warehouse_id'],
                    name = dict_entry['name'],
                    is_rfbs = dict_entry['is_rfbs'],
                    is_able_to_set_price = dict_entry['is_able_to_set_price'],
                    has_entrusted_acceptance = dict_entry['has_entrusted_acceptance'],
                    can_print_act_in_advance = dict_entry['can_print_act_in_advance'],
                    has_postings_limit = dict_entry['has_postings_limit'],
                    is_karantin = dict_entry['is_karantin'],
                    is_kgt = dict_entry['is_kgt'],
                    is_timetable_editable = dict_entry['is_timetable_editable'],
                    min_postings_limit = dict_entry['min_postings_limit'],
                    postings_limit = dict_entry['postings_limit'],
                    min_working_days = dict_entry['min_working_days'],
                    supplier_id = int(session.supplier.id)
                ))
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()

        def process_first_mile_types(dict_entry : dict) -> None:
            """Processes first mile types"""
            entry_ : dict = dict_entry['first_mile_type']
            if not isinstance(dict_entry['first_mile_type'], dict):
                print(bcolors.FAIL + f"This warehouse {dict_entry['warehouse_id']} has more than one first mile type, take a look" + bcolors.ENDC)
                return False
            if (not entry_['dropoff_point_id']) and (not entry_['first_mile_type']):
                return False
            wrhsfrstmltype_in_db = db_session.query(WarehouseFirstMileTypes).filter_by(warehouse_id=dict_entry['warehouse_id']).first()
            if wrhsfrstmltype_in_db:
                wrhsfrstmltype_in_db.dropoff_point_id = entry_['dropoff_point_id']
                wrhsfrstmltype_in_db.dropoff_timeslot_id = entry_['dropoff_timeslot_id']
                wrhsfrstmltype_in_db.first_mile_is_changing = entry_['first_mile_is_changing']
                wrhsfrstmltype_in_db.first_mile_type = entry_['first_mile_type']
                try:
                    db_session.commit()
                except exc.IntegrityError as e:
                    print('Committing failed -> ', e)
                    db_session.rollback()
                return True

            wrhsfrstmltype_model : WarehouseFirstMileTypes = WarehouseFirstMileTypes(
                warehouse_id=dict_entry['warehouse_id'],
                dropoff_point_id=entry_['dropoff_point_id'],
                dropoff_timeslot_id=entry_['dropoff_timeslot_id'],
                first_mile_is_changing=entry_['first_mile_is_changing'],
                first_mile_type=entry_['first_mile_type']
            )
            try:
                db_session.add(wrhsfrstmltype_model)
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()
            return True

        for warehouse_entry in self.make_request(session=session).json()['result']:
            process_general(dict_entry=warehouse_entry)
            if not process_first_mile_types(dict_entry=warehouse_entry):
                continue
            
        print(bcolors.OKCYAN + f'Successfully transitioned warehouses to the db for {session.supplier.name}'  + bcolors.ENDC)


class PostDeliveryMethodList(MPmethod):
    """ #fill this
    """
    def __init__(self, filter : dict = {}, limit : int = 50, offset : int = 0) -> None:
        MPmethod.__init__(self, "POST", "/v1/delivery-method/list")
        self.payload : dict = {
            "filter" : filter,
            "limit" : limit,
            "offset" : offset
        }
    
    def make_request(self, session : MPsesh) -> Response:
        
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)                  # TODO : // think about addind validators right after getting the response from the server
                if response.json()['has_next']:
                    print(f'Check delivery methods endpoint, it has next page, but the logic is not continued, please return for \
                           {session.supplier.name}')
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")

    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.PostDeliveryMethodList(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())
        
    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched delivery methods list for a given supplier"""
        for delivery_method_entry in self.make_request(session=session).json()['result']:
            if delivery_method_entry.get('warehouse_id') == 0:
                delivery_method_entry['warehouse_id'] = None

            delivery_method_in_db = db_session.query(WarehouseDeliveryMethods).filter_by(delivery_method_id=delivery_method_entry['id']).first()
            if delivery_method_in_db:
                delivery_method_in_db.company_id = delivery_method_entry['company_id']
                delivery_method_in_db.name = delivery_method_entry['name']
                delivery_method_in_db.status = delivery_method_entry['status']
                delivery_method_in_db.cutoff = delivery_method_entry['cutoff']
                delivery_method_in_db.provider_id = delivery_method_entry['provider_id']
                delivery_method_in_db.template_id = delivery_method_entry['template_id']
                delivery_method_in_db.warehouse_id = delivery_method_entry['warehouse_id']
                delivery_method_in_db.created_at = delivery_method_entry['created_at']
                delivery_method_in_db.updated_at = delivery_method_entry['updated_at']
            else:
                db_session.add(WarehouseDeliveryMethods(
                    delivery_method_id=delivery_method_entry['id'],
                    company_id=delivery_method_entry['company_id'],
                    name=delivery_method_entry['name'],
                    status=delivery_method_entry['status'],
                    cutoff=delivery_method_entry['cutoff'],
                    provider_id=delivery_method_entry['provider_id'],
                    template_id=delivery_method_entry['template_id'],
                    warehouse_id=delivery_method_entry['warehouse_id'],
                    created_at=delivery_method_entry['created_at'],
                    updated_at=delivery_method_entry['updated_at']
                ))
        
        db_session.commit()
        print(bcolors.OKCYAN + f'Successfully transitioned delivery methods to the db for {session.supplier.name}' + bcolors.ENDC)


class PostSupplyOrderList(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        page : int = 1,
        page_size : int = 100,
        states : list[str] | None = None
    ) -> None:

        MPmethod.__init__(self, "POST", "/v1/supply-order/list")
        self.payload : dict = {
            "page": page,
            "page_size": page_size,
            "states": states
        }
    
    def make_request(self, session : MPsesh, no_attention_flag: bool = False, **kwargs) -> Response:
        """no_attention_flag is required for checking unprocessed postings (those with post changed numbers)
        if it is set to `true` then it doesn't show 404 not found error message for info purposes"""
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)                  # TODO : // think about addind validators right after getting the response from the server
                return response
            else:
                if no_attention_flag and response.status_code == 404:
                    return None
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")

    def get_chunks(self, session : MPsesh) -> Generator[Response, None, None]:
        """This one gets responses as a generator if the limit passes 1000"""
        i : int = 1
        has_next: bool = True

        while has_next:
            self.payload['page'] = i
            with session.post(self.url, json=self.payload) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    has_next = response.json()['has_next']
                    i += 1
                    yield response
                else:
                    has_next = 0
                    print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}")


    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.PostSupplyOrderListResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())
        
    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched delivery methods list for a given supplier"""
        for chunk_ in self.get_chunks(session=session):
            for supply_order in chunk_.json()['supply_orders']:
                supply_order_in_db = db_session.query(SupplyOrders).filter(
                                    SupplyOrders.supply_order_id == supply_order['supply_order_id'],
                                    SupplyOrders.supply_order_number == supply_order['supply_order_number'],
                                ).first()
                if supply_order_in_db:
                    supply_order_in_db.state = supply_order['state']
                    if supply_order['local_timeslot']:
                        supply_order_in_db.local_timeslot=supply_order['local_timeslot']['from']
                    if supply_order['supply_warehouse']:
                        supply_order_in_db.supply_warehouse_id=supply_order['supply_warehouse']['warehouse_id']
                        supply_order_in_db.supply_warehouse_name=supply_order['supply_warehouse']['name']
                    try:
                        db_session.commit()
                    except exc.IntegrityError as e:
                        print('Committing failed -> ', e)
                        db_session.rollback()
                    continue
                else:
                    supply_order_model: SupplyOrders = SupplyOrders(
                                                            supply_order_id=supply_order['supply_order_id'],
                                                            supply_order_number=supply_order['supply_order_number'],
                                                            supplier_id=session.supplier.id,
                                                            state=supply_order['state'],
                                                            created_at=supply_order['created_at']
                                                        )
                    if supply_order['local_timeslot']:
                        supply_order_model.local_timeslot=supply_order['local_timeslot']['from']
                    if supply_order['supply_warehouse']:
                        supply_order_model.supply_warehouse_id=supply_order['supply_warehouse']['warehouse_id']
                        supply_order_model.supply_warehouse_name=supply_order['supply_warehouse']['name']
                    
                    try:
                        db_session.add(supply_order_model)
                        db_session.commit()
                    except exc.IntegrityError as e:
                        print('Committing failed -> ', e)
                        db_session.rollback()


class PostSupplyOrderItems(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        supply_order_id : int,
        page : int = 1,
        page_size : int = 100
    ) -> None:

        MPmethod.__init__(self, "POST", "/v1/supply-order/items")
        self.payload : dict = {
            "page": page,
            "page_size": page_size,
            "supply_order_id": supply_order_id
        }
    
    def make_request(self, session : MPsesh, no_attention_flag: bool = False, **kwargs) -> Response:
        """no_attention_flag is required for checking unprocessed postings (those with post changed numbers)
        if it is set to `true` then it doesn't show 404 not found error message for info purposes"""
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)                  # TODO : // think about addind validators right after getting the response from the server
                return response
            else:
                if no_attention_flag and response.status_code == 404:
                    return None
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")

    def get_chunks(self, supply_order_id: int, session: MPsesh) -> Generator[Response, None, None]:
        """This one gets responses as a generator if the limit passes 1000"""
        i : int = 1
        has_next: bool = True
        self.payload['supply_order_id'] = supply_order_id

        while has_next:
            self.payload['page'] = i
            with session.post(self.url, json=self.payload) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    has_next = response.json()['has_next']
                    i += 1
                    yield response
                else:
                    has_next = 0
                    print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}")


    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.PostSupplyOrderItemsResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())
        
    def process_to_db(self, supply_order_id: int, session: MPsesh) -> None:
        """Processing fetched delivery methods list for a given supplier"""
        for chunk_ in self.get_chunks(supply_order_id=supply_order_id, session=session):
            for item in chunk_.json()['items']:
                item_in_db = db_session.query(SupplyOrderItems).filter(
                                    SupplyOrderItems.supply_order_id == supply_order_id,
                                    SupplyOrderItems.sku == int(item['sku'])).first()
                if item_in_db:
                    assert item_in_db.quantity == int(item['quantity']), f'Quantities are not the same for this one - > {supply_order_id} - {item["offer_id"]}'
                    continue
                else:
                    item_model = SupplyOrderItems(
                        supply_order_id=supply_order_id,
                        sku=item['sku'],
                        offer_id=item['offer_id'],
                        quantity=item['quantity']
                    )
                    try:
                        db_session.add(item_model)
                        db_session.commit()
                    except exc.IntegrityError as e:
                        print('Committing failed -> ', e)
                        db_session.rollback()
                



class PostPostingFboGet(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        posting_number : str = None,
        analytics_data : bool = True,
        financial_data : bool = True
    ) -> None:

        MPmethod.__init__(self, "POST", "/v2/posting/fbo/get")
        self.payload : dict = {
            "posting_number" : posting_number,
            "with" : {
                "analytics_data" : analytics_data,
                "financial_data" : financial_data
            }
        }
    
    def make_request(self, session : MPsesh, no_attention_flag: bool = False, **kwargs) -> Response:
        """no_attention_flag is required for checking unprocessed postings (those with post changed numbers)
        if it is set to `true` then it doesn't show 404 not found error message for info purposes"""
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)                  # TODO : // think about addind validators right after getting the response from the server
                return response
            else:
                if no_attention_flag and response.status_code == 404:
                    return None
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")

    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.v2FboPosting(**response.json()['result'])
        except ValidationError as e:
            print('Validation failed ->', e.json())
        
    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched delivery methods list for a given supplier"""
        ...
        

class PostPostingFboList(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        dir : str = None,
        date_since : date = None,
        date_to : date = None,
        status : str = None,
        limit : int = 1000,
        offset : int = 0,
        translit : bool = False,
        analytics_data : bool = True,
        financial_data : bool = True
    ) -> None:

        MPmethod.__init__(self, "POST", "/v2/posting/fbo/list")
        if not (date_since and date_to):
            since = (date.today() - timedelta(3)).strftime('%Y-%m-%dT21:00:00.00Z')
            to = (date.today()).strftime('%Y-%m-%dT20:59:59Z')
        else:
            since = (date_since - timedelta(1)).strftime('%Y-%m-%dT21:00:00.00Z')
            to = (date_to).strftime('%Y-%m-%dT20:59:59Z')


        self.payload : dict = {
            "dir" : dir,
            "filter" : {
                "since" : since,
                "status" : status,
                "to" : to
            },
            "limit" : limit,
            "offset" : offset,
            "translit" : translit,
            "with" : {
                "analytics_data" : analytics_data,
                "financial_data" : financial_data
            }
        }

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)                  # TODO : // think about addind validators right after getting the response from the server
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")

    def get_chunks(self, session : MPsesh) -> Generator[Response, None, None]:
        """This one gets responses as a generator if the limit passes 1000"""
        with self.make_request(session=session) as response:
            i = 0
            while not ((len(response.json()['result']) < 1000) and (i != 0)):
                with self.make_request(session=session, **{"offset" : (i * 1000)}) as response:
                    i += 1
                    yield response
                    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.PostPostingFboList(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())
        
    def process_to_db(self, session : MPsesh, single_posting_number : str = False, no_attention_flag: bool = False) -> None:
        """Processing fetched delivery methods list for a given supplier"""
        
        def process_general(dict_entry : dict):
            """Func to parse general info into db from an entry in postings list"""
            fbo_posting_in_db = db_session.query(FBOPostings).filter_by(posting_number=dict_entry['posting_number']).first()
            if fbo_posting_in_db:
                if (fbo_posting_in_db.order_number != dict_entry['order_number']) or (fbo_posting_in_db.posting_number != dict_entry['posting_number']):
                    print(bcolors.WARNING + f'Check this order {fbo_posting_in_db.posting_number}, posting numbers dont match!' + bcolors.ENDC)
                fbo_posting_in_db.status = dict_entry['status']
                fbo_posting_in_db.cancel_reason_id = dict_entry['cancel_reason_id']
            else:
                db_session.add(FBOPostings(
                    order_id=dict_entry['order_id'],
                    order_number=dict_entry['order_number'],
                    posting_number=dict_entry['posting_number'],
                    status=dict_entry['status'],
                    cancel_reason_id=dict_entry['cancel_reason_id'],
                    created_at=dict_entry['created_at'],
                    in_process_at=dict_entry['in_process_at'],
                    supplier_id=int(session.supplier.id)
                )
            )
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()

        def process_analytics_data(dict_entry : dict):
            """Func to parse analytics data info into db from an entry in postings list"""
            fbo_posting_analytics_in_db = db_session.query(FBOPostingsAnalyticsData).filter_by(posting_number=dict_entry['posting_number']).first()
            if fbo_posting_analytics_in_db:
                if (fbo_posting_analytics_in_db.order_number != dict_entry['order_number']) or (fbo_posting_analytics_in_db.posting_number != dict_entry['posting_number']):
                    print(bcolors.WARNING + f'Check this order {fbo_posting_analytics_in_db.posting_number}, posting numbers dont match for analytics data!' + bcolors.ENDC)
                fbo_posting_analytics_in_db.region = dict_entry['analytics_data']['region']
                fbo_posting_analytics_in_db.city = dict_entry['analytics_data']['city']
                fbo_posting_analytics_in_db.delivery_type = dict_entry['analytics_data']['delivery_type']
                fbo_posting_analytics_in_db.payment_type_group_name = dict_entry['analytics_data']['payment_type_group_name']
                fbo_posting_analytics_in_db.warehouse_id = dict_entry['analytics_data']['warehouse_id']
                fbo_posting_analytics_in_db.warehouse_name = dict_entry['analytics_data']['warehouse_name']
            else:
                db_session.add(FBOPostingsAnalyticsData(
                    order_number=dict_entry['order_number'],
                    posting_number=dict_entry['posting_number'],
                    region = dict_entry['analytics_data']['region'],
                    city = dict_entry['analytics_data']['city'],
                    delivery_type = dict_entry['analytics_data']['delivery_type'],
                    is_premium=dict_entry['analytics_data']['is_premium'],
                    is_legal=dict_entry['analytics_data']['is_legal'],
                    payment_type_group_name=dict_entry['analytics_data']['payment_type_group_name'],
                    warehouse_id=dict_entry['analytics_data']['warehouse_id'],
                    warehouse_name=dict_entry['analytics_data']['warehouse_name'],
                )
            )
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()
        
        def process_products(dict_entry : dict, session : MPsesh):
            """Func to parse products info into db from an entry in postings list"""
            def check_product_integrity(posting_number : str, fbo_dict_entry : dict) -> bool:
                """Checks for the integrity of the products in DB and from API"""
                posting_positions_query = (db_session
                            .query(FBOPostingsProducts)
                            .filter_by(posting_number=posting_number))
                
                if posting_positions_query:
                    positions_in_db = [(position.sku, position.price, position.quantity) 
                                        for position in posting_positions_query.all()]
                    positions = [(product['sku'], int(float(product['price'])), product['quantity']) 
                                        for product in fbo_dict_entry['products']]
                    if set(positions) != set(positions_in_db):
                        difference_set_not_in_db = (set(positions) - set(positions_in_db))
                        difference_set_in_db = (set(positions_in_db) - set(positions))
                        if difference_set_not_in_db:
                            (print(
                                bcolors.FAIL + f"This combination of a product is not in the DB, just look at this posting {posting_number} \
                                product ( sku, price, quantity ) == {difference_set_not_in_db}"
                            ))
                        if difference_set_in_db:
                            (print(
                                bcolors.FAIL + f"This combination of a product is in the DB but not API, just look at this posting {posting_number} \
                                product ( sku, price, quantity ) == {difference_set_in_db}"
                                
                            ))
                            for diff_product_in_posting in list(difference_set_in_db):
                                try:
                                    for entity in (FBOPostingsProductsFinDataActions, FBOPostingsProductsFinDataItemServices,
                                        FBOPostingsProductsFinData, FBOReturns, FBOPostingsProducts):
                                        (
                                        db_session
                                            .query(entity)
                                            .filter_by(posting_number=posting_number, sku=diff_product_in_posting[0])
                                            .delete()
                                        )
                                        db_session.commit()
                                    (
                                        db_session
                                            .query(FBOPostings)
                                            .filter_by(posting_number=posting_number)
                                            .delete()
                                    )
                                    db_session.commit()
                                    return -1
                                except exc.IntegrityError as e:
                                    print('Committing failed while deleting a position not present in APIs from the DB -> ', e)
                                    db_session.rollback()

            for fbo_postin_product in dict_entry['products']:
                if not fbo_postin_product['offer_id']:
                    fbo_postin_get = PostPostingFboGet(posting_number=dict_entry['posting_number']).make_request(session=session)
                    try:
                        fbo_postin_get = fbo_postin_get.json()['result']['products']
                    except AttributeError as e:
                        print(bcolors.WARNING + f"Couldn't get FBO posting's products as json, here is the number - {dict_entry['posting_number']}" + bcolors.ENDC)
                    fbo_postin_get = [entry for entry in fbo_postin_get                         #TODO: maybe add a function to check skus
                        if (entry['sku'] == fbo_postin_product['sku']) 
                            and ((entry['price'] == fbo_postin_product['price'])
                            and (entry['quantity'] == fbo_postin_product['quantity']))]
                    if len(fbo_postin_get) != 1:
                        print(bcolors.WARNING + f"Some duplicates in this posting {dict_entry['posting_number']}" + bcolors.ENDC)
                    fbo_postin_product = fbo_postin_get[0]
                fbo_postin_product_in_db = (db_session
                            .query(FBOPostingsProducts)
                            .filter_by(posting_number=dict_entry['posting_number'], sku=fbo_postin_product['sku'])              # here was fbo_posting instead of dict_entry
                            .first())
                if fbo_postin_product_in_db:
                    if check_product_integrity(dict_entry['posting_number'], dict_entry) == -1:
                        return -1
                    if ((fbo_postin_product_in_db.quantity != fbo_postin_product['quantity'])
                        or (fbo_postin_product_in_db.price != int(float(fbo_postin_product['price'])))):
                        print(bcolors.WARNING + f'Check this posting {fbo_postin_product_in_db.posting_number}, qty or price\
                             for {fbo_postin_product_in_db.sku} doesn\'t match!' + bcolors.ENDC)
                        fbo_postin_product_in_db.quantity = fbo_postin_product['quantity']
                        fbo_postin_product_in_db.price = int(float(fbo_postin_product['price']))
                    fbo_postin_product_in_db.name = fbo_postin_product['name']
                    fbo_postin_product_in_db.offer_id = fbo_postin_product['offer_id']
                else:
                    if db_session.query(ProductSource).filter_by(sku=fbo_postin_product['sku']).first():
                        db_session.add(FBOPostingsProducts(
                            sku=fbo_postin_product['sku'],
                            name=fbo_postin_product['name'],
                            quantity=fbo_postin_product['quantity'],
                            offer_id=fbo_postin_product['offer_id'],
                            price=int(float(fbo_postin_product['price'])),
                            posting_number=dict_entry['posting_number']
                        ))
                    else:
                        prod_in_db = db_session.query(Product).filter_by(offer_id=fbo_postin_product['offer_id'], supplier_id=session.supplier.id)
                        if prod_in_db.count() != 1:
                            print(f"This product has duplicates : count - {prod_in_db.count()} \
                                - {fbo_postin_product['offer_id']} \n here it is {prod_in_db.first().product_id}")
                        db_session.add(ProductSource(
                            sku=fbo_postin_product['sku'],
                            product_id=prod_in_db.first().product_id,
                            is_enabled=True,
                            source='fbo_undefined'))
                        db_session.commit()
                        db_session.add(FBOPostingsProducts(
                            sku=fbo_postin_product['sku'],
                            name=fbo_postin_product['name'],
                            quantity=fbo_postin_product['quantity'],
                            offer_id=fbo_postin_product['offer_id'],
                            price=int(float(fbo_postin_product['price'])),
                            posting_number=dict_entry['posting_number']                                 # FIXME : may be a bug as well!
                        ))
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()
        
        def process_products_fin_data(dict_entry : dict):
            """This one processes products financial data (prices and etc) and also actions and costs of a
                given product in a posting"""
            if not dict_entry['financial_data']:
                print(bcolors.WARNING + f"No financial data for posting - {dict_entry['posting_number']}" + bcolors.ENDC)
                return False
            for fbo_postin_findata in dict_entry['financial_data']['products']:
                fbo_postin_findata_in_db = (db_session
                        .query(FBOPostingsProductsFinData)
                        .filter_by(sku=fbo_postin_findata['product_id'], posting_number=dict_entry['posting_number'])
                        .first())
                if fbo_postin_findata_in_db:
                    fbo_postin_findata_in_db.commission_amount=fbo_postin_findata['commission_amount']
                    fbo_postin_findata_in_db.commission_percent=fbo_postin_findata['commission_percent']
                    fbo_postin_findata_in_db.payout=fbo_postin_findata['payout']
                    fbo_postin_findata_in_db.old_price=fbo_postin_findata['old_price']
                    fbo_postin_findata_in_db.price=fbo_postin_findata['price']
                    fbo_postin_findata_in_db.total_discount_value=fbo_postin_findata['total_discount_value']
                    fbo_postin_findata_in_db.total_discount_percent=fbo_postin_findata['total_discount_percent']
                    fbo_postin_findata_in_db.quantity=fbo_postin_findata['quantity']
                    fbo_postin_findata_in_db.client_price=(int(fbo_postin_findata['client_price']) if fbo_postin_findata['client_price'] else None)
                    
                    # first we check if all the actions are saved for a given product
                    fbo_postin_findata_actions_in_db = (db_session
                            .query(FBOPostingsProductsFinDataActions)
                            .filter_by(sku=fbo_postin_findata['product_id'], posting_number=dict_entry['posting_number'])
                            .all())
                    if fbo_postin_findata_actions_in_db:
                        actions_in_db = [action.sold_on_action for action in fbo_postin_findata_actions_in_db]
                        try:
                            assert set(fbo_postin_findata['actions']) == set(actions_in_db)
                        except AssertionError:
                            pass
                            # print(bcolors.WARNING + f"Actions fetched from API and in the DB are not the same for this combination \
                            #     \n sku - {fbo_postin_findata['product_id']} ; posting number - {dict_entry['posting_number']}" + bcolors.ENDC)
                    else:
                        for fbo_postin_findata_action in fbo_postin_findata['actions']:
                            db_session.add(FBOPostingsProductsFinDataActions(
                                sku=fbo_postin_findata['product_id'],
                                posting_number=dict_entry['posting_number'],
                                sold_on_action=fbo_postin_findata_action
                            ))
                    
                    # then we check if there are any item services already in the DB
                    fbo_postin_findata_item_services_in_db = (db_session
                            .query(FBOPostingsProductsFinDataItemServices)
                            .filter_by(sku=fbo_postin_findata['product_id'], posting_number=dict_entry['posting_number'])
                            .first())
                    if fbo_postin_findata_item_services_in_db:
                        fbo_postin_findata_item_services_in_db.marketplace_service_item_fulfillment = fbo_postin_findata['item_services']['marketplace_service_item_fulfillment']
                        fbo_postin_findata_item_services_in_db.marketplace_service_item_pickup = fbo_postin_findata['item_services']['marketplace_service_item_pickup']
                        fbo_postin_findata_item_services_in_db.marketplace_service_item_dropoff_pvz = fbo_postin_findata['item_services']['marketplace_service_item_dropoff_pvz']
                        fbo_postin_findata_item_services_in_db.marketplace_service_item_dropoff_sc = fbo_postin_findata['item_services']['marketplace_service_item_dropoff_sc']
                        fbo_postin_findata_item_services_in_db.marketplace_service_item_dropoff_ff = fbo_postin_findata['item_services']['marketplace_service_item_dropoff_ff']
                        fbo_postin_findata_item_services_in_db.marketplace_service_item_direct_flow_trans = fbo_postin_findata['item_services']['marketplace_service_item_direct_flow_trans']
                        fbo_postin_findata_item_services_in_db.marketplace_service_item_return_flow_trans = fbo_postin_findata['item_services']['marketplace_service_item_return_flow_trans']
                        fbo_postin_findata_item_services_in_db.marketplace_service_item_deliv_to_customer = fbo_postin_findata['item_services']['marketplace_service_item_deliv_to_customer']
                        fbo_postin_findata_item_services_in_db.marketplace_service_item_return_not_deliv_to_customer = fbo_postin_findata['item_services']['marketplace_service_item_return_not_deliv_to_customer']
                        fbo_postin_findata_item_services_in_db.marketplace_service_item_return_part_goods_customer = fbo_postin_findata['item_services']['marketplace_service_item_return_part_goods_customer']
                        fbo_postin_findata_item_services_in_db.marketplace_service_item_return_after_deliv_to_customer = fbo_postin_findata['item_services']['marketplace_service_item_return_after_deliv_to_customer']
                    else:
                        db_session.add(FBOPostingsProductsFinDataItemServices(
                                sku=fbo_postin_findata['product_id'],
                                posting_number=dict_entry['posting_number'],
                                **(fbo_postin_findata['item_services'])
                            ))
                else:
                    db_session.add(FBOPostingsProductsFinData(
                        sku=fbo_postin_findata['product_id'],
                        posting_number=dict_entry['posting_number'],
                        commission_amount=fbo_postin_findata['commission_amount'],
                        commission_percent=fbo_postin_findata['commission_percent'],
                        payout=fbo_postin_findata['payout'],
                        old_price=fbo_postin_findata['old_price'],
                        price=fbo_postin_findata['price'],
                        total_discount_value=fbo_postin_findata['total_discount_value'],
                        total_discount_percent=fbo_postin_findata['total_discount_percent'],
                        quantity=fbo_postin_findata['quantity'],
                        client_price=(int(fbo_postin_findata['client_price']) if fbo_postin_findata['client_price'] else None)
                    ))
                    if fbo_postin_findata['actions']:
                        for fbo_postin_findata_action in fbo_postin_findata['actions']:
                            db_session.add(FBOPostingsProductsFinDataActions(
                                sku=fbo_postin_findata['product_id'],
                                posting_number=dict_entry['posting_number'],
                                sold_on_action=fbo_postin_findata_action
                            ))
                    db_session.add(FBOPostingsProductsFinDataItemServices(
                        sku=fbo_postin_findata['product_id'],
                        posting_number=dict_entry['posting_number'],
                        **(fbo_postin_findata['item_services'])
                    ))
                    
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()

        def process_chunks(session: MPsesh) -> Optional[list[str]]:
            """processes chunks of fbo postings, not a single one"""
            unprocessed: list[str] = []

            for chunk in self.get_chunks(session=session):
                for fbo_posting_entry in chunk.json()['result']:
                    process_general(fbo_posting_entry)
                    process_analytics_data(fbo_posting_entry)
                    if process_products(fbo_posting_entry, session=session) == -1:
                        unprocessed.append(fbo_posting_entry['posting_number'])
                        continue
                    process_products_fin_data(fbo_posting_entry)
            return unprocessed

        def process_single(session: MPsesh, posting_number: str) -> None:
            """processes a single posting"""
            try:
                fbo_single_posting = PostPostingFboGet(posting_number=posting_number).make_request(session=session, no_attention_flag=no_attention_flag).json()['result']
                process_general(fbo_single_posting)
                process_analytics_data(fbo_single_posting)
                if process_products(fbo_single_posting, session=session) == -1:
                    print('didn\'t worked as expected')
                process_products_fin_data(fbo_single_posting)
            except AttributeError:
                print(bcolors.WARNING + f"This single posting {posting_number} hasn't been found" + bcolors.ENDC)


        if not single_posting_number:
            unprocessed: Optional[list[str]] = process_chunks(session=session)
            if unprocessed:
                for unprocessed_posting in unprocessed:
                    process_single(session=session, posting_number=unprocessed_posting)
            print(bcolors.OKBLUE + f"Successfully transitioned fbo postings to the db for {session.supplier.name}" + bcolors.ENDC)
        else:
            process_single(session=session, posting_number=single_posting_number)
            


class PostPostingFbsGet(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        posting_number : str,
        translit : bool = False,
        analytics_data : bool = True,
        financial_data : bool = True,
        related_postings: bool = True,
        barcodes : bool = False
    ) -> None:

        MPmethod.__init__(self, "POST", "/v3/posting/fbs/get")
        self.payload : dict = {
            "posting_number" : posting_number,
            "with" : {
                "analytics_data" : analytics_data,
                "financial_data" : financial_data,
                "related_postings": related_postings,
                "barcodes" : barcodes,
                "translit" : translit
            }
        }
    
    def make_request(self, session : MPsesh, no_attention_flag: bool = False) -> Response:
        """no_attention_flag is required for checking unprocessed postings (those with post changed numbers)
        if it is set to `true` then it doesn't show 404 not found error message for info purposes"""
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)                  # TODO : // think about addind validators right after getting the response from the server
                return response
            else:
                if no_attention_flag and response.status_code == 404:
                    return None
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")

    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.v3FbsPosting(**response.json()['result'])
        except ValidationError as e:
            print('Validation failed ->', e.json())


class PostPostingFbsList(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        dir : str = None,
        since : date = None,
        to : date = None,
        delivery_method_id : int = None,
        order_id : int = None,
        provider_id : int = None,
        warehouse_id : int = None,
        status : str = None,
        limit : int = 1000,
        offset : int = 0,
        translit : bool = False,
        analytics_data : bool = True,
        financial_data : bool = True,
        barcodes : bool = False
    ) -> None:

        MPmethod.__init__(self, "POST", "/v3/posting/fbs/list")
        if not (since and to):
            since_ = (date.today() - timedelta(3)).strftime('%Y-%m-%dT21:00:00.00Z')
            to_ = (date.today()).strftime('%Y-%m-%dT20:59:59Z')
        else:
            since_ = (since - timedelta(1)).strftime('%Y-%m-%dT21:00:00.00Z')
            to_ = (to).strftime('%Y-%m-%dT20:59:59Z')


        self.payload : dict = {
            "dir" : dir,
            "filter" : {
                "delivery_method_id" : delivery_method_id,
                "order_id" : order_id,
                "provider_id" : provider_id,
                "warehouse_id" : warehouse_id,
                "since" : since_,
                "status" : status,
                "to" : to_
            },
            "limit" : limit,
            "offset" : offset,
            "with" : {
                "analytics_data" : analytics_data,
                "financial_data" : financial_data,
                "barcodes" : barcodes,
                "translit" : translit
            }
        }
    
    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)                  # TODO : // think about addind validators right after getting the response from the server
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")

    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.PostPostingFbsList(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session : MPsesh) -> Generator[Response, None, None]:
        """This one gets responses as a generator if the limit passes 1000"""
        with self.make_request(session=session) as response:
            i = 0
            while not ((len(response.json()['result']['postings']) < 1000) and (i != 0)):
                with self.make_request(session=session, **{"offset" : (i * 1000)}) as response:
                    i += 1
                    yield response
        
    def process_to_db(self, session : MPsesh, single_posting_number : str = False, no_attention_flag: bool = False) -> None:
        """Processing fetched delivery methods list for a given supplier"""
        def process_general(dict_entry : dict):
            """Func to parse general info into db from an entry in postings list"""
            fbs_posting_in_db = db_session.query(FBSPostings).filter_by(posting_number=dict_entry['posting_number']).first()
            if fbs_posting_in_db:
                if (fbs_posting_in_db.order_number != dict_entry['order_number']) or (fbs_posting_in_db.posting_number != dict_entry['posting_number']):
                    print(bcolors.WARNING + f'Check this order {fbs_posting_in_db.posting_number}, posting numbers dont match!' + bcolors.ENDC)
                fbs_posting_in_db.status = dict_entry['status']
                fbs_posting_in_db.in_process_at = dict_entry['in_process_at']
                fbs_posting_in_db.shipment_date = dict_entry['shipment_date']
                fbs_posting_in_db.delivering_date = dict_entry['delivering_date']
                fbs_posting_in_db.barcodes = dict_entry['barcodes']
                fbs_posting_in_db.tracking_number = dict_entry['tracking_number']
                fbs_posting_in_db.tpl_integration_type = dict_entry['tpl_integration_type']
            else:
                db_session.add(FBSPostings(
                    order_id=dict_entry['order_id'],
                    order_number=dict_entry['order_number'],
                    posting_number=dict_entry['posting_number'],
                    status=dict_entry['status'],
                    in_process_at=dict_entry['in_process_at'],
                    shipment_date=dict_entry['shipment_date'],
                    delivering_date=dict_entry['delivering_date'],
                    barcodes=dict_entry['barcodes'],
                    tracking_number=dict_entry['tracking_number'],
                    tpl_integration_type=dict_entry['tpl_integration_type'],
                    is_express=dict_entry['is_express'],
                    supplier_id=int(session.supplier.id)
                )
            )
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()

        def process_delivery(dict_entry : dict):
            """Func to parse delivery methods from a posting"""
            fbs_posting_delivery_in_db = (db_session
                            .query(FBSPostingsDeliveryMethod)
                            .filter_by(posting_number=dict_entry['posting_number'])
                            .first())
            if fbs_posting_delivery_in_db:
                fbs_posting_delivery_in_db.delivery_method_id = dict_entry['delivery_method']['id']
                fbs_posting_delivery_in_db.delivery_method_name = dict_entry['delivery_method']['name']
                fbs_posting_delivery_in_db.warehouse_id = dict_entry['delivery_method']['warehouse_id']
                fbs_posting_delivery_in_db.warehouse_name = dict_entry['delivery_method']['warehouse']
                fbs_posting_delivery_in_db.tpl_provider_id = dict_entry['delivery_method']['tpl_provider_id']
                fbs_posting_delivery_in_db.tpl_provider = dict_entry['delivery_method']['tpl_provider']
            else:
                db_session.add(FBSPostingsDeliveryMethod(
                    posting_number=dict_entry['posting_number'],
                    delivery_method_id=dict_entry['delivery_method']['id'],
                    delivery_method_name=dict_entry['delivery_method']['name'],
                    warehouse_id=dict_entry['delivery_method']['warehouse_id'],
                    warehouse_name=dict_entry['delivery_method']['warehouse'],
                    tpl_provider_id=dict_entry['delivery_method']['tpl_provider_id'],
                    tpl_provider=dict_entry['delivery_method']['tpl_provider']
                ))
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()

        def process_analytics_data(dict_entry : dict):
            """Func to parse analytics data from a posting"""
            fbs_posting_analytics_data_in_db = (db_session
                            .query(FBSPostingsAnalyticsData)
                            .filter_by(posting_number=dict_entry['posting_number'])
                            .first())
            if dict_entry['analytics_data']:
                if fbs_posting_analytics_data_in_db:
                    fbs_posting_analytics_data_in_db.region = dict_entry['analytics_data']['region']
                    fbs_posting_analytics_data_in_db.city = dict_entry['analytics_data']['city']
                    fbs_posting_analytics_data_in_db.delivery_type = dict_entry['analytics_data']['delivery_type']
                    fbs_posting_analytics_data_in_db.is_premium = dict_entry['analytics_data']['is_premium']
                    fbs_posting_analytics_data_in_db.payment_type_group_name = dict_entry['analytics_data']['payment_type_group_name']
                    fbs_posting_analytics_data_in_db.delivery_date_begin = dict_entry['analytics_data']['delivery_date_begin']
                    fbs_posting_analytics_data_in_db.delivery_date_end = dict_entry['analytics_data']['delivery_date_end']
                    fbs_posting_analytics_data_in_db.is_legal = dict_entry['analytics_data']['is_legal']
                else:
                    db_session.add(FBSPostingsAnalyticsData(
                        posting_number=dict_entry['posting_number'],
                        region=dict_entry['analytics_data']['region'],
                        city=dict_entry['analytics_data']['city'],
                        delivery_type=dict_entry['analytics_data']['delivery_type'],
                        is_premium=dict_entry['analytics_data']['is_premium'],
                        payment_type_group_name=dict_entry['analytics_data']['payment_type_group_name'],
                        delivery_date_begin=dict_entry['analytics_data']['delivery_date_begin'],
                        delivery_date_end=dict_entry['analytics_data']['delivery_date_end'],
                        is_legal=dict_entry['analytics_data']['is_legal']
                    ))
            else:
                if not fbs_posting_analytics_data_in_db:
                    db_session.add(FBSPostingsAnalyticsData(
                            posting_number=dict_entry['posting_number'],
                            is_premium=False,
                            payment_type_group_name="undefined",
                            is_legal=False
                        ))
                print(bcolors.WARNING + f"For this posting {dict_entry['posting_number']} there is no analytics data" + bcolors.ENDC)

            try:
                    db_session.commit()
            except exc.IntegrityError as e:
                    print('Committing failed -> ', e)
                    db_session.rollback()
        
        def process_products(dict_entry : dict, session : MPsesh):
            """Func to parse products info into db from an entry in postings list"""
            def check_product_integrity(posting_number : str, fbs_dict_entry : dict) -> bool:
                """Checks for the integrity of the products in DB and from API"""
                posting_positions_query = (db_session
                            .query(FBSPostingsProducts)
                            .filter_by(posting_number=posting_number))
                
                if posting_positions_query:
                    positions_in_db = [(position.sku, position.price, position.quantity) 
                                        for position in posting_positions_query.all()]
                    positions = [(product['sku'], int(float(product['price'])), product['quantity']) 
                                        for product in fbs_dict_entry['products']]
                    if set(positions) != set(positions_in_db):
                        difference_set_not_in_db = (set(positions) - set(positions_in_db))
                        difference_set_in_db = (set(positions_in_db) - set(positions))
                        if difference_set_not_in_db:
                            (print(
                                bcolors.FAIL + f"This combination of a product is not in the DB, just look at this posting {posting_number} \
                                product ( sku, price, quantity ) == {difference_set_not_in_db}"
                                
                            ))
                        if difference_set_in_db:
                            (print(
                                bcolors.FAIL + f"This combination of a product is in the DB but not API, just look at this posting {posting_number} \
                                product ( sku, price, quantity ) == {difference_set_in_db}"
                                
                            ))

            
            for fbs_postin_product in dict_entry['products']:
                fbs_postin_product_in_db = (db_session
                            .query(FBSPostingsProducts)
                            .filter_by(posting_number=dict_entry['posting_number'], sku=fbs_postin_product['sku'])
                            .first())
                if fbs_postin_product_in_db:
                    check_product_integrity(dict_entry['posting_number'], dict_entry)
                    if ((fbs_postin_product_in_db.quantity != fbs_postin_product['quantity'])
                        or (fbs_postin_product_in_db.price != int(float(fbs_postin_product['price'])))):
                        print(bcolors.WARNING + f'Check this posting {fbs_postin_product_in_db.posting_number}, qty or price for {fbs_postin_product_in_db.sku} doesn\'t match! \
                            \n Serious issue' + bcolors.ENDC)
                        fbs_postin_product_in_db.quantity = fbs_postin_product['quantity']
                        fbs_postin_product_in_db.price = int(float(fbs_postin_product['price']))
                    fbs_postin_product_in_db.name = fbs_postin_product['name']
                    fbs_postin_product_in_db.offer_id = fbs_postin_product['offer_id']
                else:
                    if db_session.query(ProductSource).filter_by(sku=fbs_postin_product['sku']).first():
                        db_session.add(FBSPostingsProducts(
                            sku=fbs_postin_product['sku'],
                            name=fbs_postin_product['name'],
                            quantity=fbs_postin_product['quantity'],
                            offer_id=fbs_postin_product['offer_id'],
                            price=int(float(fbs_postin_product['price'])),
                            posting_number=dict_entry['posting_number']
                        ))
                    else:
                        prod_in_db = db_session.query(Product).filter_by(offer_id=fbs_postin_product['offer_id'], supplier_id=session.supplier.id)
                        if prod_in_db.count() != 1:
                            print(bcolors.WARNING + f"This product has duplicates : count - {prod_in_db.count()} \
                                - {fbs_postin_product['offer_id']} \n here it is {prod_in_db.first().product_id}" + bcolors.ENDC)
                        db_session.add(ProductSource(
                            sku=fbs_postin_product['sku'],
                            product_id=prod_in_db.first().product_id,
                            is_enabled=True,
                            source='fbs_undefined'))
                        db_session.commit()
                        db_session.add(FBSPostingsProducts(
                            sku=fbs_postin_product['sku'],
                            name=fbs_postin_product['name'],
                            quantity=fbs_postin_product['quantity'],
                            offer_id=fbs_postin_product['offer_id'],
                            price=int(float(fbs_postin_product['price'])),
                            posting_number=dict_entry['posting_number']
                        ))
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()
        
        def process_products_mandatory_marks(dict_entry : dict):
            """Func to parse products info into db from an entry in postings list"""
            for fbs_postin_product in dict_entry['products']:
                if fbs_postin_product['mandatory_mark']:
                    if True in [bool(mark) for mark in fbs_postin_product['mandatory_mark']]:
                        fbs_postin_product_mandamark_in_db = (db_session
                                    .query(FBSPostingsProductsMandatoryMarks)
                                    .filter_by(posting_number=dict_entry['posting_number'], sku=fbs_postin_product['sku']))
                        if fbs_postin_product_mandamark_in_db.first():
                            if not (set(fbs_postin_product['mandatory_mark']) ==
                            set([mandamark.mandatory_mark for mandamark in fbs_postin_product_mandamark_in_db.all()])):
                                print(f"For this posting's {dict_entry['posting_number']} sku - {fbs_postin_product['offer_id']} \
                                    mandatory marks don't match!")
                        else:
                            for mark in fbs_postin_product['mandatory_mark']:
                                db_session.add(FBSPostingsProductsMandatoryMarks(
                                    mandatory_mark=mark,
                                    sku=fbs_postin_product['sku'],
                                    posting_number=dict_entry['posting_number']
                                ))
                            try:
                                db_session.commit()
                            except exc.IntegrityError as e:
                                print('Committing failed -> ', e)
                                db_session.rollback()

        def process_posting_services(dict_entry: dict):
            """This one processes posting services (logistics mainly). """              # FIXME: relatively new method
            fbs_posting_service: dict[str, float] = dict_entry['financial_data']['posting_services']
            fbs_posting_service_in_db: FBSPostingsPostingServices = (db_session
                    .query(FBSPostingsPostingServices)
                    .filter_by(posting_number=dict_entry['posting_number'])
                    .first()
            )
            if not fbs_posting_service_in_db:
                fbs_posting_service_in_db: FBSPostingsPostingServices = FBSPostingsPostingServices(
                    posting_number=dict_entry['posting_number']
                )
                try:
                    db_session.add(fbs_posting_service_in_db)
                    db_session.commit()
                except exc.IntegrityError as e:
                    print('Committing failed -> ', e)
                    db_session.rollback()
            fbs_posting_service_in_db.marketplace_service_item_fulfillment=fbs_posting_service['marketplace_service_item_fulfillment']
            fbs_posting_service_in_db.marketplace_service_item_pickup=fbs_posting_service['marketplace_service_item_pickup']
            fbs_posting_service_in_db.marketplace_service_item_dropoff_pvz=fbs_posting_service['marketplace_service_item_dropoff_pvz']
            fbs_posting_service_in_db.marketplace_service_item_dropoff_sc=fbs_posting_service['marketplace_service_item_dropoff_sc']
            fbs_posting_service_in_db.marketplace_service_item_dropoff_ff=fbs_posting_service['marketplace_service_item_dropoff_ff']
            fbs_posting_service_in_db.marketplace_service_item_direct_flow_trans=fbs_posting_service['marketplace_service_item_direct_flow_trans']
            fbs_posting_service_in_db.marketplace_service_item_return_flow_trans=fbs_posting_service['marketplace_service_item_return_flow_trans']
            fbs_posting_service_in_db.marketplace_service_item_deliv_to_customer=fbs_posting_service['marketplace_service_item_deliv_to_customer']
            fbs_posting_service_in_db.marketplace_service_item_return_not_deliv_to_customer=fbs_posting_service['marketplace_service_item_return_not_deliv_to_customer']
            fbs_posting_service_in_db.marketplace_service_item_return_part_goods_customer=fbs_posting_service['marketplace_service_item_return_part_goods_customer']
            fbs_posting_service_in_db.marketplace_service_item_return_after_deliv_to_customer=fbs_posting_service['marketplace_service_item_return_after_deliv_to_customer']
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()



        def process_products_fin_data(dict_entry : dict):
            """This one processes products financial data (prices and etc) and also actions and costs of a
                given product in a posting"""
            for fbs_postin_findata in dict_entry['financial_data']['products']:
                fbs_postin_findata_in_db = (db_session
                        .query(FBSPostingsProductsFinData)
                        .filter_by(sku=fbs_postin_findata['product_id'], posting_number=dict_entry['posting_number'])
                        .first())
                if fbs_postin_findata_in_db:
                    fbs_postin_findata_in_db.commission_amount=fbs_postin_findata['commission_amount']
                    fbs_postin_findata_in_db.commission_percent=fbs_postin_findata['commission_percent']
                    fbs_postin_findata_in_db.payout=fbs_postin_findata['payout']
                    fbs_postin_findata_in_db.old_price=fbs_postin_findata['old_price']
                    fbs_postin_findata_in_db.price=fbs_postin_findata['price']
                    fbs_postin_findata_in_db.total_discount_value=fbs_postin_findata['total_discount_value']
                    fbs_postin_findata_in_db.total_discount_percent=fbs_postin_findata['total_discount_percent']
                    fbs_postin_findata_in_db.quantity=fbs_postin_findata['quantity']
                    fbs_postin_findata_in_db.client_price=(int(fbs_postin_findata['client_price']) if fbs_postin_findata['client_price'] else None)
                    
                    # first we check if all the actions are saved for a given product
                    fbs_postin_findata_actions_in_db = (db_session
                            .query(FBSPostingsProductsFinDataActions)
                            .filter_by(sku=fbs_postin_findata['product_id'], posting_number=dict_entry['posting_number'])
                            .all())
                    if fbs_postin_findata_actions_in_db:
                        actions_in_db = [action.sold_on_action for action in fbs_postin_findata_actions_in_db]
                        try:
                            assert set(fbs_postin_findata['actions']) == set(actions_in_db)
                        except AssertionError:
                            pass
                            # print(bcolors.WARNING + f"Actions fetched from API and in the DB are not the same for this combination \
                                # \n sku - {fbs_postin_findata['product_id']} ; posting number - {dict_entry['posting_number']}" + bcolors.ENDC)
                    else:
                        for fbs_postin_findata_action in fbs_postin_findata['actions']:
                            db_session.add(FBSPostingsProductsFinDataActions(
                                sku=fbs_postin_findata['product_id'],
                                posting_number=dict_entry['posting_number'],
                                sold_on_action=fbs_postin_findata_action
                            ))
                    
                    # then we check if there are any item services already in the DB
                    fbs_postin_findata_item_services_in_db = (db_session
                            .query(FBSPostingsProductsFinDataItemServices)
                            .filter_by(sku=fbs_postin_findata['product_id'], posting_number=dict_entry['posting_number'])
                            .first())
                    if fbs_postin_findata_item_services_in_db:
                        fbs_postin_findata_item_services_in_db.marketplace_service_item_fulfillment = fbs_postin_findata['item_services']['marketplace_service_item_fulfillment']
                        fbs_postin_findata_item_services_in_db.marketplace_service_item_pickup = fbs_postin_findata['item_services']['marketplace_service_item_pickup']
                        fbs_postin_findata_item_services_in_db.marketplace_service_item_dropoff_pvz = fbs_postin_findata['item_services']['marketplace_service_item_dropoff_pvz']
                        fbs_postin_findata_item_services_in_db.marketplace_service_item_dropoff_sc = fbs_postin_findata['item_services']['marketplace_service_item_dropoff_sc']
                        fbs_postin_findata_item_services_in_db.marketplace_service_item_dropoff_ff = fbs_postin_findata['item_services']['marketplace_service_item_dropoff_ff']
                        fbs_postin_findata_item_services_in_db.marketplace_service_item_direct_flow_trans = fbs_postin_findata['item_services']['marketplace_service_item_direct_flow_trans']
                        fbs_postin_findata_item_services_in_db.marketplace_service_item_return_flow_trans = fbs_postin_findata['item_services']['marketplace_service_item_return_flow_trans']
                        fbs_postin_findata_item_services_in_db.marketplace_service_item_deliv_to_customer = fbs_postin_findata['item_services']['marketplace_service_item_deliv_to_customer']
                        fbs_postin_findata_item_services_in_db.marketplace_service_item_return_not_deliv_to_customer = fbs_postin_findata['item_services']['marketplace_service_item_return_not_deliv_to_customer']
                        fbs_postin_findata_item_services_in_db.marketplace_service_item_return_part_goods_customer = fbs_postin_findata['item_services']['marketplace_service_item_return_part_goods_customer']
                        fbs_postin_findata_item_services_in_db.marketplace_service_item_return_after_deliv_to_customer = fbs_postin_findata['item_services']['marketplace_service_item_return_after_deliv_to_customer']
                    else:
                        db_session.add(FBSPostingsProductsFinDataItemServices(
                                sku=fbs_postin_findata['product_id'],
                                posting_number=dict_entry['posting_number'],
                                **(fbs_postin_findata['item_services'])
                            ))
                else:
                    db_session.add(FBSPostingsProductsFinData(
                        sku=fbs_postin_findata['product_id'],
                        posting_number=dict_entry['posting_number'],
                        commission_amount=fbs_postin_findata['commission_amount'],
                        commission_percent=fbs_postin_findata['commission_percent'],
                        payout=fbs_postin_findata['payout'],
                        old_price=fbs_postin_findata['old_price'],
                        price=fbs_postin_findata['price'],
                        total_discount_value=fbs_postin_findata['total_discount_value'],
                        total_discount_percent=fbs_postin_findata['total_discount_percent'],
                        quantity=fbs_postin_findata['quantity'],
                        client_price=(int(fbs_postin_findata['client_price']) if fbs_postin_findata['client_price'] else None)
                    ))
                    if fbs_postin_findata['actions']:
                        for fbs_postin_findata_action in fbs_postin_findata['actions']:
                            db_session.add(FBSPostingsProductsFinDataActions(
                                sku=fbs_postin_findata['product_id'],
                                posting_number=dict_entry['posting_number'],
                                sold_on_action=fbs_postin_findata_action
                            ))
                    db_session.add(FBSPostingsProductsFinDataItemServices(
                        sku=fbs_postin_findata['product_id'],
                        posting_number=dict_entry['posting_number'],
                        **(fbs_postin_findata['item_services'])
                    ))
                    
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()

        if not single_posting_number:
            for chunk in self.get_chunks(session=session):
                for fbs_posting_entry in chunk.json()['result']['postings']:
                    process_general(fbs_posting_entry)
                    process_delivery(fbs_posting_entry)
                    process_analytics_data(fbs_posting_entry)
                    process_products(fbs_posting_entry, session=session)
                    process_products_mandatory_marks(fbs_posting_entry)
                    process_products_fin_data(fbs_posting_entry)
                    process_posting_services(fbs_posting_entry)
            
            print(bcolors.OKBLUE + f"Successfully transitioned fbs postings to the db for {session.supplier.name}" + bcolors.ENDC)
        else:
            try:
                fbs_single_posting = PostPostingFbsGet(posting_number=single_posting_number).make_request(session=session, no_attention_flag=no_attention_flag).json()['result']
                process_general(fbs_single_posting)
                process_delivery(fbs_single_posting)
                process_analytics_data(fbs_single_posting)
                process_products(fbs_single_posting, session=session)
                process_products_mandatory_marks(fbs_single_posting)
                process_products_fin_data(fbs_single_posting)
                process_posting_services(fbs_single_posting)
            except AttributeError:
                print(bcolors.WARNING + f"This single posting {single_posting_number} hasn't been found" + bcolors.ENDC)
                return -1



class PostPostingFbsUnfulfilledList(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        dir : str = None,
        cutoff_from : date = None,
        cutoff_to : date = None,
        delivering_date_from : date = None,
        delivering_date_to : date = None,
        delivery_method_id : int = None,
        order_id : int = None,
        provider_id : int = None,
        warehouse_id : int = None,
        status : str = None,
        limit : int = 1000,
        offset : int = 0,
        translit : bool = False,
        analytics_data : bool = True,
        financial_data : bool = True,
        barcodes : bool = False
    ) -> None:

        # if not (since and to):
        #     since_ = (date.today() - timedelta(2)).strftime('%Y-%m-%dT21:00:00.00Z')
        #     to_ = (date.today() - timedelta(1)).strftime('%Y-%m-%dT20:59:59Z')
        # else:
        #     since_ = (since - timedelta(1)).strftime('%Y-%m-%dT21:00:00.00Z')
        #     to_ = (to).strftime('%Y-%m-%dT20:59:59Z')

        MPmethod.__init__(self, "POST", "/v3/posting/fbs/unfulfilled/list")
        self.payload : dict = {
            "dir" : dir,
            "filter" : {
                "delivery_method_id" : delivery_method_id,
                "order_id" : order_id,
                "provider_id" : provider_id,
                "warehouse_id" : warehouse_id,
                "status" : status,
                "cutoff_from" : cutoff_from,
                "cutoff_to" : cutoff_to,
                "delivering_date_from" : delivering_date_from,
                "delivering_date_to" : delivering_date_to
            },
            "limit" : limit,
            "offset" : offset,
            "with" : {
                "analytics_data" : analytics_data,
                "financial_data" : financial_data,
                "barcodes" : barcodes,
                "translit" : translit
            }
        }
    
    def make_request(self, session : MPsesh) -> Response:
        
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                # self.validate_response(response=response)                  # TODO : // think about addind validators right after getting the response from the server
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")

    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.PostPostingFbsList(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())


class PostReturnsFbo(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        posting_number : str = None,
        status : list[str] = None,
        limit : int = 1000,
        last_id : int = None
    ) -> None:

        MPmethod.__init__(self, "POST", "/v3/returns/company/fbo")
        self.payload : dict = {
            "filter" : {
                "posting_number" : posting_number,
                "status" : status
            },
            "limit" : limit,
            "last_id" : last_id
        }

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)                  # TODO : // think about addind validators right after getting the response from the server
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")

    def get_chunks(self, session : MPsesh) -> Generator[Response, None, None]:
        """This one gets responses as a generator if the limit passes 1000"""
        with self.make_request(session=session) as response:
            i = 0
            last_id_ = None

            while not ((len(response.json()['returns']) < 1000) and (i != 0)):
                with self.make_request(session=session, **{"last_id" : last_id_}) as response:
                    i += 1
                    last_id_ = response.json()['last_id']
                    yield response
                    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.PostReturnsFBO(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched fbo returns list for a given supplier"""
        def build_orders_tree(chunk : list[dict]) -> dict:
            """Building a dictionary consisting of keys as posting numbers (str) and UtlOrderReturn objects as values, it is used
            to better analyze the structure of a response and find not matching postings via order numbers"""
            fetched_orders : dict = {}
            for entry in chunk:
                order_no : str = "-".join(entry['posting_number'].split('-')[:2])
                if order_in_dct := fetched_orders.get(order_no):
                    order_in_dct.add_postings(entry)
                else:
                    order_ = UtlOrderReturn(order_id=order_no)
                    order_.add_postings(entry)
                    fetched_orders[order_no] = order_

            return fetched_orders

        def process_general(dict_entry : dict, cont : dict, session : MPsesh):
            """Func to parse general info into db from an entry in postings list"""
            def match_postings(order_number : str) -> dict:
                """getting all the necessary information on posting"""
                def build_tree(order_number : str) -> UtlOrderReturn:
                    """builds up an Order Return tree from the data in the db given the order number"""
                    stmt = lambda order_number : (
                            select(FBOPostingsProducts)
                                .join(FBOPostings, FBOPostings.posting_number == FBOPostingsProducts.posting_number)
                                .where(FBOPostings.order_number == order_number)
                        )
                    if result := db_session.execute(stmt(order_number=order_number)).scalars().all():
                        order : UtlOrderReturn = UtlOrderReturn(order_id=order_number)
                        for model_ in result:
                            if not order.postings.get(model_.posting_number):
                                order.postings[model_.posting_number] = UtlPostingReturn(order_number, model_.posting_number)
                                order.postings[model_.posting_number].skus.append(model_.sku)
                            else:
                                order.postings[model_.posting_number].skus.append(model_.sku)
                        return order
                    else:
                        print(f"There is no order {order_number}, got it while buildin tree up")
    
                order_in_db : UtlOrderReturn = build_tree(order_number=order_number)
                order_in_api : UtlOrderReturn = cont.get(order_number)
                if order_in_db.is_equal(order_in_api):
                    views_ : dict = order_in_db.view_skus
                    if not isinstance(views_, dict):
                        print(f"check this one {order_number}")
                    else:
                        return views_
                else:
                    print(bcolors.FAIL + f"fatal error for fbo returns, check this order - {order_number}" + bcolors.ENDC)
                    return -1

            return_year = (
                datetime.strptime(
                    dict_entry['accepted_from_customer_moment'].split('T')[0],
                    "%Y-%m-%d"
                ).year
            )
            if return_year < 2022:
                return False
            
            return_in_db : FBOReturns = db_session.query(FBOReturns).filter_by(posting_number=dict_entry['posting_number'], sku=dict_entry['sku'], fbo_return_id=dict_entry['id']).first()
            # return_alt_in_db : FBOReturns = db_session.query(FBOReturns).filter_by(sku=dict_entry['sku'], fbo_return_id=dict_entry['id']).first()
            order_number_ : str = "-".join(dict_entry['posting_number'].split('-')[:2])
            posting_prod_in_db = db_session.query(FBOPostingsProducts).filter_by(posting_number=dict_entry['posting_number'], sku=dict_entry['sku']).first()
            order_in_db = db_session.query(FBOPostings).filter_by(order_number=order_number_).all()

            if not any([return_in_db]):                   # TODO: !!! edit here - deleted "return_alt_in_db"
                if not posting_prod_in_db:
                    if order_in_db:
                        print(f"this {dict_entry['posting_number']} one is only in the form of order\
                                here is the list \t {[order.posting_number for order in order_in_db]}")
                        mapping : dict = match_postings(order_number=order_number_)
                        if mapping == -1:
                            return False
                        # this one is to check whether there is a return with already changed posting number
                        alt_return_in_db : FBOReturns = (
                                        db_session
                                            .query(FBOReturns)
                                            .filter_by(sku=dict_entry['sku'], fbo_return_id=dict_entry['id'], posting_number=mapping[dict_entry['sku']])
                                            .first()
                        )
                        if alt_return_in_db:
                            return False
                        posting_prod_in_db = (
                            db_session
                                .query(FBOPostingsProducts)
                                .filter_by(posting_number=mapping[dict_entry['sku']], sku=dict_entry['sku'])
                                .first()
                        )
                        if posting_prod_in_db:
                            db_session.add(FBOReturns(
                                posting_number=mapping[dict_entry['sku']],
                                sku=dict_entry['sku'],
                                order_number=order_number_,
                                last_posting_number=dict_entry['posting_number'],
                                quantity_returned=1,
                                accepted_from_customer_moment=dict_entry['accepted_from_customer_moment'],
                                supplier_id=session.supplier.id,
                                current_place_name=dict_entry['current_place_name'],
                                dst_place_name=dict_entry['dst_place_name'],
                                fbo_return_id=dict_entry['id'],
                                is_opened=dict_entry['is_opened'],
                                return_reason_name=dict_entry['return_reason_name'],
                                returned_to_ozon_moment=dict_entry['returned_to_ozon_moment'],
                                status_name=dict_entry['status_name']
                            ))
                            try:
                                db_session.commit()
                            except exc.IntegrityError as e:
                                print('Committing failed -> ', e)
                                db_session.rollback()
                        else:
                            print(f"For this posting {dict_entry['posting_number']} there is missing sku - {dict_entry['sku']}")
                    else:
                        print(f"this {dict_entry['posting_number']} one is not present at all")
                else:
                    posting_prod_in_db = db_session.query(FBOPostingsProducts).filter_by(posting_number=dict_entry['posting_number'], sku=dict_entry['sku']).first()
                    if posting_prod_in_db:
                        db_session.add(FBOReturns(
                            posting_number=dict_entry['posting_number'],
                            sku=dict_entry['sku'],
                            order_number=order_number_,
                            last_posting_number=dict_entry['posting_number'],
                            quantity_returned=1,
                            accepted_from_customer_moment=dict_entry['accepted_from_customer_moment'],
                            supplier_id=session.supplier.id,
                            current_place_name=dict_entry['current_place_name'],
                            dst_place_name=dict_entry['dst_place_name'],
                            fbo_return_id=dict_entry['id'],
                            is_opened=dict_entry['is_opened'],
                            return_reason_name=dict_entry['return_reason_name'],
                            returned_to_ozon_moment=dict_entry['returned_to_ozon_moment'],
                            status_name=dict_entry['status_name']
                        ))
                        try:
                            db_session.commit()
                        except exc.IntegrityError as e:
                            print('Committing failed -> ', e)
                            db_session.rollback()
                    else:
                        print(f"For this posting {dict_entry['posting_number']} there is missing sku - {dict_entry['sku']}")
            return True


        for chunk in self.get_chunks(session=session):
            fetched_api_orders : dict = build_orders_tree(chunk.json()['returns'])
            for entry in chunk.json()['returns']:
                if not process_general(entry, cont=fetched_api_orders, session=session):
                    continue
            
        
        print(bcolors.OKBLUE + f"Successfully transitioned fbo returns to the db for {session.supplier.name}" + bcolors.ENDC)


class PostReturnsFbs(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        posting_number : list[str] = None,
        accepted_from_customer_from : datetime = None,
        accepted_from_customer_to : datetime = None,
        last_free_from : datetime = None,
        last_free_to : datetime = None,
        order_id : int = None,
        product_name : str = None,
        offer_id : str = None,
        status : str = None,
        limit : int = 1000,
        last_id : int | None = None
    ) -> None:

        MPmethod.__init__(self, "POST", "/v3/returns/company/fbs")        
        self.payload : dict = {
            "filter" : {
                "accepted_from_customer_moment" : {
                    "time_from" : accepted_from_customer_from,
                    "time_to" : accepted_from_customer_to
                },
                "last_free_waiting_day" : {
                    "time_from" : last_free_from,
                    "time_to" : last_free_to
                },
                "order_id" : order_id,
                "posting_number" : posting_number,
                "status" : status,
                "product_name" : product_name,
                "product_offer_id" : offer_id
            },
            "limit" : limit,
            "last_id" : last_id
        }

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)                  # TODO : // think about addind validators right after getting the response from the server
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")

    def get_chunks(self, session : MPsesh) -> Generator[Response, None, None]:
        """This one gets responses as a generator if the limit passes 1000"""
        with self.make_request(session=session) as response:
            i = 0
            last_id_ = None
            while not ((len(response.json()['returns']) < 1000) and (i != 0)):
                with self.make_request(session=session, **{"last_id" : last_id_}) as response:
                    i += 1
                    last_id_ = response.json()['last_id']
                    yield response
                    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.PostReturnsFBS(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched fbs returns list for a given supplier"""
        def process_general(dict_entry : dict, session : MPsesh):
            """Func to parse general info into db from an entry in postings list"""
            if not dict_entry['posting_number'] or not dict_entry['return_date']:
                return False
            return_year = (
                            datetime.strptime(
                                dict_entry['return_date'].split('T')[0],
                                "%Y-%m-%d"
                                ).year
                            )
            if return_year < 2022:
                return False
            
            posting_return_in_db = db_session.query(FBSReturns).filter_by(posting_number=dict_entry['posting_number'], fbs_return_id=dict_entry['id']).first()
            posting_prod_in_db = db_session.query(FBSPostingsProducts).filter_by(posting_number=dict_entry['posting_number'], sku=dict_entry['sku']).first()
            order_number = "-".join(dict_entry['posting_number'].split('-')[:2])
            order_in_db = db_session.query(FBSPostings).filter_by(order_number=order_number).first()
            
            if posting_return_in_db:
                try:
                    assert posting_return_in_db.sku == dict_entry['sku']
                    assert posting_return_in_db.quantity_returned == dict_entry['quantity']
                except AssertionError:
                    print(f"Check this one out {dict_entry['posting_number']}, it seems like skus or qty don't match")
                posting_return_in_db.status = dict_entry['status']
                posting_return_in_db.is_moving = dict_entry['is_moving']
                posting_return_in_db.is_opened = dict_entry['is_opened']
                posting_return_in_db.last_free_waiting_day = dict_entry['last_free_waiting_day']
                posting_return_in_db.place_id = dict_entry['place_id']
                posting_return_in_db.moving_to_place_name = dict_entry['moving_to_place_name']
                posting_return_in_db.price = dict_entry['price']
                posting_return_in_db.price_without_commission = dict_entry['price_without_commission']
                posting_return_in_db.commission = dict_entry['commission']
                posting_return_in_db.commission_percent = dict_entry['commission_percent']
                posting_return_in_db.return_date = dict_entry['return_date']
                posting_return_in_db.return_reason_name = dict_entry['return_reason_name']
                posting_return_in_db.waiting_for_seller_date_time = dict_entry['waiting_for_seller_date_time']
                posting_return_in_db.returned_to_seller_date_time = dict_entry['returned_to_seller_date_time']
                posting_return_in_db.waiting_for_seller_days = dict_entry['waiting_for_seller_days']
                posting_return_in_db.returns_keeping_cost = dict_entry['returns_keeping_cost']
                db_session.commit()
                return False

            if not posting_prod_in_db:
                if not order_in_db:
                    add_single : Union[int, bool] = PostPostingFbsList().process_to_db(session=session, single_posting_number=dict_entry['posting_number'])
                    if add_single == -1:
                        print(f"This one {dict_entry['posting_number']} has not been added")
                        return False
                    posting_prod_in_db = db_session.query(FBSPostingsProducts).filter_by(posting_number=dict_entry['posting_number'], sku=dict_entry['sku']).first()
                else:
                    print(f"Order {order_number} is in the database, but lack this posting {dict_entry['posting_number']}")
                    return False

            db_session.add(FBSReturns(
                fbs_return_id=dict_entry['id'],
                posting_number=posting_prod_in_db.posting_number,
                sku=dict_entry['sku'],
                last_posting_number=dict_entry['posting_number'],
                quantity_returned=dict_entry['quantity'],
                supplier_id=session.supplier.id,
                status=dict_entry['status'],
                order_number=order_number,
                is_moving=dict_entry['is_moving'],
                is_opened=dict_entry['is_opened'],
                last_free_waiting_day=dict_entry['last_free_waiting_day'],
                place_id=dict_entry['place_id'],
                moving_to_place_name=dict_entry['moving_to_place_name'],
                price=dict_entry['price'],
                price_without_commission=dict_entry['price_without_commission'],
                commission=dict_entry['commission'],
                commission_percent=dict_entry['commission_percent'],
                return_date=dict_entry['return_date'],
                return_reason_name=dict_entry['return_reason_name'],
                waiting_for_seller_date_time=dict_entry['waiting_for_seller_date_time'],
                returned_to_seller_date_time=dict_entry['returned_to_seller_date_time'],
                waiting_for_seller_days=dict_entry['waiting_for_seller_days'],
                returns_keeping_cost=dict_entry['returns_keeping_cost']
            ))
            db_session.commit()
            


        for chunk in self.get_chunks(session=session):
            for entry in chunk.json()['returns']:
                if not process_general(dict_entry=entry, session=session):
                    continue
            
        
        print(bcolors.OKBLUE + f"Successfully transitioned fbs returns to the db for {session.supplier.name}" + bcolors.ENDC)


class PostFinanceTransactionList(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        posting_number : str = None,
        from_ : datetime = None,                    #Формат: YYYY-MM-DDTHH:mm:ss.sssZ. Пример: 2019-11-25T10:43:06.51.
        to_ : datetime = None,  
        operation_type : list[schemas.FinancialOperationTypeEnum] = None,
        transaction_type : schemas.FinancialTransactionTypeEnum = "all",
        page : int = 1,
        page_size : int = 1000
    ) -> None:

        MPmethod.__init__(self, "POST", "/v3/finance/transaction/list")
        if not (from_ and to_):
            from_ = (date.today() - timedelta(3)).strftime('%Y-%m-%dT21:00:00.00Z')
            to_ = (date.today()).strftime('%Y-%m-%dT20:59:59Z')
        else:
            if round(abs(from_ - to_).days / 15, 2) > 1.00:
                print(f"Not recommending taking a period more than 15 days for finance transactions")
            from_ = (from_ - timedelta(1)).strftime('%Y-%m-%dT21:00:00.00Z')
            to_ = (to_).strftime('%Y-%m-%dT20:59:59Z')


        self.payload : dict = {
            "filter" : {
                "date" : {
                    "from" : from_,
                    "to" : to_
                },
                "operation_type" : operation_type,
                "posting_number" : posting_number,
                "transaction_type" : transaction_type
            },
            "page" : page,
            "page_size" : page_size
        }

    def setup_checker(self) -> None:
        """sets up utils.checker.Checker for checking warnings and discrepancies"""
        # MethodChecker()
        pass

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload, stream=True) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")

    def get_chunks(self, session : MPsesh) -> Generator[Response, None, None]:
        """This one gets responses as a generator if the limit passes 1000"""
        pages : int = 1
        i : int = 1
        while not i == (pages + 1):
            self.payload['page'] = i
            with session.post(self.url, json=self.payload) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    if (not response.json()['result']['operations']) and (response.json()['result']['row_count'] == 0):         # FIXME: maybe should add page_count == 0 too
                        print("There are no transactions for this account unfortunately, response ->")
                        print(response.json())
                        return [-1]
                    pages = response.json()['result']['page_count']
                    i += 1
                    yield response
                else:
                    print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}")
                    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.PostFinanceTransactionListResult(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched fbs returns list for a given supplier"""
        def process_general(dict_entry : dict, session : MPsesh) -> None:
            """Func to parse general info into db from an entry in postings list"""
            def check_integrity_of_transaction(dict_repr_trans : dict, repr_trans_in_db : FinanceTransactions, session : MPsesh) -> bool:
                """This one is for checking the integrity of transaction's representation in the DB and from the API.
                We assume that if we've fetched a transaction once, then its fields won't change."""
                try:
                    assert repr_trans_in_db.operation_id == dict_repr_trans['operation_id'], 'assumption failed for operation id'
                    assert repr_trans_in_db.operation_type == dict_repr_trans['operation_type'], 'assumption failed for operation type'
                    assert repr_trans_in_db.operation_type_name == dict_repr_trans['operation_type_name'], 'assumption failed for operation type name '
                    assert repr_trans_in_db.operation_date == datetime.strptime(dict_repr_trans['operation_date'], '%Y-%m-%d %H:%M:%S'), 'assumption failed for operation date'
                    assert float(repr_trans_in_db.delivery_charge) == round(float(dict_repr_trans['delivery_charge']), 2), 'assumption failed for operation delivery charge'
                    assert float(repr_trans_in_db.return_delivery_charge) == round(float(dict_repr_trans['return_delivery_charge']), 2), 'assumption failed for operation return delivery charge'
                    assert float(repr_trans_in_db.accruals_for_sale) == round(float(dict_repr_trans['accruals_for_sale']), 2), 'assumption failed for operation accruals for sale'
                    assert float(repr_trans_in_db.sale_commission) == round(float(dict_repr_trans['sale_commission']), 2), 'assumption failed for operation sale commssion'
                    assert float(repr_trans_in_db.amount) == round(float(dict_repr_trans['amount']), 2), 'assumption failed for operation amount'
                    assert repr_trans_in_db.type == dict_repr_trans['type'], 'assumption failed for operation type'
                    assert repr_trans_in_db.supplier_id == int(session.supplier.id), 'assumption failed for operation supplier'
                    return True
                except AssertionError as e:
                    print(f"failed for -> {dict_repr_trans['operation_id']}, heres the error - > {e}")
                    return False

            if db_session.query(FinanceTransactions).filter_by(operation_id=dict_entry['operation_id']).first():
                finance_transaction_in_db : FinanceTransactions = db_session.query(FinanceTransactions).filter_by(operation_id=dict_entry['operation_id']).first()
                if not check_integrity_of_transaction(dict_repr_trans=dict_entry, repr_trans_in_db=finance_transaction_in_db, session=session):
                    print(f"check this operation -> {dict_entry['operation_id']}")
                    finance_transaction_in_db.operation_type = dict_entry['operation_type']
                    finance_transaction_in_db.operation_type_name = dict_entry['operation_type_name']
                    finance_transaction_in_db.operation_date = dict_entry['operation_date']
                    finance_transaction_in_db.delivery_charge = round(float(dict_entry['delivery_charge']), 2)
                    finance_transaction_in_db.return_delivery_charge = round(float(dict_entry['return_delivery_charge']), 2)
                    finance_transaction_in_db.accruals_for_sale = round(float(dict_entry['accruals_for_sale']), 2)
                    finance_transaction_in_db.sale_commission = round(float(dict_entry['sale_commission']), 2)
                    finance_transaction_in_db.amount = round(float(dict_entry['amount']), 2)
                    try:
                        db_session.commit()
                    except exc.IntegrityError as e:
                        print('Committing failed -> ', e)
                        db_session.rollback()

                return False
            db_session.add(FinanceTransactions(
                operation_id=dict_entry['operation_id'],
                operation_type=dict_entry['operation_type'],
                operation_type_name=dict_entry['operation_type_name'],
                operation_date=dict_entry['operation_date'],
                delivery_charge=float(dict_entry['delivery_charge']),
                return_delivery_charge=float(dict_entry['return_delivery_charge']),
                accruals_for_sale=float(dict_entry['accruals_for_sale']),
                sale_commission=float(dict_entry['sale_commission']),
                amount=float(dict_entry['amount']),
                type=dict_entry['type'],
                supplier_id=session.supplier.id
            ))
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()
        
        def process_posting(dict_entry : dict, session : MPsesh) -> None:
            """Func to parse general info into db from an entry in postings list"""
            def check_delivery_schema(dict_entry : dict, session : MPsesh) -> str:
                """Checks delivery_schema field in the response containing posting information. If it is null and other values are filled then it
                proceeds to quick search to find out on which delivery schema a posting was, otherwise just returns a string containing the delivery
                schema name."""
                def find_posting_delivschema(posting_number : str) -> Tuple[str, str]:
                    """Finds a posting's delivery schema given its posting number"""
                    if (db_session.query(FBOPostings).filter_by(posting_number=posting_number).first()):
                        return ('FBO', posting_number)
                    elif (db_session.query(FBSPostings).filter_by(posting_number=posting_number).first()):
                        if db_session.query(FBSPostings).filter_by(posting_number=posting_number).first().is_express:
                            return ('RFBS', posting_number)
                        else:
                            return ('FBS', posting_number)
                    else:
                        return 0

                def find_posting_delivschema_by_order(order_number: str) -> Tuple[str, str]:
                    """
                    Became necessary when they had introduced acquiring operations.
                    Not correct way to do it, but the existing schema can handle it
                    this way. Finds the first posting by order number and connects it
                    """
                    fetched_queries: dict[str, FBOPostings | FBSPostings | None] = {
                        'fbo': db_session.query(FBOPostings).filter_by(order_number=order_number),
                        'fbs': db_session.query(FBSPostings).filter_by(order_number=order_number)
                    }
                    if num_of_postings := fetched_queries['fbo'].count():
                        if num_of_postings > 1:
                            print(
                                    bcolors.WARNING,
                                    f"Acquiring operation for {order_number} actually has {num_of_postings} postings \
                                        take into account",
                                    bcolors.ENDC
                                )
                        return ('FBO', fetched_queries['fbo'].first().posting_number)
                    elif num_of_postings := fetched_queries['fbs'].count():
                        if num_of_postings > 1:
                            print(
                                    bcolors.WARNING,
                                    f"Acquiring operation for {order_number} actually has {num_of_postings} postings \
                                        take into account",
                                    bcolors.ENDC
                                )
                        if fetched_queries['fbs'].first().is_express:
                            return ('RFBS', fetched_queries['fbs'].first().posting_number)
                        else:
                            return ('FBS', fetched_queries['fbs'].first().posting_number)
                    else:
                        return 0


                if not dict_entry['order_date'] and not dict_entry['posting_number']:
                    return 0
                elif (not dict_entry['posting_number']) and (not dict_entry['delivery_schema']) and (dict_entry['order_date']):
                    print(
                        bcolors.WARNING,
                        f"This finance transaction's posting part is wrong, \n for supplier \
                        {session.supplier.name} it says -> {dict_entry}",
                        bcolors.ENDC
                    )
                    return 0
                elif not dict_entry['delivery_schema'] and (dict_entry['order_date'] and dict_entry['posting_number']):
                    found_delivschema : Tuple[str, str] = find_posting_delivschema(dict_entry['posting_number'])
                    if found_delivschema:
                        return found_delivschema
                    else:
                        found_delivschema = find_posting_delivschema_by_order(dict_entry['posting_number'])
                        if not found_delivschema:
                            print(bcolors.FAIL + f"Couldn't find this posting in the DB to find out its delivery schema -- {dict_entry['posting_number']}" + bcolors.ENDC)
                            return 0
                        return found_delivschema
                else:
                    if dict_entry['delivery_schema'] == 'FBO':
                        fbo_posting_checked_in_db : FBOPostings = db_session.query(FBOPostings).filter_by(posting_number=dict_entry['posting_number']).first()
                        if not fbo_posting_checked_in_db:
                            if PostPostingFboList().process_to_db(session=session, single_posting_number=dict_entry['posting_number']) == -1:
                                # if the posting can't even be fetched via API, it must have been changed due to a cancellation or return, thus
                                # we proceed to find it by last_posting_number in returns table in the database
                                returned_fbo_in_db : FBOReturns = db_session.query(FBOReturns).filter_by(last_posting_number=dict_entry['posting_number']).first()
                                if not returned_fbo_in_db:
                                    print(f"Failed to fetch posting for transactions -- {dict_entry['posting_number']}")
                                    return 0
                                return ('FBO', returned_fbo_in_db.posting_number)
                                
                    else:
                        fbs_posting_checked_in_db : FBSPostings = db_session.query(FBSPostings).filter_by(posting_number=dict_entry['posting_number']).first()
                        if not fbs_posting_checked_in_db:
                            if PostPostingFbsList().process_to_db(session=session, single_posting_number=dict_entry['posting_number']) == -1:
                                print(f"Failed to fetch posting for transactions -- {dict_entry['posting_number']}")
                    return (dict_entry['delivery_schema'], dict_entry['posting_number'])

            if not check_delivery_schema(dict_entry['posting'], session=session):
                return False
            checked_delivery_schema, checked_posting_number = check_delivery_schema(dict_entry['posting'], session=session)
            operation_posting_in_db = db_session.query(FinanceTransactionsOperationPosting).filter_by(operation_id=dict_entry['operation_id']).first()
            if operation_posting_in_db:
                try:
                    assert operation_posting_in_db.delivery_schema == checked_delivery_schema
                    assert operation_posting_in_db.order_date == datetime.strptime(dict_entry['posting']['order_date'], '%Y-%m-%d %H:%M:%S')
                    if operation_posting_in_db.delivery_schema == 'FBO':
                        assert operation_posting_in_db.fbo_posting_number == checked_posting_number
                    else:
                        assert operation_posting_in_db.fbs_posting_number == checked_posting_number
                except AssertionError as e:
                    # (
                    #     print(bcolors.FAIL + 
                    #     f"For this operation's posting info don't match in the DB and API - {dict_entry['operation_id']}"
                    #     + bcolors.ENDC)
                    # )
                    pass
                return False
            if checked_delivery_schema != 'FBO':
                db_session.add(FinanceTransactionsOperationPosting(
                    operation_id=dict_entry['operation_id'],
                    delivery_schema=checked_delivery_schema,
                    order_date=dict_entry['posting']['order_date'],
                    fbs_posting_number=checked_posting_number,
                    warehouse_id=dict_entry['posting']['warehouse_id']
                ))

                try:
                    db_session.commit()
                except exc.IntegrityError as e:
                    print('Committing failed -> ', e)
                    db_session.rollback()

                return True
            else:
                db_session.add(FinanceTransactionsOperationPosting(
                    operation_id=dict_entry['operation_id'],
                    delivery_schema=checked_delivery_schema,
                    order_date=dict_entry['posting']['order_date'],
                    fbo_posting_number=checked_posting_number,
                    warehouse_id=dict_entry['posting']['warehouse_id']
                ))

                try:
                    db_session.commit()
                except exc.IntegrityError as e:
                    print('Committing failed -> ', e)
                    db_session.rollback()

                return True

        def process_items(dict_entry : dict) -> None:
            """Func to parse items info into db from an entry in postings list. Needs heavy rethinking"""
            def check_in_db(oper_id : int, dict_entry : dict) -> bool:
                """Checking if items for a given operation id is in the DB, and if so we check if count of items
                is the same."""
                operation_items_in_db = (
                    db_session
                        .query(FinanceTransactionsOperationItems)
                        .filter_by(operation_id=oper_id)
                )
                # checking if item is in the DB
                if operation_items_in_db.all():
                    if len(dict_entry) != operation_items_in_db.count():
                        print(f"For this operation - {oper_id} count of items is not the same")
                        return True
                    
                    # checking the integrity of names and skus from API and in the DB
                    item_in_db_names : set = set([item_in_db.name for item_in_db in operation_items_in_db.all()])
                    item_in_db_skus : set = set([item_in_db.sku for item_in_db in operation_items_in_db.all()])

                    item_from_api_names : set = set([item_from_api['name'] for item_from_api in dict_entry])
                    item_from_api_skus : list = []
                    for item_from_api in dict_entry:
                        if item_from_api['sku'] == 0:
                            item_from_api_skus.append(None)
                            continue
                        item_from_api_skus.append(item_from_api['sku'])
                    item_from_api_skus : set = set(item_from_api_skus)
                    
                    try:
                        # assert item_in_db_names == item_from_api_names
                        assert item_in_db_skus == item_from_api_skus
                    except AssertionError as e:
                        print(
                            bcolors.FAIL,
                            f"These names from db - {item_in_db_skus} \
                                and names from api - {item_from_api_skus} \
                                of operation {oper_id} items in the DB won't match with those from API - {e}",
                            bcolors.ENDC
                        )
                    return True
                return False
            
            def process_each_item(oper_id : int, process_dict_entry : dict) -> FinanceTransactionsOperationItems:
                """processes each item from a dictionary"""
                # if dict_entry['sku']:
                #     sku_in_db = db_session.query(ProductSource).filter_by(sku=dict_entry['sku']).first()
                #     if not sku_in_db:
                #         PostProductInfo(sku=dict_entry['sku']).process_to_db(session=session)
                #         print(bcolors.WARNING + f"couldn't find this sku {dict_entry['sku']} in the DB \
                #             while processing this transaction - {oper_id}" + bcolors.ENDC)
                return FinanceTransactionsOperationItems(
                    operation_id=oper_id,
                    name=process_dict_entry['name'] if process_dict_entry['name'] else None,
                    sku=process_dict_entry['sku'] if process_dict_entry['sku'] else None
                )

            if (not dict_entry['items']) or (check_in_db(oper_id=dict_entry['operation_id'], dict_entry=dict_entry['items'])):
                return False
            for item_ in dict_entry['items']:
                if dict_entry['type'] == 'compensation':
                    compensated_sku_in_db: ProductSource = db_session.query(ProductSource).filter_by(sku=item_['sku']).first()
                    if not compensated_sku_in_db:
                        prod_name: str = item_['name'].split('Уцененный')[0].rstrip('. ')
                        product_by_name_in_db: ProductSource = db_session.query(Product).filter_by(name=prod_name)
                        if product_by_name_in_db:
                            if product_by_name_in_db.count() > 1:
                                print(bcolors.FAIL, f"There is more than one product found by name of a compensated position, \
                                    situation is obscure, please look at it => {item_['sku']}", bcolors.ENDC)
                                continue
                            sku_to_add: ProductSource = ProductSource(
                                sku=item_['sku'],
                                product_id=product_by_name_in_db.first().product_id, 
                                source='fbo_undefined',
                                is_enabled=False
                            )
                            try:
                                db_session.add(sku_to_add)
                                db_session.commit()
                            except exc.IntegrityError as e:
                                print('Committing failed -> ', e)
                                db_session.rollback()

                fin_operation_item : FinanceTransactionsOperationItems = process_each_item(oper_id=dict_entry['operation_id'], process_dict_entry=item_)
                try:
                    db_session.add(fin_operation_item)
                    db_session.commit()
                except exc.IntegrityError as e:
                    print('Committing failed -> ', e)
                    db_session.rollback()

        def process_services(dict_entry: dict) -> None:
            """Processes services incurred to the transaction"""
            def check_in_db(oper_id: int, dict_entry: list[dict]) -> bool:
                """Checking if items for a given operation id is in the DB, and if so we check if count of items
                is the same. The same with the amount of services incurred"""
                operation_srvcs_in_db = (
                    db_session
                        .query(FinanceTransactionsOperationServices)
                        .filter_by(operation_id=oper_id)
                )

                srvcs_in_db: list[dict[str, Union[str, float]]] = [{'name' : op.name, 'price' : round(float(op.price), 2)} for op in operation_srvcs_in_db.all()]
                srvcs_from_api: list[dict[str, Union[str, float]]] = dict_entry
                for srvc_entry in srvcs_from_api:
                    srvc_entry['price'] = round(float(srvc_entry['price']), 2)
                
                # checking if item is in the DB
                if srvcs_in_db != srvcs_from_api:                    
                    # print(f"For this operation - {oper_id} count of services is not the same")
                    # TODO: this one is highly experimental!
                    operation_srvcs_in_db.delete()
                    try:
                        db_session.commit()
                    except exc.IntegrityError as e:
                        print('Committing failed -> ', e)
                        db_session.rollback()
                    return False
                    
                    # # checking the integrity of names and skus from API and in the DB
                    # item_in_db_names : set = set([item_in_db.name for item_in_db in operation_srvcs_in_db.all()])
                    # item_in_db_prices : set = set([round(float(item_in_db.price), 2) for item_in_db in operation_srvcs_in_db.all()])

                    # item_from_api_names : set = set([item_from_api['name'] for item_from_api in dict_entry])
                    # item_from_api_prices : set = set([round(float(item_from_api['price']), 2) for item_from_api in dict_entry])
                    
                    # try:
                    #     assert item_in_db_names == item_from_api_names
                    #     assert item_in_db_prices == item_from_api_prices
                    # except AssertionError as e:
                    #     print(
                    #         bcolors.FAIL,
                    #         f"These services from db - {item_in_db_prices} \
                    #             and services from api - {item_from_api_prices} \
                    #             of operation {oper_id} items in the DB won't match with those from API - {e}",
                    #         bcolors.ENDC
                    #     )
                    #     # TODO: this one is highly experimental!
                    #     operation_srvcs_in_db.delete()
                    #     try:
                    #         db_session.commit()
                    #     except exc.IntegrityError as e:
                    #         print('Committing failed -> ', e)
                    #         db_session.rollback()
                    #     return False
                return True
            
            def process_each_item(oper_id : int, process_dict_entry : dict) -> FinanceTransactionsOperationServices:
                """processes each item from a dictionary"""
                return FinanceTransactionsOperationServices(
                    operation_id=oper_id,
                    name=process_dict_entry['name'],
                    price=round(float(process_dict_entry['price']), 2)
                )

            if (not dict_entry['services']) or (check_in_db(oper_id=dict_entry['operation_id'], dict_entry=dict_entry['services'])):
                return False
            for item_ in dict_entry['services']:
                fin_operation_service : FinanceTransactionsOperationServices = process_each_item(oper_id=dict_entry['operation_id'], process_dict_entry=item_)
                try:
                    db_session.add(fin_operation_service)
                    db_session.commit()
                except exc.IntegrityError as e:
                    print('Committing failed -> ', e)
                    db_session.rollback()



        for chunk in self.get_chunks(session=session):
            if chunk == -1:
                return None
            for operation_entry in chunk.json()['result']['operations']:
                process_general(operation_entry, session=session)
                process_items(operation_entry)
                # TODO: have to change this behaviour. ASSUMPTION! - if a transaction doesn't have attached
                # posting to it, then it won't have services too. But have to check it regularly.
                process_posting(operation_entry, session=session)
                process_services(operation_entry)
        
        print(bcolors.OKBLUE + f"Successfully transitioned finance transactions to the db for {session.supplier.name}" + bcolors.ENDC)

class PostAnalyticsItemTurnover(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        date_from : datetime = None                    #Формат: Дата. 1-е или 15-е число месяца в формате: 2021-05-01.
    ) -> None:

        MPmethod.__init__(self, "POST", "/v1/analytics/item_turnover")
        if not date_from:
            # days_in_month : int = (
            #     date(date.today().year, (date.today().month - 1), 1) - date(date.today().year, date.today().month, 1)
            # ).days
            month_day : int = date.today().day
            if month_day in range(1, 16):
                from_ = date(date.today().year, date.today().month, 1)
            else:
                from_ = date(date.today().year, date.today().month, 15)
        else:
            from_ = date_from


        self.payload : dict = {
            "date_from" : from_.strftime('%Y-%m-%d')
        }

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
                    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.PostAnalyticsItemTurnover(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched fbs returns list for a given supplier"""
        def process_entries(period_ : str, dict_entry : dict, category_id_ : int, session: MPsesh) -> None:
            """processes each entry"""
            # first we check if item commission part is significant enough
            if dict_entry['item_commission_part'] < 0.5:
                return False
            # then we try to find sku in our DB, if it is not there unfortunately we won't add it
            # but TODO : we can make requests via account handler and get some of the discounted
            sku_in_db = db_session.query(ProductSource).filter_by(sku=dict_entry['sku']).first()
            if not sku_in_db:
                if PostProductInfoDiscounted(discounted_skus=[dict_entry['sku']]).process_to_db(session=session) == -1:
                    print(bcolors.WARNING + f"this sku for item turnover hasn't been found - {dict_entry['sku']}" + bcolors.ENDC)
                    return False
            try:
                turnover_for_item : int = int(dict_entry['turnover'])
            except ValueError:
                turnover_for_item : str = dict_entry['turnover']

            anal_item_turnover_in_db = db_session.query(AnalyticsItemTurnover).filter_by(
                                                    period=period_,
                                                    category_id=category_id_,
                                                    sku=dict_entry['sku'],
                                                    last_updated_at=datetime.strptime(res['date'], '%d.%m.%Y')
                                                ).first()
            if anal_item_turnover_in_db:
                return False
            anal_item_turnover = AnalyticsItemTurnover(
                                    period=period_,
                                    category_id=category_id_,
                                    sku=dict_entry['sku'],
                                    discounted=dict_entry['discounted'],
                                    turnover=(turnover_for_item if isinstance(turnover_for_item, int) else None),
                                    threshold_free=(dict_entry['threshold_free'] if (isinstance(dict_entry['threshold_free'], int) and dict_entry['threshold_free'] < 10_000) else None),
                                    avg_sold_items=(round(dict_entry['avg_sold_items'], 2) if (isinstance(dict_entry['avg_sold_items'], float) and dict_entry['avg_sold_items'] > 0.1) else None),
                                    avg_stock_items=(round(dict_entry['avg_stock_items'], 2) if (isinstance(dict_entry['avg_stock_items'], float) and dict_entry['avg_stock_items'] > 0.1) else None),
                                    avg_stock_items_free=(round(dict_entry['avg_stock_items_free'], 2) if (isinstance(dict_entry['avg_stock_items_free'], float) and dict_entry['avg_stock_items_free'] > 0.1) else None),
                                    item_commission_part=(round(dict_entry['item_commission_part'], 2) if (isinstance(dict_entry['item_commission_part'], float) and dict_entry['item_commission_part'] > 0.1) else None),
                                    last_updated_at=datetime.strptime(res['date'], '%d.%m.%Y')
                                )
            try:
                db_session.add(anal_item_turnover)
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()

        try:
            res : dict = self.make_request(session).json()
            for category_ in res['categories']:
                for item_ in category_['turnover_items']:
                    if not process_entries(dict_entry=item_, period_=res['period'], category_id_=category_['category_id'], session=session):
                        continue

            print(bcolors.OKBLUE + f"Successfully transitioned analytics turnover to the db for {session.supplier.name}" + bcolors.ENDC)

        except AttributeError:
            print(bcolors.FAIL + f"Request was unsuccessful for analytics turnover" + bcolors.ENDC)


class PostAnalyticsData(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        date_from : date = None,                                #Формат: 2020-09-01.
        date_to : date = None,                                  #Формат: 2020-09-01.
        dimension : list[str] = ['sku'],                        #Группировка данных в отчёте
        key_ : str = None,                                      #Параметр сортировки. Можно передать любой атрибут из параметров dimension и metric, кроме атрибута brand
        op : str = None,                                        #Операция сравнения. Default: "EQ"
        value_ : str = None,                                    # Значение для сравнения.
        limit : int = 1000,
        offset : int = 0,
        metrics : list[str] = [
            'hits_tocart_search',
            'hits_tocart_pdp',
            'hits_tocart',
            'conv_tocart_search',
            'conv_tocart_pdp',
            'conv_tocart',
            'adv_view_pdp',
            'adv_view_search_category',
            'adv_view_all',
            'adv_sum_all',
            'position_category'
        ],                     # Укажите до 14 метрик. Если их будет больше, вы получите ошибку с кодом InvalidArgument.
        order : str = None,                             # Вид сортировки ASC DESC
    ) -> None:

        MPmethod.__init__(self, "POST", "/v1/analytics/data")
        if (not date_from) and (not date_to):
            date_from : date = date.today() - timedelta(days=1)
            date_to : date = date.today() - timedelta(days=1)

        self.payload : dict = {
            "date_from" : date_from.strftime('%Y-%m-%d'),
            "date_to" : date_to.strftime('%Y-%m-%d'),
            "dimension" : dimension,
            # "filters" : {
            #     "key" : key_,
            #     "op" : op,
            #     "value" : value_
            # },
            "limit" : limit,
            "offset" : offset,
            "metrics" : metrics
            # "sort" : {
            #     "key" : key_,
            #     "order" : order
            # }
        }

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            elif response.status_code == 429:
                time.sleep(10)
                self.make_request(session=session, **kwargs)
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
                    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.PostAnalyticsData(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    # def get_chunks(self, session : MPsesh) -> Generator[Response, None, None]:            TODO: this is old representation of getting chunks with
    #     """This one gets responses as a generator if the limit passes 1000"""                     self.make_request method, deprecated
    #     with self.make_request(session=session) as response:
    #         i = 0
    #         while not ((len(response.json()['result']['data']) < 1000) and (i != 0)):
    #             with self.make_request(session=session, **{"offset" : (i * 1000)}) as response:
    #                 i += 1
    #                 yield response

    def get_chunks(self, session : MPsesh) -> Generator[Response, None, None]:
        """This one gets responses as a generator if the limit passes 1000"""
        check : int = 1
        i : int = 0
        while check:
            self.payload['offset'] = (i * 1_000)
            with session.post(self.url, json=self.payload) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    check = (len(response.json()['result']['data']) // 1_000)
                    i += 1
                    yield response
                    time.sleep(5)                                      # added this sleep to overcome 429 error
                else:
                    print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}")

    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched fbs returns list for a given supplier"""
        def process_entries(dict_entry : dict, num : int, session: MPsesh) -> None:
            """Processes metrics from data"""
            try:
                assert len(dict_entry['dimensions']) == 1
            except AssertionError:
                print(bcolors.FAIL + f"Not single entry from analytics data, its index in response - {num}" + bcolors.ENDC)
                return False
            sku_in_db : ProductSource = db_session.query(ProductSource).filter_by(sku=dict_entry['dimensions'][0]['id']).first()
            if not sku_in_db:
                if PostProductInfoDiscounted(discounted_skus=[str(dict_entry['dimensions'][0]['id'])]).process_to_db(session=session) == -1:
                    print(bcolors.FAIL + f"Couldn't find this sku from analytics data - {dict_entry['dimensions'][0]['id']}" + bcolors.ENDC)
                    return False

            analy_data_in_db = db_session.query(AnalyticsData).filter_by(
                                                        sku=dict_entry['dimensions'][0]['id'],
                                                        date_=self.payload['date_from']
                                                    )
            if analy_data_in_db.first():
                try:
                    assert analy_data_in_db.count() == 1
                except AssertionError:
                    print(bcolors.FAIL + f"Not single entry for this sku - {dict_entry['dimensions'][0]['id']}, has duplicates in DB" + bcolors.ENDC)
                    return False
                return False

            data_in_db = AnalyticsData(
                sku=dict_entry['dimensions'][0]['id'],
                date_=self.payload['date_from'],
                hits_tocart_search=round(dict_entry['metrics'][0], 2),
                hits_tocart_pdp=round(dict_entry['metrics'][1], 2),
                hits_tocart=round(dict_entry['metrics'][2], 2),
                conv_tocart_search=round(dict_entry['metrics'][3], 2),
                conv_tocart_pdp=round(dict_entry['metrics'][4], 2),
                conv_tocart=round(dict_entry['metrics'][5], 2),
                adv_view_pdp=round(dict_entry['metrics'][6], 2),
                adv_view_search_category=round(dict_entry['metrics'][7], 2),
                adv_view_all=round(dict_entry['metrics'][8], 2),
                adv_sum_all=round(dict_entry['metrics'][9], 2),
                position_category=round(dict_entry['metrics'][10], 2)
            ) 
            try:
                db_session.add(data_in_db)
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()

        for chunk in self.get_chunks(session=session):
            for num_, item_ in enumerate(chunk.json()['result']['data']):
                if not process_entries(dict_entry=item_, num=num_, session=session):
                    continue

        print(bcolors.OKBLUE + f"Successfully transitioned analytics data to the db for {session.supplier.name}" + bcolors.ENDC)


class Postv2AnalyticsStockOnWarehouses(MPmethod):
    """ Отчёт по остаткам и товарам в перемещении по складам Ozon.
    """
    def __init__(
        self,
        limit : int = 1000,
        offset : int = 0,
        warehouse_type : str = 'ALL'                                                # Фильтр по типу склада:
                                                                                    #   EXPRESS_DARK_STORE — склады Ozon с доставкой Fresh.
                                                                                    #   NOT_EXPRESS_DARK_STORE — склады Ozon без доставки Fresh.
                                                                                    #   ALL — все склады Ozon.
    ) -> None:

        MPmethod.__init__(self, "POST", "/v2/analytics/stock_on_warehouses")
        self.payload : dict = {
            "limit": limit,
            "offset": offset,
            "warehouse_type": warehouse_type
        }

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            elif response.status_code == 429:
                time.sleep(10)
                self.make_request(session=session, **kwargs)
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
                    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.Postv2AnalyticsStockOnWarehousesResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session : MPsesh) -> Generator[Response, None, None]:
        """This one gets responses as a generator if the limit passes 1000"""
        check : int = 1
        i : int = 0
        while check:
            self.payload['offset'] = (i * 1_000)
            with session.post(self.url, json=self.payload) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    check = (len(response.json()['result']['rows']) // 1_000)
                    i += 1
                    yield response
                else:
                    print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}")

    def process_to_db(self, session : MPsesh) -> None:
        """"""
        stock_on_warehouses_updater = DBv2AnalyticsStockOnWarehousesUpdater(client_session=session)
        for chunk in self.get_chunks(session=session):
            for stock_on_warehouses_entry in chunk.json()['result']['rows']:
                stock_on_warehouses_updater.refresh(stock_on_warehouses_schema_=schemas.analyticsStockOnWarehouseResultRows(**stock_on_warehouses_entry))

        print(bcolors.OKBLUE + f"Successfully transitioned analytics stock on warehouses to the db for {session.supplier.name}" + bcolors.ENDC)


class PostProductInfoDiscounted(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        discounted_skus : list[str] = None
    ) -> None:

        MPmethod.__init__(self, "GET", "/v1/product/info/discounted")
        self.payload : dict = {
            "discounted_skus" : discounted_skus
        }

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
                    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.PostProductInfoDiscounted(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched discounted skus, adding them to the DB"""
        response: Response = self.make_request(session=session)
        for disc_sku in response.json()['items']:
            original_sku_in_db: ProductSource = db_session.query(ProductSource).filter_by(sku=disc_sku['sku']).first()
            if not original_sku_in_db:
                print(
                    bcolors.FAIL,
                    f"IN DB: Couldn't find this sku for discounted sku - {disc_sku['sku']}",
                    bcolors.ENDC
                )
                return -1
            prod_id_in_db: int = original_sku_in_db.product_id
            disc_sku_to_add: ProductSource = ProductSource(
                product_id=prod_id_in_db,
                is_enabled=True,
                sku=disc_sku['discounted_sku'],
                source='discounted'
            )
            try:
                db_session.add(disc_sku_to_add)
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()



class GetPerfCampaign(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        campaignIds : list[str] = None,                                
        advObjectType : str = None,
        state : str = None
    ) -> None:

        MPmethod.__init__(self, "GET", "/api/client/campaign", api_engine='performance')
        self.payload : dict = {
            "campaignIds" : campaignIds,
            "advObjectType" : advObjectType,
            "state" : state
        }

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.get(self.url, params=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
                    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.GetPerfCampaign(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched fbs returns list for a given supplier"""
        def process_general(dict_entry : dict, session : MPsesh) -> None:
            """processing general campaign info"""
            camp_in_db : Campaigns = db_session.query(Campaigns).filter_by(id=dict_entry['id']).first()
            if camp_in_db:
                camp_in_db.state = dict_entry['state']
                camp_in_db.updated_at = dict_entry['updatedAt']
                camp_in_db.budget = int(dict_entry['budget'][:-6]) if dict_entry['budget'] != '0' else 0
                camp_in_db.daily_budget = int(dict_entry['dailyBudget'][:-6]) if dict_entry['dailyBudget'] != '0' else 0
                if dict_entry['toDate']:
                    camp_in_db.to_date = dict_entry['toDate']
                    
                try:
                    db_session.commit()
                except exc.IntegrityError as e:
                    print('Committing failed -> ', e)
                    db_session.rollback()
                return 0

            camp_model : Campaigns = Campaigns(
                supplier_id=session.supplier.id,
                id=dict_entry['id'],
                title=dict_entry['title'],
                state=dict_entry['state'],
                adv_object_type=dict_entry['advObjectType'],
                from_date=dict_entry['fromDate'] if dict_entry['fromDate'] else dict_entry['createdAt'],
                to_date=dict_entry['toDate'] if dict_entry['toDate'] else None,
                budget=int(dict_entry['budget'][:-6]) if dict_entry['budget'] != '0' else 0,
                daily_budget=int(dict_entry['dailyBudget'][:-6]) if dict_entry['dailyBudget'] != '0' else 0,
                created_at=dict_entry['createdAt'],
                updated_at=dict_entry['updatedAt']
            )
            db_session.add(camp_model)
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback() 
            if dict_entry['placement']:
                for placement_entry in dict_entry['placement']:
                    if isinstance(placement_entry, str):
                        camp_placement_in_db : CampaignPlacement = (
                            db_session
                                .query(CampaignPlacement)
                                .filter_by(campaign_id=dict_entry['id'], placement=placement_entry)
                                .first()
                        )
                        if camp_placement_in_db:
                            continue
                        db_session.add(
                            CampaignPlacement(
                                    campaign_id=dict_entry['id'],
                                    placement=placement_entry
                                )
                        )
                        try:
                            db_session.commit()
                        except exc.IntegrityError as e:
                            print('Committing failed -> ', e)
                            db_session.rollback()

        for campaign_entry in self.make_request(session=session).json()['list']:
            process_general(campaign_entry, session=session)


class GetPerfCampaignObjects(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        campaignId : str = None
    ) -> None:

        self.payload : dict = {
            "campaignId" : campaignId
        }
        MPmethod.__init__(self, "GET", "/api/client/campaign/{}/objects", api_engine='performance')

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.get(self.url.format(self.payload['campaignId']), params=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
                    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.GetPerfCampaignObjects(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched fbs returns list for a given supplier"""
        RULES : dict = {
            'BOOSTING_SKU' : 'sku',
            'SKU' : 'sku',
            'BANNER' : 'empty',
            'SIS' : 'empty',
            'BRAND_SHELF' : 'object',
            'ACTION' : 'object',
            'ACTION_CAS' : 'object',
            'SEARCH_PROMO' : 'empty',
            'EXTERNAL_GOOGLE' : 'empty',
            'VIDEO_BANNER' : 'empty',
            'PROMO_PACKAGE' : 'empty',
            'PROMO_PACKAGE_SERVICE' : 'empty',
            'PROMO_PACKAGE_SERVICE_MANUAL_BILLING' : 'empty'
        }

        target_camps : list[Tuple[str, str]] = [
            (str(camp.id), camp.adv_object_type) for camp in
            db_session.query(Campaigns).filter(
                    Campaigns.supplier_id == session.supplier.id,
                    Campaigns.state.not_in(['CAMPAIGN_STATE_ARCHIVED', 'CAMPAIGN_STATE_FINISHED'])          # TODO: maybe delete or add states for better performance
                ).all()
        ]

        for id_, adv_obj_type in target_camps:
            try:
                ad_objects : dict = self.make_request(session=session, **{"campaignId" : id_}).json()['list']
                if ad_objects:
                    for ad_object_ in ad_objects:
                        ad_object_in_db : CampaignObjects = db_session.query(CampaignObjects).filter_by(campaign_id=id_, ad_object=ad_object_['id']).first()
                        if ad_object_in_db:
                            continue
                        ad_object_to_db : CampaignObjects = CampaignObjects(campaign_id=id_, ad_object=ad_object_['id'])
                        if adv_obj_type in ['SKU', 'BOOSTING_SKU']:
                            sku_in_db : ProductSource = db_session.query(ProductSource).filter_by(sku=ad_object_['id']).first()
                            if sku_in_db:
                                ad_object_to_db.sku = ad_object_['id']
                            else:
                                print(
                                    bcolors.FAIL,
                                    f"Couldn't find this sku {ad_object_['id']} in the DB, as for an object of this campaign - {id_}",
                                    bcolors.ENDC
                                )
                        db_session.add(ad_object_to_db)
                        try:
                            db_session.commit()
                        except exc.IntegrityError as e:
                            print('Committing failed -> ', e)
                            db_session.rollback()

            except AttributeError:
                print(
                    bcolors.FAIL + f"This campaign {id_} with type {adv_obj_type} hasn't been found, or request broke down" + bcolors.ENDC
                )
            continue
        

class PostPerfStatistics(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        campaigns : list[str] = None,
        from_: date = None,                  # 2019-08-24T14:15:22Z format
        to_: date = None,
        dateFrom: date = None,
        dateTo: date = None,
        groupBy: str = 'NO_GROUP_BY'                 #  "NO_GROUP_BY" "DATE" "START_OF_WEEK" "START_OF_MONTH"
    ) -> None:

        if (not from_) and (not to_):
            from_ = (date.today() - timedelta(2))
            to_ = (date.today() - timedelta(1))
        else:
            from_ = from_
            to_ = to_
        
        self.payload : dict = {
            "campaigns" : campaigns,
            "from" : from_.strftime('%Y-%m-%dT00:00:00.00Z'),
            "to" : to_.strftime('%Y-%m-%dT00:00:00.00Z'),
            "dateFrom" : from_.strftime('%Y-%m-%d'),
            "dateTo" : to_.strftime('%Y-%m-%d'),
            "groupBy" : groupBy
        }
        MPmethod.__init__(self, "POST", "/api/client/statistics", api_engine='performance')

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content.decode('utf-8')}")
                return response
                    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.PostPerfStatistics(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched fbs returns list for a given supplier"""
        pass


class GetPerfStatisticsStatus(MPmethod):
    """Cтатус отчёта по статистике рекламной компании по идентификатору задания (асинхронное) на получение отчета.
    идентификатор - UUID"""
    def __init__(self, UUID: UUID4) -> None:
        self.payload : dict = {"UUID" : UUID}
        MPmethod.__init__(self, "GET", "/api/client/statistics/{}", api_engine='performance')

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.get(self.url.format(self.payload['UUID'])) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
                    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.GetPerfStatisticsStatus(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())


class GetPerfStatisticsList(MPmethod):
    """Метод для получения списка отчётов, которые сгенерированы сервисными аккаунтами."""
    def __init__(self, page: int = 1, page_size: int = 100) -> None:
        self.payload : dict = {
            "page" : page,
            "pageSize" : page_size
        }
        MPmethod.__init__(self, "GET", "/api/client/statistics/list", api_engine='performance')

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.get(self.url, params=self.payload) as response:
            if response.status_code == 200:
                # self.validate_response(response=response)
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
                    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.GetPerfStatisticsStatus(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())


class GetPerfStatisticsReport(MPmethod):
    """Получить отчёты - При успешном запросе отчёт в формате CSV можно скачать с помощью относительный ссылки из поля contentDisposition.
    Формат отчёта в ответе указан в поле contentType. Формат зависит от того, сколько кампаний в поле campaigns исходного запроса:
        CSV — если в списке одна кампания.
        ZIP архив — если в списке несколько кампаний. Каждый файл соответствует одной кампании из списка.
    Имя файла вида <идентификатор кампании>.csv."""
    def __init__(self, UUID: UUID4) -> None:
        self.payload : dict = {"UUID" : UUID}
        MPmethod.__init__(self, "GET", "/api/client/statistics/report", api_engine='performance')

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.get(self.url, params=self.payload) as response:
            if response.status_code == 200:
                # self.validate_response(response=response)
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
                return response
                    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.GetPerfStatisticsReport(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())


class GetPerfCampaignProducts(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        campaignId : str = None
    ) -> None:

        self.payload : dict = {
            "campaignId" : campaignId
        }
        MPmethod.__init__(self, "GET", "/api/client/campaign/{}/products", api_engine='performance')

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.get(self.url.format(self.payload['campaignId']), params=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
                    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.GetPerfCampaignProducts(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def fetch_camps(self, session: MPsesh) -> list[str]:
        """Fetches sku campaigns to process"""
        campaigns: list[Campaigns] = (
            db_session
                    .query(Campaigns)
                    .filter(
                        Campaigns.supplier_id == session.supplier.id, 
                        Campaigns.adv_object_type == 'SKU', 
                        Campaigns.state == 'CAMPAIGN_STATE_RUNNING'                 # FIXME : maybe add CAMPAIGN_STATE_INACTIVE
                            )
                    .all()
        )
        if campaigns:
            campaigns: list[str] = [str(cmp.id) for cmp in campaigns]
            return campaigns
        print(f"There are no active SKU campaigns for this supplier {session.supplier.name}")
        return False

    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched SKU campaigns to extract their skus/phrases and stop words"""
        def process_sku(campaign_id: str, sku_entry: dict[str]) -> None:
            """processes each sku entry"""
            def process_stopwords(stopword_: str, sku_entry_: dict) -> CampaignProductStopWords:
                """processes phrases"""
                stopw_in_db: CampaignProductStopWords = (
                db_session
                    .query(CampaignProductStopWords)
                    .filter_by(
                        campaign_id=campaign_id,
                        sku=sku_entry_['sku'],
                        stop_word=stopword_
                    )
                        .first()
                )
                if stopw_in_db:
                    return False

                camp_stopw_to_add: CampaignProductStopWords = CampaignProductStopWords(
                    campaign_id=campaign_id,
                    sku=sku_entry_['sku'],
                    stop_word=stopword_
                )
                return camp_stopw_to_add
            
            def process_phrase(phrase_entry: dict, sku_entry_: dict) -> CampaignProductPhrases:
                """processes phrases"""
                camp_phrase_in_db: CampaignProductPhrases = (
                db_session
                    .query(CampaignProductPhrases)
                    .filter_by(
                        campaign_id=campaign_id,
                        sku=sku_entry_['sku'],
                        phrase=phrase_entry['phrase']
                    )
                        .first()
                )
                if camp_phrase_in_db:
                    camp_phrase_in_db.bid = (int(phrase_entry['bid'][:-6]) if (not phrase_entry['bid'] == '' and not phrase_entry['bid'] == '0') else 0)
                    camp_phrase_in_db.relevance_status = phrase_entry['relevanceStatus']
                    return False

                camp_phrase_to_add: CampaignProductPhrases = CampaignProductPhrases(
                    campaign_id=campaign_id,
                    sku=sku_entry_['sku'],
                    phrase=phrase_entry['phrase'],
                    bid=(int(phrase_entry['bid'][:-6]) if (not phrase_entry['bid'] == '' and not phrase_entry['bid'] == '0') else 0),
                    relevance_status=phrase_entry['relevanceStatus']
                )
                return camp_phrase_to_add
            

            # main part
            camp_sku_in_db: CampaignProducts = (
                db_session
                    .query(CampaignProducts)
                    .filter_by(
                        campaign_id=campaign_id,
                        sku=sku_entry['sku']
                    )
                    .first()
            )
            if camp_sku_in_db:
                camp_sku_in_db.bid = (int(sku_entry['bid'][:-6]) if (not sku_entry['bid'] == '' and not sku_entry['bid'] == '0') else 0)
                camp_sku_in_db.group_id = (int(sku_entry['groupId']) if (not sku_entry['groupId'] == '0' and not sku_entry['groupId'] == '') else None)
            else:
                camp_sku_to_add: CampaignProducts = CampaignProducts(
                    campaign_id=campaign_id,
                    sku=sku_entry['sku'],
                    bid=(int(sku_entry['bid'][:-6]) if (not sku_entry['bid'] == '' and not sku_entry['bid'] == '0') else 0),
                    group_id=(int(sku_entry['groupId']) if (not sku_entry['groupId'] == '0' and not sku_entry['groupId'] == '') else None)
                )
                db_session.add(camp_sku_to_add)
                try:
                    db_session.commit()
                except exc.IntegrityError as e:
                    print('Committing failed -> ', e)
                    db_session.rollback()
            
            for phrase_ in sku_entry['phrases']:
                if phrase_to_add := process_phrase(phrase_entry=phrase_, sku_entry_=sku_entry):
                    db_session.add(phrase_to_add)
            
            for stopword_ in sku_entry['stopWords']:
                if stopword_to_add := process_stopwords(stopword_=stopword_, sku_entry_=sku_entry):
                    db_session.add(stopword_to_add)
            try:
                db_session.commit()
            except exc.IntegrityError as e:
                print('Committing failed -> ', e)
                db_session.rollback()

        target_camps: list[str] = self.fetch_camps(session=session)
        # check whether it has SKU campaigns or not
        if isinstance(target_camps, bool):
            return False

        for campaign_ in target_camps:
            if not target_camps:
                return False
            response = self.make_request(session=session, **{"campaignId" : campaign_}).json()['products']
            for sku_ in response:
                process_sku(campaign_id=campaign_, sku_entry=sku_)


class PostPerfSearchPromoProducts(MPmethod):
    """ #fill this
    """
    def __init__(
        self,
        campaignId : str = None,
        page: int = 0,
        page_size: int = 1000
    ) -> None:

        self.payload : dict = {
            "campaignId" : campaignId,
            "page" : page,
            "pageSize" : page_size,
        }
        MPmethod.__init__(self, "POST", "/api/client/campaign/{}/search_promo/products", api_engine='performance')

    def make_request(self, session : MPsesh, **kwargs) -> Response:
        self.payload.update(**kwargs)
        with session.post(self.url.format(self.payload['campaignId']), json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}")
                    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            schemas.PostPerfSearchPromoProducts(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def fetch_camps(self, session: MPsesh) -> list[str]:
        """Fetches sku campaigns to process"""
        campaigns: list[Campaigns] = (
            db_session
                    .query(Campaigns)
                    .filter(
                        Campaigns.supplier_id == session.supplier.id, 
                        Campaigns.adv_object_type == 'SEARCH_PROMO', 
                        Campaigns.state == 'CAMPAIGN_STATE_RUNNING'                 # FIXME : maybe add CAMPAIGN_STATE_INACTIVE
                            )
                    .all()
        )
        if campaigns:
            campaigns: list[str] = [str(cmp.id) for cmp in campaigns]
            return campaigns
        print(f"There are no active SKU campaigns for this supplier {session.supplier.name}")
        return False

    def process_to_db(self, session : MPsesh) -> None:
        """Processing fetched search promo campaigns to extract their skus/bids and views"""
        def process_entry(sku_entry: dict, campaign_id: str) -> None:
            """processes each entry"""
            # main part
            promo_sku_in_db: CampaignSearchPromoProducts = (
                db_session
                    .query(CampaignSearchPromoProducts)
                    .filter_by(
                        campaign_id=campaign_id,
                        sku=sku_entry['sku']
                    )
                    .first()
            )
            if promo_sku_in_db:
                promo_sku_in_db.bid = round(float(sku_entry['bid']), 2)
                promo_sku_in_db.bid_price = round(float(sku_entry['bidPrice']), 2)
                promo_sku_in_db.previous_week_views = int(sku_entry['views']['previousWeek'])
                promo_sku_in_db.this_week_views = int(sku_entry['views']['thisWeek'])
                promo_sku_in_db.visibility_index = int(sku_entry['visibilityIndex'].rstrip('+'))
                promo_sku_in_db.prev_visibility_index = int(sku_entry['previousVisibilityIndex'].rstrip('+'))
            else:
                promo_sku_to_add: CampaignSearchPromoProducts = CampaignSearchPromoProducts(
                    campaign_id=campaign_id,
                    sku=sku_entry['sku'],
                    bid = round(float(sku_entry['bid']), 2),
                    bid_price = round(float(sku_entry['bidPrice']), 2),
                    previous_week_views = int(sku_entry['views']['previousWeek']),
                    this_week_views = int(sku_entry['views']['thisWeek']),
                    visibility_index = int(sku_entry['visibilityIndex'].rstrip('+')),
                    prev_visibility_index = int(sku_entry['previousVisibilityIndex'].rstrip('+'))
                )
                db_session.add(promo_sku_to_add)
                try:
                    db_session.commit()
                except exc.IntegrityError as e:
                    print('Committing failed -> ', e)
                    db_session.rollback()
            

        target_camps: list[str] = self.fetch_camps(session=session)

        for campaign_ in target_camps:
            if not target_camps:
                return False
            response = self.make_request(session=session, **{"campaignId" : campaign_}).json()
            if int(response['total']) >= 1_000:
                print(f"This search promo campaign's product list exceeds the limit, check it! -> {campaign_}")
            for sku_ in response['products']:
                process_entry(campaign_id=campaign_, sku_entry=sku_)