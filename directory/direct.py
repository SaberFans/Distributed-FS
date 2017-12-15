import os
import flask
from flask import Flask, request, redirect, url_for

from flask import jsonify
import threading
import requests
import json
import uuid

# very coarse grained lock for atomic operation
writeLock = threading.Lock()

cacheLock = threading.Lock()

# directory mapping
directory = {}

# local fs
UPLOAD_FOLDER = '/fs'

# file name mapping
'''
FILE_NAME_MAP is mapping bewteen pathtofilename and file uuid 

'''
FILE_NAME_MAP = {}

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

app = Flask(__name__)

# create the file under path
@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        payload = request.get_json(force=True)
        try:
            fpath = payload['fpath']
            filename = payload['fname']
            fcontent = payload['fcontent']
            if not fpath.startswith('/'):
                raise Exception('invalid path: '+path)

            # extract all the sub dirs
            subdirs = [x for x in fpath.split('/') if len(x.strip())>0] 
            curdir = directory
            aggdir = '' 
 
            # lock the directory update to eliminate race condition
            with writeLock:

                print(threading.current_thread())
                print(str(writeLock))  
                while subdirs:
                    thisdir = subdirs.pop(0)
                    if thisdir not in curdir:
                        curdir[thisdir]={}

                    aggdir = aggdir+ '/' +thisdir
                    curdir = curdir[thisdir]

                    # end of the path
                    if not subdirs:
                        if 'files' not in curdir:
                            curdir['files'] = [] 
                        if filename in curdir['files']:
                            return jsonify({'response':'FileExists', 'response_code':400, 'filename':filename, 'path':aggdir, 'directory':directory})
                        # append into directory
                        curdir['files'].append(filename)

                        # write into disk
                        fileid = str(uuid.uuid4())
                        with open(os.path.join(UPLOAD_FOLDER, fileid), 'w') as the_file:
                            the_file.write(fcontent)
                        
                        # update the local mapping
                        FILE_NAME_MAP[aggdir] = fileid

                        # update in the cache server                        
                        fileinfo = {'fcontent': fcontent, 'filepath': aggdir+'/'+filename}
                        response = requests.post('http://cache:5002/put', data=json.dumps(fileinfo))
                        # response = (response.json()) 
                        return jsonify({"response":"OK", "response_code": 200, 'filepath':aggdir+'/'+filename})
        except Exception as e:
            return jsonify({"response": str(e)+", error in directory service", "response_code": 500, 'directory':directory})
    return jsonify({"response":"Error", "response_code": 200})

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
            aggdir = '' 
            while subdirs:
                thisdir = subdirs.pop(0)
                aggdir = aggdir+ '/' +thisdir
                # dir not exist
                if thisdir not in curdir:
                    return jsonify({'response':'DirNotExists', 'response_code':200, 'filename':filename, 'path':aggdir, 'directory':directory})

                curdir = curdir[thisdir] 
                # end of the path
                if not subdirs:
                    if filename not in curdir['files']:
                        return jsonify({'response':'FileNotExists', 'response_code':400, 'filename':filename, 'path':aggdir, 'directory':directory})
                    else:

                        # load in from cache
                        fileinfo = {'filepath': aggdir+'/'+filename}
                        response = requests.post('http://cache:5002/fetch', data=json.dumps(fileinfo))
                        response = response.json()
                    
                        if response['response']=='InCache':
                            return jsonify(response)
                        elif response['response']=='NotInCache':
                            # read from disk
                            fileid = FILE_NAME_MAP[aggdir]
                            with open(os.path.join(UPLOAD_FOLDER, fileid), 'r') as the_file:
                                fileContent = the_file.read()
                                # load into cache
                                fileinfo['fcontent'] = fileContent
                                response = requests.post('http://cache:5002/put', data=json.dumps(fileinfo))
                                
                                return jsonify({'response':'LoadInDisk','response_code':200, 'filename':filename, 'path':aggdir, 'fileContent': fileContent})
                        # if response['response']=='InCahe':
                        #     return jsonify({'response':'InCache', 'response_code':200, 'filename':filename, 'path':aggdir, 'filecontent': response['filecontent'], 'directory':directory}) 
                        # return jsonify({'response':'FileExists', 'response_code':200, 'filename':filename, 'path':aggdir, 'filecontent': response['filecontent'], 'directory':directory}) 
        except Exception as e:
            return jsonify({"response": str(e)+", error in directory service", "response_code": 500, 'directory':directory})
    return jsonify({"response":"Error", "response_code": 200})

@app.route("/", methods=['GET', 'POST'])
def hello():
    return jsonify(directory)

@app.route('/fs')
def fs():
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(UPLOAD_FOLDER) if isfile(join(UPLOAD_FOLDER, f))]
    return str(onlyfiles)


if __name__ == "__main__":
    # enable multi-threading for flask
    app.run(host='0.0.0.0', port=5001, threaded=True, debug=True)