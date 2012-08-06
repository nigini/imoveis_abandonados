import urllib2
import json

from flask import Flask
from flask import render_template

import default_settings as settings


app = Flask(__name__)
app.config.from_object(settings)


@app.route('/')
def index():
    
    pybossa_host = app.config['PYBOSSA_HOST']
    pybossa_port = app.config['PYBOSSA_PORT']
    pybossa_server = 'http://%s:%d' %(pybossa_host, pybossa_port)
    pybossa_app = app.config['PYBOSSA_APP']
    
    data = json.load(urllib2.urlopen(pybossa_server+'/api/app?short_name='+pybossa_app))
    app_id = data[0]['id']
    data = json.load(urllib2.urlopen("%s%s%d" %(pybossa_server,'/api/task?app_id=',app_id)))
    
    coords = []
    for task in data:
        coords.append({"task":task["id"],
            "lat":task["info"]["coord"]["lat"],
            "lon":task["info"]["coord"]["lon"]})
    return render_template('index.html',app=pybossa_app,coords=json.dumps(coords))


@app.route('/info/<int:task_id>')
def info(task_id):

    pybossa_host = app.config['PYBOSSA_HOST']
    pybossa_port = app.config['PYBOSSA_PORT']
    pybossa_server = 'http://%s:%d' %(pybossa_host, pybossa_port)
    pybossa_app = app.config['PYBOSSA_APP']
    
    task_data = json.load(urllib2.urlopen(pybossa_server+'/api/task?id=%d' %(task_id)))
    address = task_data[0]["info"]["coord"]["add"]

    answers_data = json.load(urllib2.urlopen(pybossa_server+'/api/taskrun?id=%d' %(task_id)))
    size = len(answers_data)
    photo = None
    if size>0:
        photo = answers_data[size-1]["info"]["pictureurl"]
    return render_template('info.html', address=address, photo=photo, task_id=task_id)


if __name__ == '__main__':
    app.run(debug=True, host=app.config['HOST'], port=app.config['PORT'])
