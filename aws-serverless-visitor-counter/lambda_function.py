import boto3
import json
import time

dynamodb = boto3.resource('dynamodb')
visitor_table = dynamodb.Table('VisitorCounter')
ip_table = dynamodb.Table('VisitorIPs')

RATE_LIMIT_SECONDS = 30

def lambda_handler(event, context):
    ip_address = event.get('requestContext', {}).get('http', {}).get('sourceIp', 'unknown')
    current_time = int(time.time())
    print(f"[DEBUG] Event: {json.dumps(event)}")
    print(f"[INFO] Incoming IP: {ip_address} at {current_time}")

    try:
        ip_record = ip_table.get_item(Key={'ip': ip_address})
        print(f"[DEBUG] IP lookup result: {ip_record}")

        if 'Item' in ip_record:
            last_seen = ip_record['Item'].get('last_seen', 0)
            delta = current_time - last_seen
            print(f"[INFO] IP {ip_address} last seen {last_seen} ({delta} seconds ago)")

            if delta < RATE_LIMIT_SECONDS:
                count_data = visitor_table.get_item(Key={'id': 'global'})
                cached_count = count_data.get('Item', {}).get('count', 0)
                print(f"[INFO] Rate limit enforced. Returning cached count {cached_count}.")
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'count': cached_count,
                        'message': 'Rate limit enforced'
                    })
                }

    except Exception as e:
        print(f"[ERROR] Problem checking IP table: {e}")

    # Update the main visitor counter
    try:
        response = visitor_table.update_item(
            Key={'id': 'global'},
            UpdateExpression='ADD #count :inc',
            ExpressionAttributeNames={'#count': 'count'},
            ExpressionAttributeValues={':inc': 1},
            ReturnValues='UPDATED_NEW'
        )
        new_count = int(response['Attributes']['count'])
        print(f"[INFO] Visitor count incremented to {new_count}")
    except Exception as e:
        print(f"[ERROR] Failed to update counter: {e}")
        new_count = -1

    # Save IP timestamp for rate-limiting
    try:
        ip_table.put_item(Item={
            'ip': ip_address,
            'last_seen': current_time
        })
        print(f"[INFO] Stored new last_seen for IP {ip_address}")
    except Exception as e:
        print(f"[ERROR] Could not update IP table: {e}")

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'count': new_count
        })
    }
