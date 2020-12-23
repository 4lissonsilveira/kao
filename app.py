from flask import Flask

from make_celery import make_celery

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)

celery = make_celery(app)

@celery.task()
def add_together(a, b):
    from time import sleep
    sleep(30)
    print(a + b)


@app.route('/')
def hello_world():
    task = add_together.delay(23, 42)
    return task.id

@app.route('/active-tasks')
def list_tasks():
    response_content = """
    <table border=1>
    <tr>
        <th>Task Id</th>
        <th>Task name</th>
        <th>Start Time</th>
    </tr>
    """
    i = celery.control.inspect()
    items = list(i.active().values())[0]
    for item in items:
        response_content += "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            item['id'], item['name'], item['time_start']
        )
    response_content += "</table>"
    return response_content


@app.route('/task-state/<task_id>')
def task_state(task_id):
    task = celery.AsyncResult(task_id)
    return task.state


if __name__ == '__main__':
    app.run()
