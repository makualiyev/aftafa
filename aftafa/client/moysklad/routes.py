from abc import ABC
from abc import abstractmethod
from typing import Optional, Generator, Union


from requests.models import Response

from aftafa.client.moysklad.handlers import MPsesh
import aftafa.client.moysklad.schemas as sc
import aftafa.client.moysklad.models as md
from aftafa.client.moysklad.crud import (
    GroupDBWriter,
    EmployeeDBWriter,
    StoreDBWriter,
    OrganizationDBWriter,
    CounterpartyDBWriter,
    SalesChannelDBWriter,
    DocumentStateDBWriter,
    ContractDBWriter,
    ProductFolderDBWriter,
    ProductDBWriter,
    ProductBarcodeDBWriter,
    ProductAttributeDBWriter,
    EntityAttrDBWriter,
    CustomEntityDBWriter,
    CustomEntityMemberDBWriter
)

# class GetRequest(ABC):
#     """
#     Abstract class for GET requests.

#     Parameters
#     ----------
#     names : array-like or None
#         An array containing a list of the names used for the output DataFrame.
#     """
#     base_url = 

#     @abstractmethod
#     def get(self) -> Response:

class GetEntityGroup:
    """
    Getting entities given.

    Parameters
    ----------
    entity : str
    """
    def __init__(self, sesh: MPsesh) -> None:
        self.sesh = sesh
        self.container = []

    def get_entities(self) -> None:
        response: Response = self.sesh.make_request('GET', '/entity/group')
        group_writer: GroupDBWriter = GroupDBWriter()
        for group_repr in response.json()['rows']:
            group_model: md.Group = group_writer.prep_model(schema_=sc.GroupEntity(**group_repr))
            if group_writer.check_integrity(group_model=group_model):
                group_writer.update(group_model)
                continue
            group_writer.create(group_model)
            

class GetEntityEmployee:
    """
    Getting entities given.

    Parameters
    ----------
    entity : str
    """
    def __init__(self, sesh: MPsesh) -> None:
        self.sesh = sesh
        self.container = []

    def get_entities(self) -> None:
        response: Response = self.sesh.make_request('GET', '/entity/employee')
        empl_writer: EmployeeDBWriter = EmployeeDBWriter()
        for empl_repr in response.json()['rows']:
            empl_model: md.Group = empl_writer.prep_model(schema_=sc.EmployeeEntity(**empl_repr))
            if empl_writer.check_integrity(empl_model=empl_model):
                empl_writer.update(empl_model)
                continue
            empl_writer.create(empl_model)
        return 0

    
class GetEntityStore:
    """
    Getting entities given.

    Parameters
    ----------
    entity : str
    """
    def __init__(self, sesh: MPsesh) -> None:
        self.sesh = sesh
        self.container = []

    def get_entities(self) -> None:
        response: Response = self.sesh.make_request('GET', '/entity/store')
        store_writer: StoreDBWriter = StoreDBWriter()
        for store_repr in response.json()['rows']:
            store_model: md.Group = store_writer.prep_model(schema_=sc.StoreEntity(**store_repr))
            if store_writer.check_integrity(store_model=store_model):
                store_writer.update(store_model)
                continue
            store_writer.create(store_model)
        return 0


class GetEntityOrganization:
    """
    Getting entities given.

    Parameters
    ----------
    entity : str
    """
    def __init__(self, sesh: MPsesh) -> None:
        self.sesh = sesh
        self.container = []

    def get_entities(self) -> None:
        response: Response = self.sesh.make_request('GET', '/entity/organization')
        organization_writer: OrganizationDBWriter = OrganizationDBWriter()
        for organization_repr in response.json()['rows']:
            organization_model: md.Organization = organization_writer.prep_model(schema_=sc.OrganizationEntity(**organization_repr))
            if organization_writer.check_integrity(organization_model=organization_model):
                organization_writer.update(organization_model)
                continue
            organization_writer.create(organization_model)
        return 0


class GetEntityCounterparty:
    """
    Getting entities given.

    Parameters
    ----------
    entity : str
    """
    def __init__(self, sesh: MPsesh) -> None:
        self.sesh = sesh
        self.container = []

    def get_entities(self) -> None:
        response: Response = self.sesh.make_request('GET', '/entity/counterparty')
        counterparty_writer: CounterpartyDBWriter = CounterpartyDBWriter()
        for counterparty_repr in response.json()['rows']:
            counterparty_model: md.Counterparty = counterparty_writer.prep_model(schema_=sc.CounterpartyEntity(**counterparty_repr))
            if counterparty_writer.check_integrity(counterparty_model=counterparty_model):
                counterparty_writer.update(counterparty_model)
                continue
            counterparty_writer.create(counterparty_model)
        return 0


class GetEntitySalesChannel:
    """
    Getting entities given.

    Parameters
    ----------
    entity : str
    """
    def __init__(self, sesh: MPsesh) -> None:
        self.sesh = sesh
        self.container = []

    def get_entities(self) -> None:
        response: Response = self.sesh.make_request('GET', '/entity/saleschannel')
        saleschannel_writer: SalesChannelDBWriter = SalesChannelDBWriter()
        for saleschannel_repr in response.json()['rows']:
            saleschannel_model: md.SalesChannel = saleschannel_writer.prep_model(schema_=sc.SalesChannelEntity(**saleschannel_repr))
            if saleschannel_writer.check_integrity(saleschannel_model=saleschannel_model):
                saleschannel_writer.update(saleschannel_model)
                continue
            saleschannel_writer.create(saleschannel_model)
        return 0


class GetEntityDocumentState:
    """
    Getting entities given.

    Parameters
    ----------
    entity : str
    """
    def __init__(self, sesh: MPsesh, entity: str) -> None:
        self.sesh = sesh
        self.entity = entity
        self.container = []

    def get_states(self) -> None:
        response: Response = self.sesh.make_request('GET', f'/entity/{self.entity}/metadata')
        doc_state_writer: DocumentStateDBWriter = DocumentStateDBWriter()
        for doc_state_repr in response.json()['states']:
            doc_state_model: md.DocumentState = doc_state_writer.prep_model(schema_=sc.DocumentStateEntity(**doc_state_repr))
            if doc_state_writer.check_integrity(doc_state_model=doc_state_model):
                doc_state_writer.update(doc_state_model)
                continue
            doc_state_writer.create(doc_state_model)
        return 0


class GetEntityContract:
    """
    Getting entities given.

    Parameters
    ----------
    entity : str
    """
    def __init__(self, sesh: MPsesh) -> None:
        self.sesh = sesh
        self.container = []

    def get_entities(self) -> None:
        response: Response = self.sesh.make_request('GET', '/entity/contract')
        contract_writer: ContractDBWriter = ContractDBWriter()
        for contract_repr in response.json()['rows']:
            contract_model: md.Contract = contract_writer.prep_model(schema_=sc.ContractEntity(**contract_repr))
            if contract_writer.check_integrity(contract_model=contract_model):
                contract_writer.update(contract_model)
                continue
            contract_writer.create(contract_model)
        return 0


class GetEntityProductFolder:
    """
    Getting entities given.

    Parameters
    ----------
    entity : str
    """
    def __init__(self, sesh: MPsesh) -> None:
        self.sesh = sesh
        self.container = []

    def get_entities(self) -> None:
        response: Response = self.sesh.make_request('GET', '/entity/productfolder')
        prod_folder_writer: ProductFolderDBWriter = ProductFolderDBWriter()
        for prod_folder_repr in response.json()['rows']:
            prod_folder_model: md.ProductFolder = prod_folder_writer.prep_model(schema_=sc.ProductFolderEntity(**prod_folder_repr))
            if prod_folder_writer.check_integrity(product_folder_model=prod_folder_model):
                prod_folder_writer.update(prod_folder_model)
                continue
            prod_folder_writer.create(prod_folder_model)
        return 0


class GetCustomEntity:
    """
    Getting entities given.

    Parameters
    ----------
    entity : str
    """
    def __init__(self, sesh: MPsesh, customentity_id: str) -> None:
        self.sesh = sesh
        self.customentity_id = customentity_id
        self.container = []

    def get_customentity(self) -> None:
        response: Response = self.sesh.make_request(
            'GET', 
            f'/context/companysettings/metadata/customEntities/{self.customentity_id}'
        )
        customentity_writer: CustomEntityDBWriter = CustomEntityDBWriter(customentity_id=self.customentity_id)
        
        customentity_model: md.CustomEntity = customentity_writer.prep_model(schema_=sc.CustomEntity(**response.json()))
        if customentity_writer.check_integrity(customentity_model=customentity_model):
            customentity_writer.update(customentity_model)
            return 0
        customentity_writer.create(customentity_model)
        return 0


class GetCustomEntityMember:
    """
    Getting entities given.

    Parameters
    ----------
    entity : str
    """
    def __init__(self, sesh: MPsesh, customentity_id: str) -> None:
        self.sesh = sesh
        self.customentity_id = customentity_id
        self.container = []

    def get_customentity_members(self) -> None:
        response: Response = self.sesh.make_request(
            'GET',
            f'/entity/customentity/{self.customentity_id}'
        )
        customentity_member_writer: CustomEntityMemberDBWriter = CustomEntityMemberDBWriter(
                                                        customentity_id=self.customentity_id
                                                    )
        
        for customentity_member_repr in response.json()['rows']:
            customentity_member_model: md.CustomEntityMember = customentity_member_writer.prep_model(
                schema_=sc.CustomEntityMember(**customentity_member_repr)
            )
            if customentity_member_writer.check_integrity(customentity_member_model=customentity_member_model):
                customentity_member_writer.update(customentity_member_model)
                continue
            customentity_member_writer.create(customentity_member_model)
        return 0


class GetEntityAttribute:
    """
    Getting entities given.

    Parameters
    ----------
    entity : str
    """
    def __init__(self, sesh: MPsesh, entity: str) -> None:
        self.sesh = sesh
        self.entity = entity
        self.container = []

    def get_attributes(self) -> None:
        response: Response = self.sesh.make_request('GET', f'/entity/{self.entity}/metadata/attributes')
        attribute_writer: EntityAttrDBWriter = EntityAttrDBWriter(entity_type=self.entity)
        for attribute_repr in response.json()['rows']:
            if attribute_repr['type'] == 'customentity':
                customentity_id: str = attribute_repr['customEntityMeta']['href'].split('/')[-1]
                GetCustomEntity(
                    customentity_id=customentity_id,
                    sesh=self.sesh
                ).get_customentity()
                GetCustomEntityMember(
                    customentity_id=customentity_id,
                    sesh=self.sesh
                ).get_customentity_members()
            else:
                customentity_id: Optional[str] = None
            attribute_model: md.EntityAttribute = attribute_writer.prep_model(
                schema_=sc.Attribute(**attribute_repr),
                customentity_id=customentity_id
            )
            if attribute_writer.check_integrity(attribute_model=attribute_model):
                attribute_writer.update(attribute_model)
                continue
            attribute_writer.create(attribute_model)
        return 0


class GetEntityProduct:
    """
    Getting entities given.

    Parameters
    ----------
    entity : str
    """
    def __init__(
        self,
        sesh: MPsesh,
        name: str = None,
        code: str = None,
        article: str = None
    ) -> None:
        self.sesh = sesh
        self.name = name
        self.code = code
        self.article = article
        self.params = {
            'limit': 1000,
            'offset': 0
        }
        self.container = []

    def get_chunks(self) -> Generator[Response, None, None]:
        
        check_: int = 1
        offset_: int = 0
        
        while check_:
            self.params.update({'offset': (offset_ * 1_000)})
            with self.sesh.make_request('GET', '/entity/product', **self.params) as response:
                if response.json()['meta']['size'] < response.json()['meta']['limit']:
                    check_ = 0
                    yield response
                elif not (((response.json()['meta']['size'] - response.json()['meta']['offset']) // 1_000) > 0):
                    check_ = 0
                    yield response
                else:
                    offset_ += 1
                    yield response

    def get_entities(self) -> None:
        # product_writer: ProductDBWriter = ProductDBWriter()
        # product_barcode_writer: ProductBarcodeDBWriter = ProductBarcodeDBWriter()
        db_writers = {
            'product': ProductDBWriter(),
            'product_barcode': ProductBarcodeDBWriter(),
            'product_attribute': ProductAttributeDBWriter()
        }

        def process_products(writers: dict[str, Union[ProductBarcodeDBWriter, ProductDBWriter]], product_repr: dict) -> bool:
            """ . """
            product_model_: md.Product = writers['product'].prep_model(schema_=sc.ProductEntity(**product_repr))
            product_barcode_models_: list[md.ProductBarcode] = writers['product_barcode'].prep_model(schema_=sc.ProductEntity(**product_repr))

            if writers['product'].check_integrity(product_model=product_model_):
                writers['product'].update(product_model_)
                for barcode_model_ in product_barcode_models_:
                    if writers['product_barcode'].check_integrity(product_barcode_model=barcode_model_):
                        writers['product_barcode'].update(barcode_model_)
                    else:
                        writers['product_barcode'].create(product_barcode_model=barcode_model_)
            else:
                writers['product'].create(product_model_)
                for barcode_model_ in product_barcode_models_:
                    writers['product_barcode'].create(product_barcode_model=barcode_model_)

        def process_product_attributes(
                        writers: dict[str, Union[ProductBarcodeDBWriter, ProductDBWriter]], product_repr: dict
                    ) -> bool:
            product_attribute_models_: list[md.ProductAttribute] = writers['product_attribute'].prep_model(schema_=sc.ProductEntity(**product_repr))

            for attribute_model_ in product_attribute_models_:
                if writers['product_attribute'].check_integrity(product_attribute_model=attribute_model_):
                    writers['product_attribute'].update(attribute_model_)
                else:
                    writers['product_attribute'].create(product_attribute_model=attribute_model_)



        for chunk in self.get_chunks():
            for product_repr in chunk.json()['rows']:
                process_products(writers=db_writers, product_repr=product_repr)
                process_product_attributes(writers=db_writers, product_repr=product_repr)

                # product_model_: md.Product = product_writer.prep_model(schema_=sc.ProductEntity(**product_repr))
                # if product_writer.check_integrity(product_model=product_model_):
                #     product_writer.update(product_model_)
                #     continue
                # product_writer.create(product_model_)
        # return 0

# if __name__ == '__main__':
#     GetEntityGroup(MPsesh()).get_groups()