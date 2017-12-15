import os
import flask
from flask import send_from_directory
from flask import Flask, request, redirect, url_for
from flask import jsonify
import time
import requests
import json


app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/read", methods=['GET', 'POST'])
def read():
    # check if the post request has the file part
    if request.method == 'POST':
        try:    
            fpath = request.form['filepath']
            fname = request.form['filename']

            fileinfo = {"fpath": fpath, "fname": fname}

            response = requests.post('http://directory:5001/find', data=json.dumps(fileinfo))
            
            response = response.json()  
            
            return jsonify(response)

        except Exception as e:
            return jsonify({'response': str(e), 'ssresponse_code': 500})
        except:
            return jsonify({'response':'other error', 'response_code': 500})

    return jsonify({'response_code':200, 'response':'error'})
@app.route("/write", methods=['GET', 'POST'])
def write():
    # check if the post request has the file part
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify('No file part')
        try:    

            fpath = request.form['path']
            file = request.files['file']
            fileContent = str(file.read())

            if not fpath or not file:
                raise Exception('missing either file path or file name in the input')
            if file:

                if file.filename == '':
                    return jsonify('error, empty filename')

                filename = file.filename
                fileinfo = {"fpath": fpath, "fname": filename,"fcontent": fileContent}
                
                response = requests.post('http://directory:5001/add', data=json.dumps(fileinfo))   

                response = response.json()
                return jsonify(response)
                if response['response_code'] == 200 and esponse['response'] =='OK':
                    return jsonify({'response':'Write Sucess', 'response_code':200, 'filename': filename, 'path':fpath})
        except Exception as e:
            return jsonify({'response': str(e), 'ssresponse_code': 500})
        except:
            return jsonify({'response':'other error', 'response_code': 500})

    return jsonify({'response_code':200, 'response':'error'})

@app.route('/update', methods=['GET', 'POST'])
def update():
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
                
                if response['response_code'] == 200:
                    if response['response'] =='FileNotExists':
                        raise Exception('file not exists')
                    elif response['response'] == 'FileExists':
                        return jsonify(response)
                    else:    
                        raise Exception('some other error')
        except Exception as e:
            return jsonify({'response': str(e), 'ssresponse_code': 500})
        except:
            return jsonify({'response':'other error', 'response_code': 500})

    return jsonify({'response_code':200, 'response':'error'})



if __name__ == "__main__":
    # enable multi-threading for flask
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)



