import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("visitor-counter")


def lambda_handler(event, context):
    # Atomic increment: concurrent visitors cannot overwrite each other.
    # ADD also creates the item the first time the function runs.
    response = table.update_item(
        Key={"id": "site"},
        UpdateExpression="ADD visits :inc",
        ExpressionAttributeValues={":inc": 1},
        ReturnValues="UPDATED_NEW",
    )
    count = int(response["Attributes"]["visits"])
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"count": count}),
    }
