from flask import Flask


def create_app(): # izveido Flask instanci un padot to uz main.py
    app = Flask(__name__)
    return app