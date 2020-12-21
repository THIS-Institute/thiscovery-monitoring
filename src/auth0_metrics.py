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
import datetime
from http import HTTPStatus
import thiscovery_lib.utilities as utils
from thiscovery_lib import dynamodb_utilities as ddb_utils
# import src.common.constants as constants

AUTH0_EVENTS_TABLE_NAME = 'Auth0Events'
STACK_NAME = 'thiscovery-monitoring'
METRIC_NAMESPACE = 'Authentication'


class CloudWatchMetricsClient(utils.BaseClient):

    def __init__(self):
        super().__init__('cloudwatch')

    def put_metric(self, metric_name, metric_value):
        # Create CloudWatch client

        metric_data = [
                {
                    'MetricName': metric_name,
                    'Dimensions': [
                        {
                            'Name': 'Logins',
                            'Value': 'Last hour'
                        },
                    ],
                    'Unit': 'None',
                    'Value': metric_value
                },
            ]

        # Put custom metrics
        self.client.put_metric_data(
            MetricData=metric_data,
            Namespace=METRIC_NAMESPACE
        )


def calculate_auth0_metrics(event, context):

    time_now = utils.now_with_tz()
    one_hour = datetime.timedelta(hours=1)
    one_hour_ago = time_now - one_hour
    one_hour_ago = one_hour_ago.strftime("%Y-%m-%d %H:%M:%S.%f")

    ddb = ddb_utils.Dynamodb(stack_name=STACK_NAME)

    s_events = ddb.query(
            table_name=AUTH0_EVENTS_TABLE_NAME,
            KeyConditionExpression='event_type = :event_type and event_date > :one_hour_ago',
            ExpressionAttributeValues={
                ':event_type': 's',
                ':one_hour_ago': one_hour_ago,
            }
        )

    cwm = CloudWatchMetricsClient()
    cwm.put_metric('SuccessfulLogins', len(s_events))

    # return s_events
    fp_events = ddb.query(
            table_name=AUTH0_EVENTS_TABLE_NAME,
            KeyConditionExpression='event_type = :event_type and event_date > :one_hour_ago',
            ExpressionAttributeValues={
                ':event_type': 'fp',
                ':one_hour_ago': one_hour_ago,
            }
        )

    # now go through each failed login and see if there is a successful login for same user
    failed_login_count = 0
    for failed_login in fp_events:
        failed_login_user = failed_login['user_name']
        succeeded_eventually = False
        for successful_login in s_events:
            successful_login_user = successful_login['user_name']
            if failed_login_user == successful_login_user:
                succeeded_eventually = True
                break
        if not succeeded_eventually:
            failed_login_count += 1

    cwm.put_metric('FailedLogins', failed_login_count)

    return {
        "statusCode": HTTPStatus.OK,
    }