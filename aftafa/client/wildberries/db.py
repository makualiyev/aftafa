from sqlalchemy import text

from aftafa.common.dal import engine as db_engine, session as db_session
from aftafa.client.wildberries.models import Base



def initial_create() -> None:
    metadata = Base.metadata
    metadata.create_all(bind=db_engine)
    return None

def initial_populate() -> None:
    pass

def main() -> None:
    initial_create()
    initial_populate()


if __name__ == '__main__':
    main()
