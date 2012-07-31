#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of PyBOSSA.
#
# PyBOSSA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyBOSSA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyBOSSA.  If not, see <http://www.gnu.org/licenses/>.

import urllib
import urllib2
import json
import re
import string
from optparse import OptionParser


def delete_app(api_url, api_key, id):
    request = urllib2.Request(api_url + '/api/app/' + str(id) + \
                              '?api_key=' + api_key)
    request.get_method = lambda: 'DELETE'

    if (urllib2.urlopen(request).getcode() == 204):
        return True
    else:
        return False


def update_app(api_url, api_key, id, name=None):
    data = dict(id=id, name=name)
    data = json.dumps(data)
    request = urllib2.Request(api_url + '/api/app/' + str(id) + \
                              '?api_key=' + api_key)
    request.add_data(data)
    request.add_header('Content-type', 'application/json')
    request.get_method = lambda: 'PUT'

    if (urllib2.urlopen(request).getcode() == 200):
        return True
    else:
        return False


def create_app(api_url, api_key, name=None, short_name=None,
               description=None):
    
    print('Creating app')
    name = u'Imoveis Abandonados'  # Name with a typo
    short_name = u'abandonados'
    description = u'Dados sobre o imovel'
    # JSON Blob to present the tasks for this app to the users
    # First we read the template:
    file = open('template.html')
    text = file.read()
    file.close()
    # HTML Blob with a long description for the application
    file = open('long_description.html')
    long_description = file.read()
    file.close()
    info = dict(task_presenter=text,sched="incremental")
    data = dict(name=name, short_name=short_name, description=description,
                long_description=long_description,
                hidden=0, info=info)
    data = json.dumps(data)

    # Checking which apps have been already registered in the DB
    apps = json.loads(urllib2.urlopen(api_url + '/api/app' + \
                      '?api_key=' + api_key).read())
    for app in apps:
        if app['short_name'] == short_name:
            print('{app_name} app is already registered in the DB'\
                    .format(app_name=name))
            print('Deleting it!')
            if (delete_app(api_url, api_key, app['id'])):
                print "Application deleted!"
    print("The application is not registered in PyBOSSA. Creating it...")
    # Setting the POST action
    request = urllib2.Request(api_url + '/api/app?api_key=' + api_key)
    request.add_data(data)
    request.add_header('Content-type', 'application/json')

    # Create the app in PyBOSSA
    output = json.loads(urllib2.urlopen(request).read())
    if (output['id'] != None):
        print("Done!")
        print("Ooooops! the name of the application has a typo!")
        print("Updating it!")
        if (update_app(api_url, api_key, output['id'],
            "")):
            print "Application name fixed!"
            return output['id']
        else:
            print "An error has occurred"
    else:
        print("Error creating the application")
        return 0


def create_task(api_url, api_key, app_id, n_answers, coords=None):
    """
    Creates tasks for the application

    :arg integer app_id: Application ID in PyBossa.
    :returns: Task ID in PyBossa.
    :rtype: integer
    """
    # Data for the tasks
    coords = {"lat":"-23.54066","lon":"-46.64124"}
    
    info = dict(question="Imovel abandonado?",
                   n_answers=int(n_answers), coords=coords)

    data = dict(app_id=app_id, state=0, info=info,
                 calibration=0, priority_0=0)

    data = json.dumps(data)

    # Setting the POST action
    request = urllib2.Request(api_url + '/api/task' + '?api_key=' + api_key)
    request.add_data(data)
    request.add_header('Content-type', 'application/json')

    # Create the task
    output = json.loads(urllib2.urlopen(request).read())
    if (output['id'] != None):
        return True
    else:
        return False


def update_template(api_url, api_key, app='abandonados'):
    """

    :arg string app: Application short_name in PyBossa.
    :returns: True when the template has been updated.
    :rtype: boolean
    """
    request = urllib2.Request('%s/api/app?short_name=%s' %
                              (api_url, app))
    request.add_header('Content-type', 'application/json')

    res = urllib2.urlopen(request).read()
    res = json.loads(res)
    res = res[0]
    if res.get('short_name'):
        # Re-read the template
        file = open('template.html')
        text = file.read()
        file.close()
        # Re-read the long_description
        file = open('long_description.html')
        long_desc = file.read()
        file.close()
        info = dict(task_presenter=text,sched="incremental")
        data = dict(id=res['id'], name=res['name'],
                    short_name=res['short_name'],
                    description=res['description'], hidden=res['hidden'],
                    long_description=long_desc,
                    info=info)
        data = json.dumps(data)
        request = urllib2.Request(api_url + '/api/app/' + str(res['id']) + \
                                  '?api_key=' + api_key)
        request.add_data(data)
        request.add_header('Content-type', 'application/json')
        request.get_method = lambda: 'PUT'

        if (urllib2.urlopen(request).getcode() == 200):
            return True
        else:
            return False

    else:
        return False


def update_tasks(api_url, api_key, app='abandonados'):
    """
    Update tasks question

    :arg string app: Application short_name in PyBossa.
    :returns: True when the template has been updated.
    :rtype: boolean
    """
    request = urllib2.Request('%s/api/app?short_name=%s' %
                              (api_url, app))
    request.add_header('Content-type', 'application/json')

    res = urllib2.urlopen(request).read()
    res = json.loads(res)
    app = res[0]
    if app.get('short_name'):
        request = urllib2.Request('%s/api/task?app_id=%s&limit=%s' %
                                  (api_url, app['id'], 1000))
        request.add_header('Content-type', 'application/json')

        res = urllib2.urlopen(request).read()
        tasks = json.loads(res)

        for t in tasks:
            t['info']['question'] = u'Do you see a human in this photo?'
            data = dict(info=t['info'], app_id=t['app_id'])
            data = json.dumps(data)
            request = urllib2.Request(api_url + '/api/task/' + str(t['id']) + \
                                      '?api_key=' + api_key)
            request.add_data(data)
            request.add_header('Content-type', 'application/json')
            request.get_method = lambda: 'PUT'

            if (urllib2.urlopen(request).getcode() == 200):
                print "Task ID: %s  updated" % t['id']
            else:
                return False

    else:
        return False


def get_coords():
    #TODO: add some code here to get coords from the web interface
    return None


if __name__ == "__main__":
    # Arguments for the application
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    # URL where PyBossa listens
    parser.add_option("-u", "--url", dest="api_url",
                      help="PyBossa URL http://domain.com/", metavar="URL")
    # API-KEY
    parser.add_option("-k", "--api-key", dest="api_key",
                      help="PyBossa User API-KEY to interact with PyBossa",
                      metavar="API-KEY")
    # Create App
    parser.add_option("-c", "--create-app", action="store_true",
                      dest="create_app",
                      help="Create the application",
                      metavar="CREATE-APP")
    # Update template for tasks and long_description for app
    parser.add_option("-t", "--update-template", action="store_true",
                      dest="update_template",
                      help="Update Tasks template",
                      metavar="UPDATE-TEMPLATE"
                     )

    # Update tasks question
    parser.add_option("-q", "--update-tasks", action="store_true",
                      dest="update_tasks",
                      help="Update Tasks question",
                      metavar="UPDATE-TASKS"
                     )

    parser.add_option("-x", "--extra-task", action="store_true",
                      dest="add_more_tasks",
                      help="Add more tasks",
                      metavar="ADD-MORE-TASKS"
                      )
    # Modify the number of TaskRuns per Task
    # (default 30)
    parser.add_option("-n", "--number-answers",
                      dest="n_answers",
                      help="Number of answers per task",
                      metavar="N-ANSWERS"
                     )

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose")
    (options, args) = parser.parse_args()

    if not options.api_url:
        options.api_url = 'http://localhost:5000/'

    if not options.api_key:
        parser.error("You must supply an API-KEY to create an \
                      application and tasks in PyBossa")

    if (options.verbose):
        print('Running against PyBosssa instance at: %s' % options.api_url)
        print('Using API-KEY: %s' % options.api_key)

    if options.create_app:
        app_id = create_app(options.api_url, options.api_key)
        
        create_task(options.api_url, options.api_key, app_id, 30)
        
        
    else:
        if options.add_more_tasks:
            request = urllib2.Request('%s/api/app?short_name=%s' %
                                      (options.api_url, 'abandonados'))
            request.add_header('Content-type', 'application/json')

            app = urllib2.urlopen(request).read()
            app = json.loads(app)
            app = app[0]
            #TODO: call get_taskinfo and create task

    if options.update_template:
        print "Updating app template"
        update_template(options.api_url, options.api_key)

    if options.update_tasks:
        print "Updating task question"
        update_tasks(options.api_url, options.api_key)

    if not options.create_app and not options.update_template\
            and not options.add_more_tasks:
        parser.error("Please check --help or -h for the available options")
