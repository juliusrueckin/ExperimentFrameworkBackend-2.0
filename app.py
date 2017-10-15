import bottle
from bottle import request, response, hook
from bottle import post, get, put, delete
import re, json
import api

app = application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(host = '127.0.0.1', port = 8080)