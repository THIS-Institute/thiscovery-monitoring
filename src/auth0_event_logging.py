#
#   Thiscovery API - THIS Institute’s citizen science platform
#   Copyright (C) 2020 THIS Institute
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   A copy of the GNU Affero General Public License is available in the
#   docs folder of this project.  It is also available www.gnu.org/licenses/
#

import json
import time
from http import HTTPStatus
import thiscovery_lib.utilities as utils
from thiscovery_lib import dynamodb_utilities as ddb_utils
# import src.common.constants as constants

AUTH0_EVENTS_TABLE_NAME = 'Auth0Events'


class Auth0Event:

    def __init__(self, event):
        # self.logger = utils.get_logger()

        self.event_item = {
            'type': 's',
            'user_name': "andy.paterson@mac.com",
            'date': "2020-12-07T19:45:35.657Z",
        }

        self.event = event
        self.type = 's'


    def save_event(self):
        ddb = ddb_utils.Dynamodb(stack_name='thiscovery-monitoring')
        ddb.put_item(AUTH0_EVENTS_TABLE_NAME, self.type, self.type, self.event, self.event_item, True, None, 'type')


@utils.lambda_wrapper
@utils.api_error_handler
def test(event, context):
    e = Auth0Event({'k1': 'v1'})
    e.save_event()


@utils.lambda_wrapper
@utils.api_error_handler
def persist_auth0_event(event, context):
    pass
    # logger = event['logger']
    # correlation_id = event['correlation_id']
    #
    # params = event['queryStringParameters']
    # user_id = str(utils.validate_uuid(params['user_id']))
    # logger.info('API call', extra={'user_id': user_id, 'correlation_id': correlation_id, 'event': event})
    # if user_id == '760f4e4d-4a3b-4671-8ceb-129d81f9d9ca':
    #     raise ValueError('Deliberate error raised to test error handling')
    # return {
    #     "statusCode": HTTPStatus.OK,
    #     "body": json.dumps(get_project_status_for_user(user_id, correlation_id))
    # }


@utils.lambda_wrapper
@utils.api_error_handler
def log_request_api(event, context):
    logger = event['logger']

    # params = event['queryStringParameters']
    # body = event['body']
    logger.info('API call', extra={'event': event})
    return {
        "statusCode": HTTPStatus.OK,
    }