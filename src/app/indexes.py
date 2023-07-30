import logging
import time
from typing import List, Tuple, Dict

from pymongo import ASCENDING

from app.settings import settings

indexes_data = {
    "user": {
        "__user_index__": [
            ("active", ASCENDING),
            ("latest", ASCENDING)
        ],
        "__user_email_index__": [
            ("active", ASCENDING),
            ("latest", ASCENDING),
            ("email", ASCENDING),
        ],
        "__user_entity_id_index__": [
            ("active", ASCENDING),
            ("latest", ASCENDING),
            ("entity_id", ASCENDING),
        ],
        "__user_role_index__": [
            ("active", ASCENDING),
            ("latest", ASCENDING),
            ("role", ASCENDING),
        ],
    },
    "revoked_token": {
        "__revoked_token_index__": [
            ("active", ASCENDING),
            ("latest", ASCENDING)
        ],
        "__revoked_token_entity_id_index__": [
            ("active", ASCENDING),
            ("latest", ASCENDING),
            ("entity_id", ASCENDING)
        ],
        "__revoked_token_jti_index__": [
            ("active", ASCENDING),
            ("latest", ASCENDING),
            ("jti", ASCENDING)
        ]
    },
}


def create_indexes():
    for collection_name, index_data in indexes_data.items():
        create_index_in_collection(collection_name=collection_name, data=index_data)


def create_index_in_collection(collection_name: str, data: Dict[str, List[Tuple]]):
    logging.info(f"Creating indexes for {collection_name}")
    repo = settings.get_repo()
    for index_name, columns in data.items():
        repo.create_index(
            columns=columns,
            index_name=index_name,
            collection_name=collection_name,
            partial_filter=dict(latest=True, active=True)
        )


def run(retires: int = 5):
    try:
        create_indexes()
    except Exception as ex:
        logging.exception(ex)
        logging.warning("Retrying creating indexes")
        retires -= 1
        time.sleep(0.1)
        run(retires=retires)


if __name__ == "__main__":
    run()
