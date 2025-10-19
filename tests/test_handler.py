import unittest
import boto3
from moto import mock_dynamodb
import os
import sys

# Add the 'src' directory to the Python path to import 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from app import lambda_handler

@mock_dynamodb
class TestLambdaHandler(unittest.TestCase):

    def setUp(self):
        """Set up a mock DynamoDB table and environment variables."""
        self.table_name = "test-table"
        os.environ['TABLE_NAME'] = self.table_name

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        dynamodb.create_table(
            TableName=self.table_name,
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
        )
        self.table = dynamodb.Table(self.table_name)

    def test_first_visit(self):
        """Test the counter for the very first visitor."""
        response = lambda_handler({}, {})
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(body['count'], 1)

        # Verify the count in the mock database
        db_response = self.table.get_item(Key={'id': 'visitor_count'})
        self.assertEqual(db_response['Item']['visit_count'], 1)

    def test_subsequent_visits(self):
        """Test that the counter increments correctly on subsequent visits."""
        # Simulate the first visit
        lambda_handler({}, {})
        
        # Simulate the second visit
        response = lambda_handler({}, {})
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(body['count'], 2)

        # Verify the count in the mock database
        db_response = self.table.get_item(Key={'id': 'visitor_count'})
        self.assertEqual(db_response['Item']['visit_count'], 2)

if __name__ == '__main__':
    unittest.main()
