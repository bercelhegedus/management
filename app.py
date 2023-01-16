from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

class TaskCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<TaskCategory %r>' % self.name

class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)

    def __init__(self, name, email, expiry_date):
        self.name = name
        self.email = email
        self.expiry_date = expiry_date

    def __repr__(self):
        return '<People %r>' % self.name

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    task_category_id = db.Column(db.Integer, db.ForeignKey('task_category.id'), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    date_created = db.Column(db.String(255), nullable=False)

    def __init__(self, name, task_category_id, people_id, date_created):
        self.name = name
        self.task_category_id = task_category_id
        self.people_id = people_id
        self.date_created = date_created

    def __repr__(self):
        return '<Task %r>' % self.name

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    task_category_id = db.Column(db.Integer, db.ForeignKey('task_category.id'), nullable=False)
    expiry_date = db.Column(db.String(255), nullable=False)

    def __init__(self, people_id, task_category_id, expiry_date):
        self.people_id = people_id
        self.task_category_id = task_category_id
        self.expiry_date = expiry_date

    def __repr__(self):
        return '<Permission %r>' % self.people_id

@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'GET':
        categories = TaskCategory.query.all()
        return jsonify([category.name for category in categories])
    elif request.method == 'POST':
        name = request.json['name']
        category = TaskCategory(name)
        db.session.add(category)
        db.session.commit()
        return jsonify({'message': 'Task category created'}), 201

@app.route('/people', methods=['GET', 'POST'])
def people():
    if request.method == 'GET':
        people = People.query.all()
        return jsonify([{'name': person.name, 'email': person.email, 'expiry_date': person.expiry_date} for person in people])
    elif request.method == 'POST':
        name = request.json['name']
        email = request.json['email']
        person = People(name, email)
        db.session.add(person)
        db.session.commit()
        return jsonify({'message': 'Person created'}), 201

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'GET':
        tasks = Task.query.all()
        return jsonify([{'name': task.name, 'category': task.category, 'person': task.person, 'date_created': task.date_created} for task in tasks])
    elif request.method == 'POST':
        name = request.json['name']
        task_category_id = request.json['task_category_id']
        people_id = request.json['people_id']
        date_created = request.json['date_created']
        task = Task(name, task_category_id, people_id, date_created)
        db.session.add(task)
        db.session.commit()
        return jsonify({'message': 'Task created'}), 201

@app.route('/permissions', methods=['GET', 'POST'])
def permissions():
    if request.method == 'GET':
        permissions = Permission.query.all()
        return jsonify([{'people': permission.people_id, 'category': permission.category, 'expiry_date': permission.expiry_date} for permission in permissions])
    elif request.method == 'POST':
        people_id = request.json['people_id']
        task_category_id = request.json['task_category_id']
        expiry_date = request.json['expiry_date']
        permission = Permission(people_id, task_category_id, expiry_date)
        db.session.add(permission)
        db.session.commit()
        return jsonify({'message': 'Permission created'}), 201

@app.route('/categories/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def category(id):
    category = TaskCategory.query.get(id)
    if request.method == 'GET':
        return jsonify({'name': category.name})
    elif request.method == 'PUT':
        name = request.json['name']
        category.name = name
        db.session.commit()
        return jsonify({'message': 'Task category updated'})
    elif request.method == 'DELETE':
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Task category deleted'})

@app.route('/people/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def person(id):
    person = People.query.get(id)
    if request.method == 'GET':
        return jsonify({'name': person.name, 'email': person.email, 'expiry_date': person.expiry_date})
    elif request.method == 'PUT':
        name = request.json['name']
        email = request.json['email']
        expiry_date = request.json['expiry_date']
        person.name = name
        person.email = email
        person.expiry_date = expiry_date
        db.session.commit()
        return jsonify({'message': 'Person updated'})
    elif request.method == 'DELETE':
        db.session.delete(person)
        db.session.commit()
        return jsonify({'message': 'Person deleted'})

@app.route('/tasks/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def task(id):
    task = Task.query.get(id)
    if request.method == 'GET':
        return jsonify({'name': task.name, 'category': task.category, 'person': task.person, 'date_created': task.date_created})
    elif request.method == 'PUT':
        name = request.json['name']
        task_category_id = request.json['task_category_id']
        people_id = request.json['people_id']
        date_created = request.json['date_created']
        task.name = name
        task.task_category_id = task_category_id
        task.people_id = people_id
        task.date_created = date_created
        db.session.commit()
        return jsonify({'message': 'Task updated'})
    elif request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted'})

@app.route('/permissions/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def permission(id):
    permission = Permission.query.get(id)
    if request.method == 'GET':
        return jsonify({'people': permission.people_id, 'category': permission.category, 'expiry_date': permission.expiry_date})
    elif request.method == 'PUT':
        people_id = request.json['people_id']
        task_category_id = request.json['task_category_id']
        expiry_date = request.json['expiry_date']
        permission.people_id = people_id
        permission.task_category_id = task_category_id
        permission.expiry_date = expiry_date
        db.session.commit()
        return jsonify({'message': 'Permission updated'})
    elif request.method == 'DELETE':
        db.session.delete(permission)
        db.session.commit()
        return jsonify({'message': 'Permission deleted'})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

