def generate_random_image_hash():
    import random
    return '%032x' % random.getrandbits(128)


def download_image_from_s3_to_lambda_temp(image_name, bucket_name):
    import boto3
    boto3.client('s3').download_fileobj(bucket_name, image_name, open('/tmp/' + image_name, 'wb'))


def load_image_from_lambda_temp(image_name):
    return open('/tmp/' + image_name, 'rb')


def remove_image_from_lambda_temp(image_name):
    import os
    if os.path.exists('/tmp/' + image_name):
        os.remove('/tmp/' + image_name)


def add_item_dynamodb(image_hash, user_email, image_name):
    import boto3
    flow_control_table = boto3.resource('dynamodb').Table('irss_flow_control_table')
    if check_if_item_exist_dynamo(image_hash) is False:
        flow_control_table.put_item(
            Item={
                'image_hash': str(image_hash),
                'user_email': str(user_email),
                'image_original_name': str(image_name),
                'image_estate': '1'
            }
        )
        return True
    elif check_if_item_exist_dynamo(image_hash) is True:
        return False


def get_item_dynamodb(image_hash):
    import boto3
    flow_control_table = boto3.resource('dynamodb').Table('irss_flow_control_table')
    if check_if_item_exist_dynamo(image_hash) is True:
        item = flow_control_table.get_item(
            Key={
                'image_hash': str(image_hash)
            }
        )
        item = item['Item']
        return item
    elif check_if_item_exist_dynamo(image_hash) is False:
        return None


def delet_item_dynamodb(image_hash):
    import boto3
    flow_control_table = boto3.resource('dynamodb').Table('irss_flow_control_table')
    if check_if_item_exist_dynamo(image_hash) is True:
        flow_control_table.delete_item(
            Key={
                'image_hash': str(image_hash)
            }
        )


def check_if_item_exist_dynamo(image_hash):
    import boto3
    flow_control_table = boto3.resource('dynamodb').Table('irss_flow_control_table')
    item = flow_control_table.get_item(
        Key={
            'image_hash': str(image_hash)
        }
    )
    if 'Item' in [key for key in item]:
        return True
    else:
        return False
