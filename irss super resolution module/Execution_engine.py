from Run_ESRGAN import Run as run_esrgan
import os, time, boto3

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='irss_not_processed_images_queue.fifo')

download_bucket = "irss.not.processed.images.bucket"
upload_bucket = "irss.processed.images.bucket"


def check_if_item_exist_dynamo(image_hash):
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


def get_item_dynamodb(image_hash):
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


def download_image_from_s3(image_name, bucket_name):
    boto3.client('s3').download_fileobj(bucket_name, image_name, open('./LR/' + image_name, 'wb'))


def lambda_upload_file_to_s3(image_name, bucket_name):
    boto3.client('s3').upload_fileobj(open('/HR/' + image_name, 'rb'), bucket_name, image_name)


def delete_file_from_s3(filename, bucket_name):
    boto3.client('s3').delete_object(Bucket=bucket_name, Key=filename)


while True:
    print(queue.receive_messages())
    for message in queue.receive_messages():
        codigo_imagen = message.body
        print("Codigo de la siguiente imagen:" + str(codigo_imagen))
        if check_if_item_exist_dynamo(codigo_imagen) == True:
            estado = get_item_dynamodb(codigo_imagen)
            nombre_imagen = str(estado['image_original_name'])
            paso_imagen = int(estado['image_estate'])
            print("Estado de la imagen: " + str(paso_imagen))
            print("Nombre de la imagen: " + str(nombre_imagen))
            if paso_imagen == 1:
                download_image_from_s3(nombre_imagen, download_bucket)
                run_esrgan()
                if os.path.exists('./LR/' + nombre_imagen):
                    os.remove('./LR/' + nombre_imagen)
                nombre_imagen, extension = nombre_imagen.split(".")
                nombre_imagen = nombre_imagen + "_rlt." + extension
                lambda_upload_file_to_s3(nombre_imagen, upload_bucket)
                if os.path.exists('./HR/' + nombre_imagen):
                    os.remove('./HR/' + nombre_imagen)
                delete_file_from_s3(nombre_imagen, download_bucket)
                print("Imagen " + nombre_imagen + " escalada y entrgada en " + upload_bucket)

        message.delete()
        time.sleep(60)
