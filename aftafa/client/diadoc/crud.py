from pathlib import Path
from datetime import datetime, timedelta
from typing import Any
import hashlib

from sqlalchemy import cast, Date, select
from requests import Response

from aftafa.client.diadoc.client import DiadocClient
from aftafa.client.diadoc.db import session as db_session, engine
from aftafa.client.diadoc.schema.document import Document as DocumentSchema
from aftafa.client.diadoc.schema.message import Message as MessageSchema
import aftafa.client.diadoc.model as diadoc_models


class DBDocumentUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(
        self,
        client_session: DiadocClient,
        db_session=db_session,
        db_engine=engine,
        extraction_ts=None
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session
        if extraction_ts:
            self.extraction_ts = extraction_ts
        else:
            self.extraction_ts = datetime.now()

    def prep_model(self, schema_: DocumentSchema) -> diadoc_models.Document:
        """prepares ORM model for a given schema"""

        req_fields: list[str] = [i for i in diadoc_models.Document.__dict__ if not i.startswith("_")]
        document_schema: dict[str, Any] = schema_.dict()
        document_schema['counteragent_id'] = 1
        document_schema['extracted_at'] = self.extraction_ts

        document_schema = {key: value for key, value in document_schema.items() if key in req_fields}

        return diadoc_models.Document(**document_schema)

    def check_integrity(self, prepped_model: diadoc_models.Document) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        document_model_queried: diadoc_models.Document = self.db_session.query(
            diadoc_models.Document
        ).filter(
            diadoc_models.Document.index_key == str(prepped_model.index_key)
        )
        if document_model_queried.count() > 1:
            print(
                f"This document entry {prepped_model.index_key} has duplicates"
            )
        document_item_in_db = document_model_queried.first()
        if document_item_in_db:
            return True
        return False

    def update(self, prepped_model: diadoc_models.Document) -> None:
        """Updates Product entity"""
        document_model_in_db: diadoc_models.Document = self.db_session.query(
            diadoc_models.Document
        ).filter(
            diadoc_models.Document.index_key == str(prepped_model.index_key)
        ).first()

        document_model_in_db.is_deleted = prepped_model.is_deleted
        document_model_in_db.is_test = prepped_model.is_test
        document_model_in_db.is_read = prepped_model.is_read
        document_model_in_db.packet_is_locked = prepped_model.packet_is_locked
        document_model_in_db.revocation_status = prepped_model.revocation_status

        self.db_session.commit()

    def create(self, prepped_model: diadoc_models.Document) -> None:
        """Creates Order entity"""
        self.db_session.add(prepped_model)
        self.db_session.commit()

    def refresh(self, document_schema: dict) -> None:
        prepped_model_ = self.prep_model(schema_=document_schema)
        if self.check_integrity(prepped_model=prepped_model_):
            self.update(prepped_model=prepped_model_)
            return None
        self.create(prepped_model=prepped_model_)
        return None
    

class DBMessageUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(
        self,
        client_session: DiadocClient,
        db_session=db_session,
        db_engine=engine,
        extraction_ts=None
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session
        if extraction_ts:
            self.extraction_ts = extraction_ts
        else:
            self.extraction_ts = datetime.now()

    def prep_model(self, schema_: MessageSchema) -> diadoc_models.Message:
        """prepares ORM model for a given schema"""

        req_fields: list[str] = [i for i in diadoc_models.Message.__dict__ if not i.startswith("_")]
        message_schema: dict[str, Any] = schema_.dict()
        message_schema['extracted_at'] = self.extraction_ts

        message_schema = {key: value for key, value in message_schema.items() if key in req_fields}

        return diadoc_models.Message(**message_schema)

    def check_integrity(self, prepped_model: diadoc_models.Message) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        message_model_queried: diadoc_models.Message = self.db_session.query(
            diadoc_models.Message
        ).filter(
            diadoc_models.Message.message_id == str(prepped_model.message_id)
        )
        if message_model_queried.count() > 1:
            print(
                f"This message entry {prepped_model.message_id} has duplicates"
            )
        message_item_in_db = message_model_queried.first()
        if message_item_in_db:
            return True
        return False

    def update(self, prepped_model: diadoc_models.Message) -> None:
        """Updates Product entity"""
        message_model_in_db: diadoc_models.Message = self.db_session.query(
            diadoc_models.Message
        ).filter(
            diadoc_models.Message.message_id == str(prepped_model.message_id)
        ).first()

        message_model_in_db.is_draft = prepped_model.is_draft
        message_model_in_db.draft_is_locked = prepped_model.draft_is_locked
        message_model_in_db.draft_is_recycled = prepped_model.draft_is_recycled
        message_model_in_db.is_deleted = prepped_model.is_deleted
        message_model_in_db.is_test = prepped_model.is_test
        message_model_in_db.is_internal = prepped_model.is_internal
        message_model_in_db.is_proxified = prepped_model.is_proxified
        message_model_in_db.is_reusable = prepped_model.is_reusable
        message_model_in_db.packet_is_locked = prepped_model.packet_is_locked

        self.db_session.commit()

    def create(self, prepped_model: diadoc_models.Message) -> None:
        """Creates Order entity"""
        self.db_session.add(prepped_model)
        self.db_session.commit()

    def populate_message_entities(self, schema_: MessageSchema) -> None:
        message_schema: dict[str, Any] = schema_.dict()

        if message_schema.get("entities"):
            message_entity_updater: DBMessageEntityUpdater = DBMessageEntityUpdater(client_session=self.sesh, extraction_ts=self.extraction_ts)
            for message_entity in message_schema.get("entities"):
                message_entity_updater.refresh(
                    message_entity_schema=message_entity,
                    message_id=message_schema['message_id']
                )

    def refresh(self, message_schema: dict) -> None:
        prepped_model_ = self.prep_model(schema_=message_schema)
        if self.check_integrity(prepped_model=prepped_model_):
            self.update(prepped_model=prepped_model_)
            self.populate_message_entities(schema_=message_schema)
            return None
        self.create(prepped_model=prepped_model_)
        self.populate_message_entities(schema_=message_schema)
        return None
    
    def get_message_ids(self, date_from: str | None) -> list[str] | None:
        if not date_from:
            date_from = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
        date_from = datetime.strptime(date_from, '%d.%m.%Y').strftime('%Y-%m-%d')
            


        message_ids_in_db: list[diadoc_models.Document] = self.db_session.query(diadoc_models.Document).filter(
            cast(diadoc_models.Document.creation_timestamp, Date) >= date_from
        ).all()

        if not message_ids_in_db:
            print(f"No messages for this date {date_from.strftime('%d.%m.%Y')}")
            return None

        message_ids_in_db: list[str] = [message_.message_id for message_ in message_ids_in_db]
        return message_ids_in_db
        
    

class DBMessageEntityUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(
        self,
        client_session: DiadocClient,
        db_session=db_session,
        db_engine=engine,
        extraction_ts=None
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session
        if extraction_ts:
            self.extraction_ts = extraction_ts
        else:
            self.extraction_ts = datetime.now()

    def prep_model(self, schema_: dict, message_id: str) -> diadoc_models.MessageEntity:
        """prepares ORM model for a given schema"""

        req_fields: list[str] = [i for i in diadoc_models.MessageEntity.__dict__ if not i.startswith("_")]
        
        # if not isinstance(schema_, EntitySchema):
        #     message_entity_schema = EntitySchema(**schema_)
        message_entity_schema: dict[str, Any] = schema_
        
        message_entity_schema['message_id'] = message_id
        if message_entity_schema['content']:
            message_entity_schema['content_size'] = message_entity_schema['content'].get('Size')
        message_entity_schema['extracted_at'] = self.extraction_ts

        message_entity_schema = {key: value for key, value in message_entity_schema.items() if key in req_fields}

        return diadoc_models.MessageEntity(**message_entity_schema)

    def check_integrity(self, prepped_model: diadoc_models.MessageEntity) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        message_entity_model_queried: diadoc_models.MessageEntity = self.db_session.query(
            diadoc_models.MessageEntity
        ).filter(
            diadoc_models.MessageEntity.message_id == str(prepped_model.message_id),
            diadoc_models.MessageEntity.entity_id == str(prepped_model.entity_id)
        )
        if message_entity_model_queried.count() > 1:
            print(
                f"This message entity entry {prepped_model.entity_id} has duplicates"
            )
        message_entity_item_in_db = message_entity_model_queried.first()
        if message_entity_item_in_db:
            return True
        return False

    def update(self, prepped_model: diadoc_models.MessageEntity) -> None:
        """Updates Product entity"""
        message_entity_model_in_db: diadoc_models.MessageEntity = self.db_session.query(
            diadoc_models.MessageEntity
        ).filter(
            diadoc_models.MessageEntity.message_id == str(prepped_model.message_id),
            diadoc_models.MessageEntity.entity_id == str(prepped_model.entity_id)
        ).first()

        message_entity_model_in_db.need_receipt = prepped_model.need_receipt
        message_entity_model_in_db.need_recipient_signature = prepped_model.need_recipient_signature
        message_entity_model_in_db.is_approvement_signature = prepped_model.is_approvement_signature
        message_entity_model_in_db.is_encrypted_content = prepped_model.is_encrypted_content

        self.db_session.commit()

    def create(self, prepped_model: diadoc_models.MessageEntity) -> None:
        """Creates Order entity"""
        self.db_session.add(prepped_model)
        self.db_session.commit()


    def refresh(self, message_entity_schema: dict, message_id: str) -> None:
        prepped_model_ = self.prep_model(schema_=message_entity_schema, message_id=message_id)
        if self.check_integrity(prepped_model=prepped_model_):
            self.update(prepped_model=prepped_model_)
            return None
        self.create(prepped_model=prepped_model_)
        return None
    

class DBEntityContentUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(
        self,
        client_session: DiadocClient,
        file_destination: str,
        db_session=db_session,
        db_engine=engine,
        extraction_ts=None
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session
        if extraction_ts:
            self.extraction_ts = extraction_ts
        else:
            self.extraction_ts = datetime.now()
        if self._init_file_destination(file_destination):
            self.file_destination = file_destination
        else:
            raise ValueError('Not right file destination')


    def _init_file_destination(self, file_destination: str) -> bool:
        folder_path = Path(file_destination)
        if not folder_path.exists():
            print(f"Please enter a valid path to file destination, not this -> {file_destination}")
            return False
        if not folder_path.is_dir():
            print(f"Please enter a valid `folder` path to file destination, not this -> {file_destination}")
            return False
        return True


    def get_entities_for_content(self, date_from: str | None) -> list[dict[str, str]] | None:
        if not date_from:
            date_from = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
        date_from = datetime.strptime(date_from, '%d.%m.%Y').strftime('%Y-%m-%d')
        
        stmt = (
                select(diadoc_models.MessageEntity)
                    .join(diadoc_models.Message, diadoc_models.MessageEntity.message_id == diadoc_models.Message.message_id)
                    .join(diadoc_models.Document, diadoc_models.Message.message_id == diadoc_models.Document.message_id)
                    .filter(
                        diadoc_models.Document.creation_timestamp >= date_from,
                        diadoc_models.MessageEntity.entity_type == 'Attachment',
                        diadoc_models.MessageEntity.attachment_type == 'Nonformalized'
                    )
            )

        enitity_ids_in_db: list[diadoc_models.MessageEntity] = self.db_session.execute(stmt).all()

        if not enitity_ids_in_db:
            print(f"No entities for this date {date_from.strftime('%d.%m.%Y')}")
            return None

        enitity_ids_in_db = [message_entity[0] for message_entity in enitity_ids_in_db]
        enitity_ids_in_db: list[dict[str, str]] = [
            {
                'message_id': message_entity.message_id,
                'entity_id': message_entity.entity_id,
                'file_name': message_entity.file_name
            }
            for message_entity in enitity_ids_in_db
        ]
        return enitity_ids_in_db
    

    def save_to_file(self, response: Response, entity_entry: dict[str, str]) -> None:
        folder_path = Path(self.file_destination)
        init_file_name: str = Path(entity_entry['entity_id'])
        file_name: str = Path(entity_entry['file_name'])

        with open((folder_path / ''.join([init_file_name.stem, file_name.suffix])), 'wb') as f:
            f.write(response.content)

        file_checksum = hashlib.md5(
                            open(
                                (folder_path / ''.join([init_file_name.stem, file_name.suffix])),
                                'rb'
                            ).read()
                        ).hexdigest()
        
        # (folder_path / ''.join([init_file_name.stem, file_name.suffix])).rename(
        #         folder_path / f"{file_name.stem}_[{file_checksum}]{file_name.suffix}"
        # )

        # os.rename(
        #     (folder_path / ''.join([init_file_name.stem, file_name.suffix])),
        #     (folder_path / f"{file_name.stem}_[{file_checksum}]{file_name.suffix}")
        # )

        return None


    

    # def create(self, prepped_model: diadoc_models.MessageEntity) -> None:
    #     """Creates Order entity"""
    #     self.db_session.add(prepped_model)
    #     self.db_session.commit()


    # def refresh(self, message_entity_schema: dict, message_id: str) -> None:
    #     prepped_model_ = self.prep_model(schema_=message_entity_schema, message_id=message_id)
    #     if self.check_integrity(prepped_model=prepped_model_):
    #         self.update(prepped_model=prepped_model_)
    #         return None
    #     self.create(prepped_model=prepped_model_)
    #     return None