import os
from pymongo import MongoClient
from elasticsearch import Elasticsearch
from dotenv import load_dotenv


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
ELASTIC_USER = os.getenv("ELASTIC_USER")  
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")  


mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[DATABASE_NAME]
mongo_collection = mongo_db[COLLECTION_NAME]


es = Elasticsearch(hosts=["http://localhost:9200"],
                   basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD),
                   verify_certs=False)

def load_data_from_mongo_to_elastic():
    cursor = mongo_collection.find()
    for document in cursor:
        # הסר את ה-_id מהמסמך
        document_copy = document.copy()
        document_copy.pop("_id", None)  # הסרת _id מהמסמך

        # שלח את המסמך ל-Elasticsearch עם המזהה כפרמטר
        es.index(index="your_index_name", id=document["_id"], document=document_copy)

if __name__ == '__main__':
    load_data_from_mongo_to_elastic()
