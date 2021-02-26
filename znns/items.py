import datetime
from uuid import uuid4

import boto3
from boto3.dynamodb.conditions import Attr


class DynamoDBTable:
    def __init__(self, table_name, local_mode=False):
        if local_mode:
            dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
        else:
            dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.Table(table_name)

    def list(self, limit=100):
        res = self.table.scan(Limit=limit)
        return res['Items']

    def update(self, model_id, updates):
        updates = {} if updates is None else updates
        updates['updated_at'] = self.get_timestamp()
        self.table.update_item(
            AttributeUpdates=updates,
            ConditionExpression=Attr('id').eq(model_id)
        )

    @staticmethod
    def get_timestamp():
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


class Model(DynamoDBTable):
    def __init__(self, local_mode=False):
        super(Model, self).__init__(table_name='models', local_mode=local_mode)


class Album(DynamoDBTable):
    def __init__(self, local_mode=False):
        super(Album, self).__init__(table_name='albums', local_mode=local_mode)

    def add(self, model_id, title, url):
        item = {
            'id': str(uuid4()),
            'updated_at': self.get_timestamp(),
            'model_id': model_id,
            'title': title,
            'url': url,
        }
        self.table.put_item(Item=item)
        return item

    def has(self, url):
        items = self.table.scan(FilterExpression=Attr('url').contains(url))['Items']
        return len(items) > 0
