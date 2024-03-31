
"""
Flask route that returns json status response
"""
from flask import Flask , jsonify
from models import storage
from api.v1.views import app_views
import os
from werkzeug.exceptions import NotFound

app = Flask(__name__)
app.register_blueprint(app_views)

@app.teardown_appcontext
def teardown_appcontext(exception):
    storage.close()

@app.errorhandler(NotFound)
def handle_not_found(error):
    """Handler for 404 Not Found errors"""
    response = jsonify({"error": "Not found"})
    response.status_code = 404
    return response

if __name__ == "__main__":
    host = os.getenv('HBNB_API_HOST', '0.0.0.0')
    port = os.getenv('HBNB_API_PORT', 5000)
    app.run(host='0.0.0.0', port=5000)
    app.run(host=host, port=port, threaded=True)