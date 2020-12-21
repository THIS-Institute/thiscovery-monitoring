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
STACK_NAME = 'thiscovery-monitoring'


class Auth0Event:

    def __init__(self, event):
        # self.logger = utils.get_logger()

        # id, date and type will be present in every event, user_name may not be present for some events
        id = event['id']
        detail_data = event['detail']['data']
        event_date = detail_data['date'].replace('T',' ').replace('Z','')
        event_type = detail_data['type']
        if 'user_name' in detail_data:
            user_name = detail_data['user_name']
        else:
            user_name = 'unknown'

        self.event_item = {
            'id': id,
            'event_date': event_date,
            'event_type': event_type,
            'user_name': user_name,
        }

        self.event = event
        self.event_type = event_type


    def save_event(self):
        ddb = ddb_utils.Dynamodb(stack_name=STACK_NAME)
        ddb.put_item(AUTH0_EVENTS_TABLE_NAME, self.event_type, self.event_type, self.event, self.event_item, True, None, 'event_type')


@utils.lambda_wrapper
@utils.api_error_handler
def test(event, context):
    e = Auth0Event({'k1': 'v1'})
    e.save_event()


# @utils.api_error_handler
def persist_auth0_event(event, context):

    e = Auth0Event(event)
    e.save_event()

    return {
        "statusCode": HTTPStatus.OK,
    }


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