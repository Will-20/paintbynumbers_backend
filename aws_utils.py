import json
import boto3
import io
from botocore.exceptions import ClientError
from PIL import Image
import logging

def get_image(image_id):
    client = boto3.client('s3')
    try:
        outfile = io.BytesIO()
        client.download_fileobj("paint-by-numbers-image-data", image_id, outfile)
        outfile.seek(0)
    except ClientError as e:
        logging.log(e)
    im = Image.open(outfile)
    return im

def put_image(image, image_id):
    client = boto3.client('s3')
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    buf.seek(0)
    try:
        client.upload_fileobj(buf, "paint-by-numbers-image-data", image_id)
    except ClientError as e:
        logging.log(e)

def put_colours(image_id, colours):
    def hexify(point):
        s = "#"
        for p in point:
            s += str(hex(int(p)))[2:].zfill(2)
        return s
    json_dict = dict([(i+1, hexify(colours[i])) for i in range(len(colours))])
    json_string = json.dumps(json_dict).encode('UTF-8')
    client = boto3.client('s3')
    try:
        client.put_object(Body=json_string, Bucket="paint-by-numbers-image-data", Key=image_id+"_colours")
        print(json_string)
    except ClientError as e:
        logging.log(e)
