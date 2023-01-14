from pymongo import MongoClient
from pymongo.collection import Collection
from scrapers.interface import JobSummary, JobDetails
from typing import List
from .models import MongoJob, MongoTokens


class DBMongoClient:
    PORT = 27018
    DOCUMENT_NAME = 'FindJobs'

    def __init__(self) -> None:
        client = MongoClient("mongodb://localhost:27018/")
        self._db = client["FindJobs"]

    @property
    def offers(self) -> Collection:
        return self._db["Offers"]

    @property
    def tokens(self) -> Collection:
        return self._db["Tokens"]

    def insert_tokens(self, tokens):

        for token in tokens:
            current_value = self.tokens.find_one({'name': token['name']})
            item = MongoTokens(**token, current_value=current_value)

            if current_value:
                self.tokens.update_one({'name': item.name}, item.__dict__)

            self.tokens.insert_one(item.__dict__)

    def insert_jobs(self, jobs: List[JobDetails]):
        items = [MongoJob(**item.__dict__) for item in jobs]

        return self.offers.insert_many([item.__dict__ for item in items])

    def filter_unknowing_jobs(self, jobs: List[JobSummary], portal: str) -> List[JobSummary]:
        pipeline = [
            {
                '$match': {
                    "$expr": {
                        "$and": {
                            "$or": [
                                {"$in": ['$id', [job.id for job in jobs]]},
                                {"$in": ['$url', [job.url for job in jobs]]},
                            ],
                            "$eq": ['$portal', portal]
                        }
                    }
                }
            }
        ]

        result = self.offers.aggregate(pipeline)

    def ranking(self, keywords, limit=10, offset=0):
        return self.tokens.aggregate([
            {
                '$match': {
                    'name': {
                        '$in': keywords
                    }
                }
            },
            {
                '$unwind': {
                    'path': '$docList',
                }
            },
            {
                '$group': {
                    '_id': '$docList',
                    'count': {
                        '$sum': 1
                    },
                    'tokens': {
                        '$push': '$name'
                    }
                }
            },
            {
                '$sort': {
                    'count': -1
                }
            },
            {
                '$skip': offset
            },
            {
                '$limit': limit
            },
            {
                '$lookup': {
                    'from': 'Offers',
                    'localField': '_id',
                    'foreignField': '_id',
                    'as': 'Doc'
                }
            },
            {
                '$unwind': {
                    'path': '$Doc'
                }
            }
        ])


# [
#     {
#         '$match': {
#             'name': {
#                 '$in': [
#                     'python', 'back', 'backend', 'node', 'nodejs'
#                 ]
#             }
#         }
#     }, {
#         '$addFields': {
#             'kwd': [
#                 'python', 'back', 'backend', 'node', 'nodejs'
#             ],
#             'values': [
#                 1, 3, 4, 2, 1
#             ]
#         }
#     }, {
#         '$addFields': {
#             'value_index': {
#                 '$indexOfArray': [
#                     '$kwd', '$name'
#                 ]
#             }
#         }
#     }, {
#         '$addFields': {
#             'value': {
#                 '$arrayElemAt': [
#                     '$values', '$value_index'
#                 ]
#             }
#         }
#     }, {
#         '$unwind': {
#             'path': '$docList'
#         }
#     }, {
#         '$group': {
#             '_id': '$docList',
#             'count': {
#                 '$sum': '$value'
#             },
#             'tokens': {
#                 '$push': '$name'
#             }
#         }
#     }, {
#         '$sort': {
#             'count': -1
#         }
#     }, {
#         '$lookup': {
#             'from': 'Offers',
#             'localField': '_id',
#             'foreignField': '_id',
#             'as': 'Doc'
#         }
#     }, {
#         '$unwind': {
#             'path': '$Doc'
#         }
#     }
# ]
