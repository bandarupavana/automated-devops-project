# app.py
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    # Get the environment variable set in the Dockerfile/Deployment
    version = os.environ.get('APP_VERSION', '1.0')
    return f'<h1>Hello from the Automated DevOps Pipeline!</h1><p>Application Version: {version}</p>'

if __name__ == '__main__':
    # Listen on 0.0.0.0 for Docker to work correctly
    app.run(host='0.0.0.0', port=5000)