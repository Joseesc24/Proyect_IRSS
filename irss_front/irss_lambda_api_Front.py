import json
import boto3
from io import BytesIO
import random

boquet="irss.not.processed.images.bucket"

def lambda_handler(event, context):
    method = event['requestContext']['http']['method']
    
    mensaje={
        'status':0,
        'mensaje': 'Undefined'
    }
    
    if method == 'POST':
        data = json.loads(event['body'])
        file = data['myFile']
        name = data['name']
        file = b64decode(file.split(',')[1])
        codigo=generate_random_image_hash()
        save_image(codigo+"-"+name, file)
        upload_image(codigo+"-"+name)
        add_item_dynamodb(codigo, data['Correo'], codigo+'-'+name)
        
        mensaje={
            'status':0,
            'mensaje': 'Se Creao El Archivo '+name+' como '+codigo+'-'+name+' con el codigo '+codigo,
            'archivo' : name
            
        }
        
    return {
        'headers': {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST"
        },
        'statusCode': 200,
        'body': json.dumps(mensaje)
    }


def upload_image(name):
    s3_client = boto3.client('s3') 
    archivo = '/tmp/' + name
    response=s3_client.upload_file(archivo, boquet, name)

def save_image(name, file):
    with open('/tmp/' + name, 'wb') as destination:
           destination.write(file)





def add_item_dynamodb(image_hash, user_email, image_name):
    
    flow_control_table = boto3.resource('dynamodb').Table('irss_flow_control_table')
    
    if check_if_item_exist_dynamo(image_hash, flow_control_table) is False:
        flow_control_table.put_item(
            Item={
                'image_hash': image_hash,
                'user_email': user_email,
                'image_original_name': image_name,
                'image_estate': 1
            }
        )
        return True
    elif check_if_item_exist_dynamo(image_hash, flow_control_table) is True:
        return False


def check_if_item_exist_dynamo(image_hash, flow_control_table):
    print(type(flow_control_table))
    item = flow_control_table.get_item(
        Key={'image_hash': image_hash}
    )
    if 'Item' in [key for key in item]:
        return True
    else:
        return False

def generate_random_image_hash():
    return '%032x' % random.getrandbits(128)