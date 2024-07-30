import sqlalchemy as sa

from aftafa.client.diadoc.db import Base, DEFAULT_SCHEMA


class Counteragent(Base):
    """
    
    """
    __tablename__ = "counteragent"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    org_guid = sa.Column(sa.String(255), nullable=False)
    full_name = sa.Column(sa.String(255), nullable=False)
    short_name = sa.Column(sa.String(255), nullable=False)
    box_id = sa.Column(sa.String(255), unique=True, nullable=False)
    slug = sa.Column(sa.String(255), nullable=False)


# Counteragent(
#     org_guid='f7445b7a-c4a5-42a3-beda-75fee639d347',
#     full_name='Общество с ограниченной ответственностью "Склад А"',
#     short_name='ООО "СКЛАД А"',
#     box_id='6817822838e145068b2f26528c461a7b@diadoc.ru',
#     slug='Sklad_A'
# )

class Document(Base):
    """
    """
    __tablename__ = "document"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    counteragent_id = sa.Column(sa.Integer, sa.ForeignKey(Counteragent.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    counteragent_box_id = sa.Column(sa.String(255), sa.ForeignKey(Counteragent.box_id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    index_key = sa.Column(sa.String(255), unique=True, index=True, nullable=False)
    message_id = sa.Column(sa.String(255), nullable=False)
    entity_id = sa.Column(sa.String(255), nullable=False)

    document_type = sa.Column(sa.String(255), nullable=False)
    creation_timestamp_ticks = sa.Column(sa.String(255))
    creation_timestamp = sa.Column(sa.String(255))
    file_name = sa.Column(sa.String(255))
    message_id_guid = sa.Column(sa.String(255))
    entity_id_guid = sa.Column(sa.String(255))
    
    document_date = sa.Column(sa.String(255))
    document_number = sa.Column(sa.String(255))
    type_named_id = sa.Column(sa.String(255))
    function = sa.Column(sa.String(255))
    title = sa.Column(sa.String(255))

    is_deleted = sa.Column(sa.Boolean, nullable=True)
    is_test = sa.Column(sa.Boolean, nullable=True)
    has_custom_print_form = sa.Column(sa.Boolean, nullable=True)
    is_encrypted_content = sa.Column(sa.Boolean, nullable=True)
    is_read = sa.Column(sa.Boolean, nullable=True)
    packet_is_locked = sa.Column(sa.Boolean, nullable=True)
    workflow_id = sa.Column(sa.Integer, nullable=True)
    revocation_status = sa.Column(sa.String(255))
    last_modification_timestamp_ticks = sa.Column(sa.String(255))
    
    extracted_at = sa.Column(sa.DateTime, nullable=False)


class Message(Base):
    """
    """
    __tablename__ = "message"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    message_id = sa.Column(sa.String(255), unique=True, index=True, nullable=False)

    timestamp_ticks = sa.Column(sa.String(255))
    last_patch_timestamp_ticks = sa.Column(sa.String(255))

    from_box_id = sa.Column(sa.String(255))
    from_title = sa.Column(sa.String(255))
    to_box_id = sa.Column(sa.String(255))
    to_title = sa.Column(sa.String(255))
    
    created_from_draft_id = sa.Column(sa.String(255), nullable=True)
    proxy_box_id = sa.Column(sa.String(255), nullable=True)
    proxy_title = sa.Column(sa.String(255), nullable=True)
    lock_mode = sa.Column(sa.String(255), nullable=True)
    message_type = sa.Column(sa.String(255), nullable=True)
    
    is_draft = sa.Column(sa.Boolean, nullable=True)
    draft_is_locked = sa.Column(sa.Boolean, nullable=True)
    draft_is_recycled = sa.Column(sa.Boolean, nullable=True)
    is_deleted = sa.Column(sa.Boolean, nullable=True)
    is_test = sa.Column(sa.Boolean, nullable=True)
    is_internal = sa.Column(sa.Boolean, nullable=True)
    is_proxified = sa.Column(sa.Boolean, nullable=True)
    is_reusable = sa.Column(sa.Boolean, nullable=True)
    packet_is_locked = sa.Column(sa.Boolean, nullable=True)
    
    extracted_at = sa.Column(sa.DateTime, nullable=False)


class MessageEntity(Base):
    """
    """
    __tablename__ = "message_entity"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    message_id = sa.Column(sa.String(255), sa.ForeignKey(Message.message_id, ondelete='CASCADE', onupdate='CASCADE'), index=True, nullable=False)
    entity_id = sa.Column(sa.String(255), unique=True, index=True, nullable=False)
    parent_entity_id = sa.Column(sa.String(255), nullable=True)

    entity_type = sa.Column(sa.String(255), nullable=True)
    attachment_type = sa.Column(sa.String(255), nullable=True)
    file_name = sa.Column(sa.String(255), nullable=True)
    content_size = sa.Column(sa.String(255), nullable=True)
    content_type_id = sa.Column(sa.String(255), nullable=True)
    raw_creation_date = sa.Column(sa.String(255), nullable=True)
    
    author_user_id = sa.Column(sa.String(255), nullable=True)
    signer_box_id = sa.Column(sa.String(255), nullable=True)
    signer_department_id = sa.Column(sa.String(255), nullable=True)
    packet_id = sa.Column(sa.String(255), nullable=True)
    not_delivered_event_id = sa.Column(sa.String(255), nullable=True)
    attachment_version = sa.Column(sa.String(255), nullable=True)
    version = sa.Column(sa.String(255), nullable=True)
    
    
    need_receipt = sa.Column(sa.Boolean, nullable=True)
    need_recipient_signature = sa.Column(sa.Boolean, nullable=True)
    is_approvement_signature = sa.Column(sa.Boolean, nullable=True)
    is_encrypted_content = sa.Column(sa.Boolean, nullable=True)
    
    extracted_at = sa.Column(sa.DateTime, nullable=False)
    
    
    