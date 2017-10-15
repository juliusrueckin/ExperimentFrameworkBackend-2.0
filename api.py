from bottle import request, response, hook
from bottle import post, get, put, delete, route
import re, json
from main import Experiment

@route('/<:re:.*>', method='OPTIONS')
def enable_cors_generic_route():
    """
    This route takes priority over all others. So any request with an OPTIONS
    method will be handled by this function.

    See: https://github.com/bottlepy/bottle/issues/402

    NOTE: This means we won't 404 any invalid path that is an OPTIONS request.
    """
    add_cors_headers()

@hook('after_request')
def enable_cors_after_request_hook():
    """
    This executes after every route. We use it to attach CORS headers when
    applicable.
    """
    add_cors_headers()

def add_cors_headers():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = \
        'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = \
        'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@post('/start_experiment')
def start_experiment():
	#starts new experiment series
	print(request.json)
	try:
		# parse input data
		try:
			data = request.json
		except:
			raise ValueError

		if data is None:
			raise ValueError

		#check whether input data includes amount of repetitions and basic config file
		if 'configFilePath' not in data.keys():
			raise ValueError('config file path required as parameters')

	except ValueError:
		# if bad request data, return 400 Bad Request
		response.status = 400
		return

	except KeyError:
		# if name already exists, return 409 Conflict
		response.status = 409
		return

	config = json.load(open(data['configFilePath'],"r"))
	experiment = Experiment(config)
	experiment.run_experiment()
    
	# return 200 Success
	response.headers['Content-Type'] = 'application/json'
	return json.dumps({'status': 'STARTED'})