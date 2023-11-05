# import configparser

# from psycopg2 import OperationalError, connect

# config = configparser.ConfigParser()
# config.read('config.ini')

# MongoDB_USER = config['MongoDB']['MongoDB_USER']
# MongoDB_PASSWORD = config['MongoDB']['MongoDB_PASSWORD']
# MongoDB_HOST = config['MongoDB']['MongoDB_HOST']
# MongoDB_NAME = config['MongoDB']['MongoDB_NAME']

# connect_state = False

# def connect_db():
#     global connect_state
#     if MongoDB_USER:
#         URI = f"""mongodb+srv://{MongoDB_USER}:{MongoDB_PASSWORD}@{MongoDB_HOST}/{MongoDB_NAME}?retryWrites=true&w=majority"""
#         try:
#             connect(host=URI, ssl=True)
#         except OperationalError:
#             print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
#         except Exception as e:
#             print("error:",e)
#         else:
#             print("connect_db - ok")
#             connect_state = True
#     else:
#         print("not defined MongoDB_USER from enviroment. Database not connected")
#     return connect_state

from pymongo.mongo_client import MongoClient

MongoDB_USER = "phantomDB"
MongoDB_PASSWORD = "Phantom"
MongoDB_HOST = "cluster0.irjd6gn.mongodb.net"
Mongo_NAME = "scrapy"

URI = f"mongodb+srv://{MongoDB_USER}:{MongoDB_PASSWORD}@{MongoDB_HOST}/{Mongo_NAME}?retryWrites=true&w=majority&appName=AtlasApp"

client = None

def connect_db():
    global client
    client = MongoClient(URI)
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    connect_db()