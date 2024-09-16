from flask import Flask, request
from PIL import Image
from celery.result import AsyncResult

from tasks import convert
from utils import celery_init_app

app = Flask(__name__)
app.config.from_mapping(
    CELERY=dict(
        # broker_url="redis://default:AYDaAAIjcDE2MmE1NjMxMjA2NmU0YTY0YTE5MjM5NWQyMGYzMjA1NnAxMA@normal-ray-32986.upstash.io:6379",
        # result_backend="redis://default:AYDaAAIjcDE2MmE1NjMxMjA2NmU0YTY0YTE5MjM5NWQyMGYzMjA1NnAxMA@normal-ray-32986.upstash.io:6379",
        broker_url="redis://localhost:6379/0",
        result_backend="redis://localhost:6379/0",
    )
)
celery = celery_init_app(app)

@app.route('/api/upload', methods=['POST'])
def task_start():

    image_id = request.form['image_id']
    image_name = request.form['image_name']
    num_colours = request.form['num_colours']
    print(num_colours)
    mywidth = request.form['width']

    task = convert.delay(image_id, image_name, num_colours, mywidth)
    return {"task_id": task.id}


@app.route("/api/progress", methods=["POST"])
def task_progress():
    data = request.get_json()
    print(data["task_id"])
    task = AsyncResult(data["task_id"])
    
    if task.info is None:
        prog = "UNSTARTED"
    else:
        prog = task.info.get("progress", "UNSTARTED")
    return {"state": task.state, "progress": prog}

if __name__ == '__main__':
    app.run(port=5328)

