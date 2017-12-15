import os
import flask
from flask import send_from_directory
from flask import Flask, request, redirect, url_for
from flask import jsonify
import time
import requests
import json
import uuid

UPLOAD_FOLDER = '/fs'
ALLOWED_EXTENSIONS = set(['txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/write", methods=['GET', 'POST'])
def write():
    # check if the post request has the file part
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify('No file part')
        try:    

            fpath = request.form['path']
            file = request.files['file']

            if not fpath or not file:
                raise Exception('missing either file path or file name in the input')
            if file:
                if file.filename == '':
                    return jsonify('error, empty filename')
                filename = file.filename
                fileinfo = {"fpath": fpath, "fname": filename}

                response = requests.post('http://directory:5001/find', data=json.dumps(fileinfo))
                response = response.json()
                
                if response['response_code'] == 200 and response['response'] =='OK':
                    # save into file
                    fileid = str(uuid.uuid4())
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], fileid))
                    return jsonify({'response':fileid, 'response_code':200, 'filename': filename, 'path':fpath})
                else:
                    raise Exception(response['response'])
        except Exception as e:
            return jsonify({'response': str(e), 'ssresponse_code': 500})
        except:
            return jsonify({'response':'other error', 'response_code': 500})

    return jsonify({'response_code':200, 'response':'error'})


@app.route('/update', methods=['GET', 'POST'])
def update():
    return jsonify('200, update')


@app.route('/test')
def test():
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(UPLOAD_FOLDER) if isfile(join(UPLOAD_FOLDER, f))]
    return str(onlyfiles)

@app.route('/read', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(flask.current_app.root_path, app.config['UPLOAD_FOLDER'])
    return flask.send_from_directory(directory=uploads, filename=filename)


if __name__ == "__main__":
    # enable multi-threading for flask
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)



