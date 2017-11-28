"""Pagination sample for Microsoft Graph."""
# Copyright (c) Microsoft. All rights reserved. Licensed under the MIT license.
# See LICENSE in the project root for license information.
import os

import bottle
import graphrest

import config


# Create a Graph session object.
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
    """Handler for the application's Redirect URI."""
    MSGRAPH.redirect_uri_handler()


@bottle.route('/generator')
@bottle.view('generator.html')
def generator():
    """Example of using a Python generator to return items from paginated data."""
    # Priming the iterator.
    return {'graphdata': next(MSG_GENERATOR)}


def graph_generator(session, endpoint=None):
    """Generator for paginated result sets returned by Microsoft Graph.

    session = authenticated Graph session object
    endpoint = the Graph endpoint (for example, 'me/messages' for messages,
               or 'me/drive/root/children' for OneDrive drive items)
    """
    while endpoint:
        print('Retrieving next page ...')
        response = session.get(endpoint).json()
        yield from response.get['value']
        endpoint = response.get('@odata.nextLink')


@bottle.route('/static/<filepath:path>')
def server_static(filepath):
    """Handler for static files, used with the development server."""
    root_folder = os.path.abspath(os.path.dirname(__file__))
    return bottle.static_file(filepath, root=os.path.join(root_folder, 'static'))


if __name__ == '__main__':
    # To return messages from folder foldername, use this endpoint instead:
    # 'me/mailFolders/foldername/messages'
    MSG_GENERATOR = graph_generator(MSGRAPH, 'me/messages')
    bottle.run(app=bottle.app(), server='wsgiref', host='localhost', port=5000)
