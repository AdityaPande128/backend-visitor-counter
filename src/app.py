import json
import boto3
import os

table_name = os.environ.get('TABLE_NAME')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """
    Handles API Gateway requests to increment and retrieve the visitor count.
    """
    try:
        response = table.update_item(
            Key={'id': 'visitor_count'},
            UpdateExpression='SET visit_count = if_not_exists(visit_count, :start) + :inc',
            ExpressionAttributeValues={
                ':inc': 1,
                ':start': 0
            },
            ReturnValues='UPDATED_NEW'
        )
        
        count = int(response['Attributes']['visit_count'])
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*', 
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps({'count': count})
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps({'error': 'Could not process the request.'})
        }
