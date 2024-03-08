from flask import Flask, request, jsonify
from models import db, User, Task
from app import app
import random


@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data['title']
    description = data['description']

    users = User.query.all()
    if not users:
        return jsonify({"message": "No users available to assign the task"})
    asignee = random.choice(users)

    task = Task(title=title, description=description, assignee_name=asignee.name)
    db.session.add(task)
    db.session.commit()

    return jsonify({"message": "Task created successfully"})


@app.route('/assign-tasks', methods=['POST'])
def assign_tasks():
    users = User.query.all()
    if not users:
        return jsonify({"message": "No users available"}), 400

    tasks = Task.query.filter_by(is_completed=False).all()
    if not tasks:
        return jsonify({"message": "No tasks to assign"}), 200

    for task in tasks:
        assignee = random.choice(users)
        task.assignee_name = assignee.name
    db.session.commit()

    return jsonify({"message": "All tasks assigned"}), 200


@app.route('/complete-task', methods=['POST'])
def complete_task():
    data = request.get_json()
    task_id = data['id']

    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return jsonify({"message": "Task doesn't exist"}), 404

    task.is_completed = True
    db.session.commit()

    return jsonify({"message": f"Task {task_id} was completed"})


@app.route('/tasks', methods=['GET'])
def get_tasks_by_user():
    assignee = request.args.get('assignee')

    if not assignee:
        return jsonify({"message": "Assignee is required"}), 400

    user = User.query.filter_by(name=assignee).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    tasks = Task.query.filter_by(assignee_name=assignee).all()
    response_body = [{"id": task.id, "title": task.title, "description": task.description, "is_completed": task.is_completed} for task in tasks]

    return jsonify({"tasks": response_body})
