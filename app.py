import os
from icecream import ic
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

from api.route import api

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")


if  __name__ == '__main__':
    app.run(debug=True, port=2424)
