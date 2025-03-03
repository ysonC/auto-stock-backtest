from flask import Flask, render_template    
from app.api.api_functions import api  # Import the API blueprint

from app.app_logging import setup_logging

app = Flask(__name__, static_folder='static', template_folder='templates')

# Register the API blueprint
app.register_blueprint(api, url_prefix="/api")

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    setup_logging(debug_mode=True)
    app.run(debug=True)
