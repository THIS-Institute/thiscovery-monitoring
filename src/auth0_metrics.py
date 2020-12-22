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
import common.constants as constants


class CloudWatchMetricsClient(utils.BaseClient):

    def __init__(self):
        super().__init__('cloudwatch')

    def put_metric(self, metric_name, metric_value, metric_units = 'Count'):

        metric_data = [
                {
                    'MetricName': metric_name,
                    'Dimensions': [
                        {
                            'Name': 'Logins',
                            'Value': 'Last hour'
                        },
                    ],
                    'Unit': metric_units,
                    'Value': metric_value
                },
            ]

        # Put custom metrics
        self.client.put_metric_data(
            MetricData=metric_data,
            Namespace=constants.METRIC_NAMESPACE
        )


def get_unique_users_from_events(events):
    users = set()
    for event in events:
        user = event['user_name']
        if user not in users:
            users.add(user)
    return users


def time_x_hours_ago(x_hours):
    x_hours_ago = utils.now_with_tz() - datetime.timedelta(hours=x_hours)
    return x_hours_ago.strftime("%Y-%m-%d %H:%M:%S.%f")


def get_events(ddb, event_type, earliest_event_datetime):
    events = ddb.query(
        table_name=constants.AUTH0_EVENTS_TABLE_NAME,
        KeyConditionExpression='event_type = :event_type and event_date > :datetime_threshold',
        ExpressionAttributeValues={
            ':event_type': event_type,
            ':datetime_threshold': earliest_event_datetime,
        }
    )
    return events


def calculate_auth0_metrics(event, context):
    logger = utils.get_logger()

    x_hours_ago = time_x_hours_ago(12)

    ddb = ddb_utils.Dynamodb(stack_name=constants.STACK_NAME)
    cwm = CloudWatchMetricsClient()

    # successful login users
    successful_login_events = get_events(ddb, constants.SUCCESSFUL_LOGIN, x_hours_ago)
    successful_login_users = get_unique_users_from_events(successful_login_events)
    successful_login_count = len(successful_login_users)
    cwm.put_metric('SuccessfulLogins', successful_login_count)

    # get login failures due to password or username errors
    failed_login_events = get_events(ddb, constants.FAILED_LOGIN_PASSWORD, x_hours_ago) + get_events(ddb, constants.FAILED_LOGIN_USER, x_hours_ago)
    failed_login_users = get_unique_users_from_events(failed_login_events)
    # don't include users that failed and then succeeded - they are nothing to worry about
    persistent_failed_login_users = failed_login_users - successful_login_users
    persistent_failed_login_count = len(persistent_failed_login_users)
    cwm.put_metric('FailedLogins', persistent_failed_login_count)

    failed_login_percent = persistent_failed_login_count * 100 / (successful_login_count + persistent_failed_login_count)
    cwm.put_metric('FailedLoginPercent', failed_login_percent, 'Percent')

    # successful signup users
    successful_signup_events = get_events(ddb, constants.SUCCESSFUL_SIGNUP, x_hours_ago)
    successful_signup_users = get_unique_users_from_events(successful_signup_events)
    successful_signup_count = len(successful_signup_users)
    cwm.put_metric('SuccessfulSignups', successful_signup_count)

    # completed signup users
    completed_signup_events = get_events(ddb, constants.SUCCESSFUL_VERIFICATION_EMAIL, x_hours_ago)
    completed_signup_users = get_unique_users_from_events(completed_signup_events)
    completed_signup_count = len(completed_signup_users)
    cwm.put_metric('CompletedSignups', completed_signup_count)

    # failed to send signup notification email
    failed_email_events = get_events(ddb, constants.FAILED_SENDING_NOTIFICATION_EMAIL, x_hours_ago)
    failed_email_count = len(failed_email_events)
    cwm.put_metric('FailedSignupEmails', failed_email_count)

    # percentage of completed signups
    uncompleted_signup_users = successful_signup_users - completed_signup_users
    uncompleted_signup_count = len(uncompleted_signup_users)
    if successful_signup_count > 0:
        completed_signup_percent = (successful_signup_count - uncompleted_signup_count) * 100 / successful_signup_count
        cwm.put_metric('CompletedSignupPercent', completed_signup_percent, 'Percent')

    # average signup verification interval
    one_week_ago = time_x_hours_ago(24 * 7)
    successful_signup_events = get_events(ddb, constants.SUCCESSFUL_SIGNUP, one_week_ago)
    signup_times = {}

    # get all signup data and calculate each elapsed time
    for completed_signup_event in completed_signup_events:
        for successful_signup_event in successful_signup_events:
            if successful_signup_event['user_name'] == completed_signup_event['user_name']:
                signup_time = datetime.datetime.strptime(successful_signup_event['event_date'],constants.DATE_FORMAT)
                completion_time = datetime.datetime.strptime(completed_signup_event['event_date'], constants.DATE_FORMAT)
                signup_times[successful_signup_event['user_name']] = (completion_time - signup_time)
    # calculate average - note this could be done in loop above, but explict recording and averaging makes debugging and verification easier
    if len(signup_times) > 0:
        total_elapsed_time = datetime.timedelta()
        for elapsed_time in signup_times.values():
            total_elapsed_time += elapsed_time
        average_elapsed_minutes = total_elapsed_time.total_seconds() / len(signup_times) / 60
        cwm.put_metric('AverageSignupTime', average_elapsed_minutes)

    logger.info('Logging Auth0 metrics', extra={
        'SuccessfulLogins': successful_login_count,
        'FailedLogins': persistent_failed_login_count,
        'FailedLoginPercent': failed_login_percent,
        'SuccessfulSignups': successful_signup_count,
        'FailedSignupEmails': failed_email_count,
        'CompletedSignups': completed_signup_count,
        'CompletedSignupPercent': completed_signup_percent,
        'AverageSignupTime': average_elapsed_minutes,
    })

    return {
        "statusCode": HTTPStatus.OK,
    }





