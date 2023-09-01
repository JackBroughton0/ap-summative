import pymongo


def upload_to_mongo(collection, upload_data):
    """Upload the formatted data to MongoDB for later retrieval"""
    # Insert JSON data into the collection
    collection.insert_many(upload_data)

def retrieve_from_mongo(collection):
    """Retrieve the cleaned and formatted data from MongoDB.
    This will be the input data for data visualisations"""
    all_documents = collection.find({})
    # df = 
    # return df

def connect_to_mongodb():
    """Connect to the Mongodb server and return the
    collection responsible for storing the formatted data"""
    # Establish a connection to the MongoDB server
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["radio_data"]
    collection = db["formatted_data"]
    return collection

