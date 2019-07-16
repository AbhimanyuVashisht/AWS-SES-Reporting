import sys
from chalice import Chalice
import os
import boto3
from uuid import uuid4
from datetime import datetime
import json
import pymysql
# import logger

app = Chalice(app_name='aws-ses-deliveries')

app.debug = False
access_key = os.environ['ACCESS_ID']
secret_key = os.environ['ACCESS_KEY']

rds_config = {
    "DB_USERNAME": os.environ['DB_USER'],
    "DB_HOST": os.environ['DB_HOST'],
    "DB_PASSWORD": os.environ['DB_PASSWORD'],
    "DB_DATABASE": os.environ['DB_DATABASE'],
    "DB_PORT": os.environ['DB_PORT']
}


try:
    conn = pymysql.connect(rds_config['DB_HOST'], user=rds_config['DB_USERNAME'], password=rds_config['DB_PASSWORD'],
                           db=rds_config['DB_DATABASE'], port=3306, connect_timeout=5)
except pymysql.MySQLError as e:
    sys.exit()


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
    if key in ["bouncedRecipients", "complainedRecipients"]:
        with conn.cursor() as curr:
            email = mailobj[key][0]["emailAddress"]
            curr.execute("UPDATE users SET e_verified = 0 WHERE email= '" + email + "' OR alternate_email= '" + email + "' ;")
        conn.commit()
