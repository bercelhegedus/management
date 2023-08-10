
from flask import Flask, render_template, request, send_file, jsonify, make_response
from dataentry_app import dataentry_blueprint
from update_app import update_blueprint

app = Flask(__name__)

app.register_blueprint(dataentry_blueprint)
app.register_blueprint(update_blueprint)

@app.route('/')
def landing():
    return render_template('landing_index.html')

if __name__ == '__main__':
    app.run(debug=True)
