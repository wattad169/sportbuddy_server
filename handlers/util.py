from constants import *
import json


def to_json(query):
	return [dict(p.to_dict(exclude=['added_on']), **dict(id=p.key.id())) for p in query]



def create_response(status,response_body):
	result = {}
	if(status==OK):
		result[STATUS] = OK
	else:
		result[STATUS] = NOK

	result[MESSAGE] = response_body

	return json.dumps(result)
