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


def calculate_auth0_metrics(event, context):

    ddb = ddb_utils.Dynamodb(stack_name=STACK_NAME)

    s_events = ddb.query(
            table_name=AUTH0_EVENTS_TABLE_NAME,
            KeyConditionExpression='type = :type',
            ExpressionAttributeValues={
                ':type': 's',
            }
        )

    return s_events

    # return {
    #     "statusCode": HTTPStatus.OK,
    # }