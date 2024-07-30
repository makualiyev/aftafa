from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base



DEFAULT_SCHEMA = 'ec'
with open("env/conf", "r") as f:
    db_url: str = f.readline()

Base = declarative_base()
engine = create_engine(db_url)
session = Session(engine)

convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': (
        'fk__%(table_name)s__%(all_column_names)s__'
        '%(referred_table_name)s'
    ),
    'pk': 'pk__%(table_name)s'
}

Base.metadata.naming_convention = convention