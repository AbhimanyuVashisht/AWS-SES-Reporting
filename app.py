from chalice import Chalice
import os
import boto3
from uuid import uuid4
from datetime import datetime
import json

app = Chalice(app_name='aws-ses-deliveries')

app.debug = True
access_key = os.environ['ACCESS_ID']
secret_key = os.environ['ACCESS_KEY']


@app.on_sns_message(topic='aws-ses-deliveries')
def handler(event):
    data = json.loads(event.message)
    mailtype = data["notificationType"].lower()
    if mailtype == "delivery":
        key = "recipients"
    elif mailtype == "bounce":
        key = "bouncedRecipients"
    else:
        key = "complainedRecipients"
    mailobj = data[mailtype]
    token = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
    session = boto3.session.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='us-east-1'
    )
    dynamo = session.resource('dynamodb')
    table = dynamo.Table('aws-ses-deliveries')
    table.put_item(
        Item={
            'id': token,
            'mailtype': mailtype,
            'timestamp': mailobj["timestamp"],
            'recipients': mailobj[key]
        }
    )