import os
import flask
from flask import Flask, request, redirect, url_for
from flask import jsonify

LOCAL_FOLDER = '/file'
ALLOWED_EXTENSIONS = set(['txt'])

# in-memory cache
cachefile = {}
'''
    {
        'pathtofile':'filecontent',
        ...

    }
    this in memory cache will only be modified by directory service
    there's a write lock in directory service to avoid race condition
'''

app = Flask(__name__)


@app.route("/fetch", methods=['GET', 'POST'])
def fetch():
    if request.method == 'POST':
        payload = request.get_json(force=True)
        if payload['filepath'] in cachefile:
            return jsonify({'response':'InCache','response_code':200, 'filepath': payload['filepath'], 'filecontent': cachefile[payload['filepath']]})
        else:
            return jsonify({'response':'NotInCache', 'response_code':200, 'filepath': payload['filepath']})
    return jsonify('OK, 200')

@app.route("/put", methods=['GET', 'POST'])
def put():
    if request.method == 'POST':
        payload = request.get_json(force=True)
        cachefile[payload['filepath']] = payload['fcontent']
        return jsonify({'filepath': payload['filepath'], 'filecontent': cachefile[payload['filepath']]})
        
    return jsonify('OK, 200')
@app.route("/")
def list():
    return jsonify(cachefile)

@app.route("/clear")
def clear():
    global cachefile
    cachefile = {}
    return jsonify(cachefile)

if __name__ == "__main__":
    # enable multi-threading for flask
    app.run(host='0.0.0.0', port=5002, threaded=True, debug=True)