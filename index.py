from flask import Flask, jsonify, request
from PIL import Image
import time
from celery.result import AsyncResult

from tasks import convert_task
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
celery_init_app(app)

@app.route('/api/upload', methods=['POST'])
def task_start():
    task = convert_task.delay("")
    return {"task_id": task.id}


@app.route("/api/progress", methods=["POST"])
def task_progress():
    data = request.get_json()
    task = AsyncResult(data["task_id"])
    if task.info is None:
        prog = 0
    else:
        prog = task.info.get("progress", 0)
    return {"state": task.state, "progress": prog}


if __name__ == '__main__':
    app.run(port=5328)



# celery_app = celery_init_app(app)

# @app.route('/api/image', methods=['POST'])
# def image():
#     time.sleep(4)
#     return "received " + str(len(request))


# def celery_init_app(app: Flask) -> Celery:
#     class FlaskTask(Task):
#         def __call__(self, *args: object, **kwargs: object) -> object:
#             with app.app_context():
#                 return self.run(*args, **kwargs)

#     celery_app = Celery(app.name, task_cls=FlaskTask)
#     celery_app.config_from_object(app.config["CELERY"])
#     celery_app.set_default()
#     app.extensions["celery"] = celery_app
#     return celery_app

# @app.route('/api/hello', methods=['GET'])
# def hello_world():
#     return jsonify("Hello, World!")

# @app.route('/api/goodbye', methods=['POST'])
# def goodbye():
#     time.sleep(3)
#     return request.form["title"]

# # Adds the convert task to the broker?
# @app.route('/api/upload', methods=['POST'])
# def upload():
#     image_id = request.form['image_id']
#     image_name = request.form['image_name']
#     num_colours = request.form['num_colours']
#     width = request.form['width']

#     print(image_id, image_name)

#     # img = Image.open(file)
#     # print(img.size)

#     # convert(img, 40)
    
#     return jsonify({
#         "output": f"ID: {image_id} Image_name: {image_name}"
#     })