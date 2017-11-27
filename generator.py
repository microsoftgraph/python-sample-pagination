"""pagination sample for Microsoft Graph"""
# Copyright (c) Microsoft. All rights reserved. Licensed under the MIT license.
# See LICENSE in the project root for license information.
import os

import bottle
import graphrest

import config

# create a Graph session object
MSGRAPH = graphrest.GraphSession(client_id=config.CLIENT_ID,
                                 client_secret=config.CLIENT_SECRET,
                                 redirect_uri=config.REDIRECT_URI,
                                 scopes=['User.Read', 'Mail.Read'])

bottle.TEMPLATE_PATH = ['./static/templates']

@bottle.route('/')
@bottle.view('homepage.html')
def homepage():
    """Render the home page."""

    return {'title': 'Pythonic Generator'}

@bottle.route('/login')
def login():
    """Prompt user to authenticate."""
    MSGRAPH.login(login_redirect='/generator')

@bottle.route('/login/authorized')
def authorized():
    """Handler for the application's Redirect Uri."""
    MSGRAPH.redirect_uri_handler()

@bottle.route('/generator')
@bottle.view('generator.html')
def generator():
    """Example of using a Python generator to return paginated data."""
    return {'graphdata': next(MSG_GENERATOR)}

def messages(msgraph, mailfolder=None):
    """Generator to return messages from a specified folder.
    msgraph = authenticated Graph session object
    mailfolder = name or id of mail folder; for example, 'inbox' or a
                120-character ID value. If not specified, ALL messages
                are returned, using the me/messages endpoint.
    """
    next_page = 'me/mailFolders/' + mailfolder + '/messages' if mailfolder else 'me/messages'
    while next_page:
        response = msgraph.get(next_page).json()
        for msg in response.get('value', None):
            yield msg
        next_page = response.get('@odata.nextLink', None)

@bottle.route('/static/<filepath:path>')
def server_static(filepath):
    """Handler for static files, used with the development server."""
    root_folder = os.path.abspath(os.path.dirname(__file__))
    return bottle.static_file(filepath, root=os.path.join(root_folder, 'static'))

if __name__ == '__main__':
    MSG_GENERATOR = messages(MSGRAPH, 'inbox')
    bottle.run(app=bottle.app(), server='wsgiref', host='localhost', port=5000)
