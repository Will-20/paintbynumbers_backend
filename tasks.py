from celery import shared_task
from PIL import Image, ImageFilter
import boto3
from botocore.exceptions import ClientError
from time import sleep
import numpy as np
from convert import regionise_image, remove_small_pixels

@shared_task(bind=True)
def convert_task(self, imageId):
    self.update_state(state='PROCESSING', meta={"progress": 0})
    sleep(3)
    self.update_state(state='PROCESSING', meta={"progress": 33})
    sleep(3)
    self.update_state(state='PROCESSING', meta={"progress": 66})
    sleep(3)
    self.update_state(state='PROCESSING', meta={"progress": 99})
    sleep(3)
    return {"result": "Task is Done", "progress": 100}

# Converts an image into its contours
@shared_task(bind=True)
def convert(self, name: str, num_colours: str, mywidth: str):
    self.update_state(state='PROCESSING', meta={"progress": "STARTED"})
    
    num_colours = int(num_colours)
    mywidth = int(mywidth)


    image = Image.open("130882.png")

    image = image.convert('RGB')
    

    wpercent = (mywidth/float(image.size[0]))
    myheight = int((float(image.size[1])*float(wpercent)))
    resized_image = image.resize((mywidth,myheight), resample=Image.Resampling.HAMMING).filter(ImageFilter.BLUR)
    self.update_state(state='PROCESSING', meta={"progress": "RESIZED IMAGE"})

    index_map, k_centroids = regionise_image(resized_image, num_colours, distance='euclidean')
    self.update_state(state='PROCESSING', meta={"progress": "OBTAINED COLOURS"})

    index_map, outline_with_numbers_image = remove_small_pixels(index_map)
    regioned_image = k_centroids[index_map].astype(np.uint8)
    self.update_state(state='PROCESSING', meta={"progress": "REGIONED IMAGE"})

    smoothed_im = Image.fromarray(regioned_image)
    outline_image = Image.fromarray(outline_with_numbers_image)
    self.update_state(state='PROCESSING', meta={"progress": "OBTAINED OUTLINE"})

    # Save in bucket instead?
    smoothed_im.save("image.png")
    outline_image.save("image_outline.png")
    return {"result": "Task is Done", "progress": "FINISHED"}

    # s3_client = boto3.client('s3')
    # try:
    #     response = s3_client.upload_file(name, "paint-by-numbers-image-data")
    # except ClientError as e:
    #     print(e)
    #     return False
    # return True
