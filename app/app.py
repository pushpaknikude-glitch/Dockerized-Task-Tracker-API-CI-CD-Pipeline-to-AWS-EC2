from flask import Flask, jsonify, request
import redis
import os
import json

app = Flask(__name__)

redis_host = os.environ.get('REDIS_HOST', 'redis')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

TASKS_KEY = 'tasks'


@app.route('/')
def home():
    return jsonify({
        'message': 'Task Tracker API is running',
        'endpoints': {
            'GET /health': 'check service health',
            'GET /tasks': 'list all tasks',
            'POST /tasks': 'create a task, body: {"title": "..."}',
            'DELETE /tasks/<id>': 'delete a task'
        }
    })


@app.route('/health')
def health():
    try:
        r.ping()
        return jsonify({'status': 'healthy', 'redis': 'connected'}), 200
    except redis.exceptions.ConnectionError:
        return jsonify({'status': 'unhealthy', 'redis': 'disconnected'}), 503


@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = r.hgetall(TASKS_KEY)
    result = [{'id': k, **json.loads(v)} for k, v in tasks.items()]
    return jsonify(result), 200


@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json(silent=True)
    if not data or 'title' not in data:
        return jsonify({'error': 'title is required'}), 400

    task_id = str(r.incr('task_id_counter'))
    task = {'title': data['title'], 'done': False}
    r.hset(TASKS_KEY, task_id, json.dumps(task))
    return jsonify({'id': task_id, **task}), 201


@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    deleted = r.hdel(TASKS_KEY, task_id)
    if deleted:
        return jsonify({'message': f'Task {task_id} deleted'}), 200
    return jsonify({'error': 'Task not found'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
