# app.py
"""
Main entry point for the Flask application.
Reference: Flask Application Factory Pattern - https://flask.palletsprojects.com/en/2.2.x/patterns/appfactories/
"""
from flask import Flask
from routes import bp

app = Flask(__name__)
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)
