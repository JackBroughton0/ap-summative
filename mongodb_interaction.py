import pymongo
import pandas as pd
from pandas import json_normalize


def upload_to_mongo(collection, upload_data):
    """Upload the formatted data to MongoDB for later retrieval"""
    # Insert JSON data into the collection
    collection.insert_many(upload_data)


def clean_column_name(column_name):
    # Remove the prefixes and dots
    cleaned_name = column_name.replace('Service Labels.', '').replace('Site Info.', '')
    return cleaned_name


def retrieve_from_mongo(collection):
    """Retrieve the cleaned and formatted data from MongoDB.
    This will be the input data for data visualisations"""
    all_documents = collection.find({})
    document_list = list(all_documents)
    df = json_normalize(document_list)
    df.columns = [clean_column_name(col) for col in df.columns]
    return df


def connect_to_mongodb():
    """Connect to the Mongodb server and return the
    collection responsible for storing the formatted data"""
    # Establish a connection to the MongoDB server
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["radio_data"]
    collection = db["formatted_data"]
    return collection


if __name__ == '__main__':
    collection = connect_to_mongodb()
    df = retrieve_from_mongo(collection)
    print('hold')

