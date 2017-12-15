import os
import flask
from flask import send_from_directory
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename
from flask import jsonify
import time

LOCAL_FOLDER = '/file'
ALLOWED_EXTENSIONS = set(['txt'])

# directory mapping
directory = {}
''' 
    /dir1/               f0
    /dir1/dir2           f1, f2
    /dir1/dir2/dir3      f3, f4, f5
    {
        'dir1':{
            'files':['f0'],
            'dir2':{
                'files':['f1','f2'],
                'dir3':{
                    'files':['f3','f4','f5']
                }
            }
        }
    }
'''
# in-memory cache
cachefile = {}

app = Flask(__name__)

# create the file under path
@app.route("/find", methods=['GET', 'POST'])
def find():
    if request.method == 'POST':

        payload = request.get_json(force=True)
        
        try:
            fpath = payload['fpath']
            filename = payload['fname']

            if not fpath.startswith('/'):
                raise Exception('invalid path: '+path)

            # extract all the sub dirs
            subdirs = [x for x in fpath.split('/') if len(x.strip())>0]
            curdir = directory
            while subdirs:
                thisdir = subdirs.pop(0)
                if thisdir not in curdir:
                    directory[thisdir]={}
                curdir = directory[thisdir]
                # end of the path
                if not subdirs:
                    if 'files' not in curdir:
                        curdir['files'] = []
                    if filename in curdir['files']:
                        raise Exception('file name '+filename+' exists for path '+fpath)
                    curdir['files'].append(filename)
                    return jsonify({"response":"OK", "response_code": 200})
        except Exception as e:
            return jsonify({"response": str(e)+", error in directory service", "response_code": 500})
    return jsonify({"response":"Error", "response_code": 200})

@app.route("/", methods=['GET', 'POST'])
def hello():
    return jsonify({'response':'ok', 'response_code': 200})


if __name__ == "__main__":
    # enable multi-threading for flask
    app.run(host='0.0.0.0', port=5001, threaded=True, debug=True)