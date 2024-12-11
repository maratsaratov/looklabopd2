"""
This script runs the OPD2 application using a development server.
"""

from os import environ
from OPD2 import app
from outfit_display import get_random_outfit, plot_outfit

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, debug=True)
    
