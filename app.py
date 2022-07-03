from flask import Flask, jsonify
from flask_cors import CORS
from tracking import get_status_from_code

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

@app.route('/tracking/<code>', methods=['GET'])
def get_tracking_status(code):
    response = { 'message':  get_status_from_code(code) }

    return jsonify(response)

if __name__ == '__main__':
    app.run(port=5000)