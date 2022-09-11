import pymongo
import certifi
import json
import logging_file
import config


# Create connection with mongoDB
def create_connection():
    try:
        config.configure()
        password = config.get_mongodb_pass()
        client = pymongo.MongoClient(
            f"mongodb+srv://hiteshwadhwani1403:{password}@ineuron.xskip.mongodb.net/?retryWrites=true&w=majority",
            tlsCAFile=certifi.where())
        logging_file.info(client)
    except Exception as e:
        logging_file.error(f"Some error in making connection with mongoDB {e}")

    return client


def store_data(collection_name):
    client = create_connection()
    # create DB
    db = client['youtube-scrapper']
    # create collection
    col = db[collection_name]
    with open(f'{collection_name}.json') as file:
        file_data = json.load(file)
    try:
        col.insert_many([file_data])
    except Exception as e:
        logging_file.error(f"error in inserting data {e}")


def find_data(collection_name):
    client_conn = create_connection()
    db = client_conn['youtube-scrapper']
    mycol = db[collection_name]
    data = mycol.find({})
    return data


print(find_data("krish_naik"))
