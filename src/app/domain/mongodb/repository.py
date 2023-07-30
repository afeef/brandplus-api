import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Callable

from pymongo import MongoClient, ReturnDocument
from app.domain.repositories.repository import Repository
from app.domain.mongodb import __all__ as mongo_classes


def get_uuid4_hex():
    return uuid.uuid4().hex


class MongoDBRepository(Repository, *mongo_classes):
    def __init__(self, mongo_uri, mongo_database, *args, **kwargs):
        self._client = MongoClient(mongo_uri)
        self.db = self._client.get_database(mongo_database)

    def create(self, data: Dict, collection_name: str):
        self.db[collection_name].insert_one(data)

    def create_many(self, data: List[Dict], collection_name: str):
        self.db[collection_name].insert_many(documents=data)

    def _with_retry(self, function: Callable, max_retries=5, *args, **kwargs):
        updated_doc = function(**kwargs)
        if updated_doc:
            return updated_doc
        max_retries -= 1
        if max_retries > 0:
            time.sleep(0.05)
            logging.debug(f"Retrying executing {function.__name__}")
            return self._with_retry(function, max_retries=max_retries, *args, **kwargs)

    def update(self, data: Dict, collection_name: str):
        collection = self.db[collection_name]
        updated_doc = self._with_retry(
            function=collection.find_one_and_update,
            filter={'entity_id': data.get("entity_id"), 'latest': True, 'active': True},
            update={'$set': {'latest': False}},
            upsert=False,
            return_document=ReturnDocument.AFTER,
        )
        if updated_doc:
            data.update({
                'previous_version': updated_doc.get('version'),
                'version': get_uuid4_hex(),
                'changed_on': datetime.utcnow().isoformat()
            })
            collection.insert_one(data)
            return data
        raise Exception('Update Failed')

    def delete(self, data: Dict, collection_name: str):
        collection = self.db[collection_name]
        collection.update_one(
            {'entity_id': data.get("entity_id"), 'latest': True, 'active': True},
            {'$set': {'active': False}},
            upsert=False
        )

    def get_one(self, collection_name: str, index: str, query: Dict):
        base_query = {'latest': True, 'active': True}
        if query:
            base_query.update(query)

        data = self.db[collection_name].find_one(base_query, hint=index)
        if data:
            return data

    def get_all(self, collection_name: str, index: str, query: Dict = None):
        base_query = {'latest': True, 'active': True}
        if query:
            base_query.update(query)

        data = self.db[collection_name].find(
            base_query,
            hint=index
        )
        if data:
            return data
        return []

    def get_count(self, collection_name: str, index: str, query: Dict):
        query.update(dict(latest=True, active=True))
        return self.db[collection_name].count_documents(query, hint=index)

    def create_index(self, collection_name: str, columns: List, index_name: str, partial_filter: Dict):
        self.db[collection_name].create_index(
            columns,
            name=index_name,
            partialFilterExpression=partial_filter
        )
