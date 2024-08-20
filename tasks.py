from celery import shared_task
# import boto3
from time import sleep

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