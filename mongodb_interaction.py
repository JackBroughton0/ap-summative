import pymongo
import pandas as pd
import numpy as np
from pandas import json_normalize


def upload_to_mongo(upload_data):
    """Upload the formatted data to MongoDB for later retrieval"""
    collection = connect_to_mongodb()
    # Delete all current documents in the collection
    collection.delete_many({})
    # Insert JSON data into the collection
    collection.insert_many(upload_data)


def clean_column_name(column_name):
    """Remove prefixes from column names"""
    cleaned_name = column_name.replace('Service Labels.', '').replace('Site Info.', '')
    return cleaned_name


def retrieve_from_mongo():
    """
    Retrieve the cleaned and formatted data from MongoDB.
    This will be the input data for data visualisations
    """
    collection = connect_to_mongodb()
    # Get all the documents stored in the MongoDB collection
    all_documents = collection.find({})
    document_list = list(all_documents)
    # Convert list of dictionaries into a dataframe
    df = json_normalize(document_list)
    # Remove prefixes where the data was stored in a nested dictionary
    df.columns = [clean_column_name(col) for col in df.columns]
    # Replace None with more intuitive np.nan
    df = df.fillna(value=np.nan)
    return df


def connect_to_mongodb():
    """
    Connect to the Mongodb server and return the
    collection responsible for storing the formatted data
    """
    # Establish a connection to the MongoDB server
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["radio_data"]
    collection = db["formatted_data"]
    return collection

