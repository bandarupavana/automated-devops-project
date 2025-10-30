from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    # Get the environment variable set in the Deployment
    # Use environment variable PORT if available, otherwise default to 8080
    version = os.environ.get('APP_VERSION', '1.0')
    return f'<h1>Hello from the Automated DevOps Pipeline!</h1><p>Application Version: {version}</p>'

if __name__ == '__main__':
    # Using 8080 for GKE standard practice, matching the YAML targetPort
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
