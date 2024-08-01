from dataclasses import asdict
from typing import List, Dict, Any, Union

from pymongo import MongoClient, UpdateOne
from pymongo.collection import Collection

from config  import settings

class MongoDBHandler:

    def __init__(self):
        self.client = MongoClient(settings.MONGO_DB_HOST, settings.MONGO_DB_PORT)
        self.db = self.client[settings.MONGO_DB_NAME]
        self.collection = self.db[settings.MONGO_DB_COLLECTION_NAME]
    
    def get_collection(self) -> Collection:
        """
        Return the collection
        """
        return self.collection
    
    def get_all_data(self) -> Union[List[Dict[str, Any]], List[None]]:
        """
        Return all the data from collection
        """
        return list(self.collection.find({}))
    
    def insert_data_operations(self, unique_data: List[Any]) -> None:
        """
        This function performs the following operations:
          1. Iterates through each unique host data.
          2. Checks if the host data exists in the database using the host ID.
          3. If the host exists, compares the 'updated' value with the 'updated' value stored in the database.
             If the 'updated' value is greater, updates the operations array with the new host data.
          4. If the host does not exist, adds an operation to insert the new host data with upsert=True.
          5. Executes all the operations in bulk to the database.
        """
        operations = []
        for host in unique_data:
            host_dict = asdict(host)
            existing_host = self.collection.find_one({'host_id': host.host_id})
            if existing_host:
                existing_updated = existing_host.get('updated')
                if existing_updated and host.updated > existing_updated:
                    operations.append(UpdateOne({'host_id': host.host_id}, {'$set': host_dict}))
            else:
                operations.append(UpdateOne({'host_id': host.host_id}, {'$set': host_dict}, upsert=True))
        
        if operations:
            self.collection.bulk_write(operations)

mongo_db = MongoDBHandler()