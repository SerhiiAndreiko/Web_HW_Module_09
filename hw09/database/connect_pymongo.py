# from pymongo.mongo_client import MongoClient

# uri = "mongodb+srv://phantomDB:Phantom@cluster0.irjd6gn.mongodb.net/?retryWrites=true&w=majority&appName=AtlasApp"

# # Create a new client and connect to the server
# client = MongoClient(uri)

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

from pymongo.mongo_client import MongoClient

MongoDB_USER = "phantomDB"
MongoDB_PASSWORD = "Phantom"
MongoDB_HOST = "cluster0.irjd6gn.mongodb.net"

URI = f"mongodb+srv://{MongoDB_USER}:{MongoDB_PASSWORD}@{MongoDB_HOST}/?retryWrites=true&w=majority&appName=AtlasApp"

client = None

def connect():
    global client
    client = MongoClient(URI)
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    connect()
