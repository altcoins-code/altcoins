import pprint

import pymongo


class MongoDB:
    def __init__(self, host="localhost", port=27017, collection='timeseries'):
        client = pymongo.MongoClient(host, port)
        self.db = client.coins
        self.dates = None
        if not collection in self.db.collection_names():
            self.create_collection(collection)

    def clear_collection(self, collection):
        self.db.drop_collection(collection)

    def create_collection(self, collection):
        self.db.create_collection(collection)

    def update(self, table):
        self.db.timeseries.insert_one({'date': table.timestamp, 'data': table.data.T.to_dict()})

    def list(self):
        dates = []
        for i, post in enumerate(self.db.timeseries.find()):
            print('%d: %s' % (i, str(post['date'])))
            dates.append(post['date'])
        self.dates = dates

    def get_date(self, date):
        # date must be datetime object
        return self.db.timeseries.find_one({"date": date})

    def remove_date(self, date):
        # date must be datetime object
        self.db.timeseries.delete_one({"date": date})

    def pop(self):
        return list(self.db.timeseries.find().sort("date", pymongo.DESCENDING).limit(1)).pop()


if __name__ == "__main__":
    store = MongoDB()
    pprint.pprint(store.pop()['data'])
    # store.list()
