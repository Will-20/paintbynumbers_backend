from celery import shared_task
from PIL import Image, ImageFilter
import numpy as np
from convert import regionise_image
from remove_small_pixels import remove_small_pixels

from aws_utils import get_image, put_colours, put_image

# Converts an image into its contours
@shared_task(bind=True)
def convert(self, image_id: str, image_name: str, num_colours: str, mywidth: str):
    self.update_state(state='PROCESSING', meta={"progress": "Resizing Image..."})
    
    num_colours = int(num_colours)
    mywidth = int(mywidth)
    image = get_image(image_id)
    image = image.convert('RGB')
    wpercent = (mywidth/float(image.size[0]))
    myheight = int((float(image.size[1])*float(wpercent)))
    resized_image = image.resize((mywidth,myheight), resample=Image.Resampling.HAMMING).filter(ImageFilter.BLUR)
    self.update_state(state='PROCESSING', meta={"progress": f"Looking for common colours"})

    index_map, k_centroids = regionise_image(resized_image, num_colours, distance='redmean')
    put_colours(image_id, k_centroids)
    self.update_state(state='PROCESSING', meta={"progress": "Filling in regions"})

    index_map, outline_with_numbers_image = remove_small_pixels(index_map)
    regioned_image = k_centroids[index_map].astype(np.uint8)
    smoothed_im = Image.fromarray(regioned_image)
    outline_image = Image.fromarray(outline_with_numbers_image)
    self.update_state(state='PROCESSING', meta={"progress": "Uploading Images"})

    put_image(smoothed_im, image_id+"_filled")
    put_image(outline_image, image_id+"_outline")

    return {"result": "Task is Done", "progress": "Finished"}

