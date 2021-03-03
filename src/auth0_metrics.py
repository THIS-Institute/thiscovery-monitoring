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

import datetime
from http import HTTPStatus
import thiscovery_lib.utilities as utils
from thiscovery_lib import dynamodb_utilities as ddb_utils
import common.constants as constants


class CloudWatchMetricsClient(utils.BaseClient):

    def __init__(self, hours):
        super().__init__('cloudwatch')

        if hours == 1:
            self.value_label = 'Last hour'
        else:
            self.value_label = f'Last {hours} hours'

    def put_metric(self, metric_name, metric_value, metric_units='Count'):

        metric_data = [
                {
                    'MetricName': metric_name,
                    'Dimensions': [
                        {
                            'Name': 'Logins',
                            'Value': self.value_label
                        },
                    ],
                    'Unit': metric_units,
                    'Value': metric_value
                },
            ]

        # Put custom metrics
        result = self.client.put_metric_data(
            MetricData=metric_data,
            Namespace=constants.METRIC_NAMESPACE
        )
        assert result['ResponseMetadata']['HTTPStatusCode'] == HTTPStatus.OK, \
            f'CloudWatch put_metric_data call failed with response {result}'
        return HTTPStatus.OK


class Auth0EventLogClient:
    
    def __init__(self):
        self.ddb = ddb_utils.Dynamodb(stack_name=constants.STACK_NAME)

    def get_events(self, event_type, earliest_event_datetime):
        events = self.ddb.query(
            table_name=constants.AUTH0_EVENTS_TABLE_NAME,
            KeyConditionExpression='event_type = :event_type and event_date > :datetime_threshold',
            ExpressionAttributeValues={
                ':event_type': event_type,
                ':datetime_threshold': earliest_event_datetime,
            }
        )
        return events

    @staticmethod
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


class Auth0MetricsCalculator:

    def __init__(self, event):
        self.logger = utils.get_logger()

        if event and 'hours' in event:
            hours = int(event['hours'])
        else:
            hours = 1
        self.x_hours_ago = time_x_hours_ago(hours)
        self.auth0_event_client = Auth0EventLogClient()
        self.metrics_client = CloudWatchMetricsClient(hours)

        self.successful_login_users = None
        self.successful_login_users_count = None
        self.persistent_failed_login_users = None
        self.persistent_failed_login_count = None
        self.failed_login_percent = None
        self.completed_signup_events = None
        self.successful_signup_users = None
        self.successful_signup_users_count = None
        self.completed_signup_users = None
        self.completed_signup_users_count = None
        self.completed_signup_percent = None
        self.failed_email_count = None
        self.average_elapsed_minutes = None

    def calc_successful_login_users(self):
        successful_login_events = self.auth0_event_client.get_events(
            constants.SUCCESSFUL_LOGIN,
            self.x_hours_ago
        )
        self.successful_login_users = self.auth0_event_client.get_unique_users_from_events(successful_login_events)
        self.successful_login_users_count = len(self.successful_login_users)
        self.metrics_client.put_metric('SuccessfulLogins', self.successful_login_users_count)
        return self.successful_login_users_count

    def calc_password_failures(self):
        """
        Get login failures due to password (but not username) errors
        """
        failed_login_events = self.auth0_event_client.get_events(
            constants.FAILED_LOGIN_PASSWORD,
            self.x_hours_ago,
        )
        failed_login_users = self.auth0_event_client.get_unique_users_from_events(failed_login_events)
        # don't include users that failed and then succeeded - they are nothing to worry about
        self.persistent_failed_login_users = failed_login_users - self.successful_login_users
        self.persistent_failed_login_count = len(self.persistent_failed_login_users)
        self.metrics_client.put_metric('FailedLogins', self.persistent_failed_login_count)
        return self.persistent_failed_login_count

    def calc_failed_login_percent(self):
        total_users = self.successful_login_users_count + self.persistent_failed_login_count
        if total_users:
            self.failed_login_percent = self.persistent_failed_login_count * 100 / total_users
            self.metrics_client.put_metric('FailedLoginPercent', self.failed_login_percent, 'Percent')
            return self.failed_login_percent

    def calc_successful_signup_users(self):
        successful_signup_events = self.auth0_event_client.get_events(
            constants.SUCCESSFUL_SIGNUP,
            self.x_hours_ago
        )
        self.successful_signup_users = self.auth0_event_client.get_unique_users_from_events(successful_signup_events)
        self.successful_signup_users_count = len(self.successful_signup_users)
        self.metrics_client.put_metric('SuccessfulSignups', self.successful_signup_users_count)
        return self.successful_signup_users_count

    def calc_completed_signup_users(self):
        self.completed_signup_events = self.auth0_event_client.get_events(constants.SUCCESSFUL_VERIFICATION_EMAIL, self.x_hours_ago)
        self.completed_signup_users = self.auth0_event_client.get_unique_users_from_events(self.completed_signup_events)
        self.completed_signup_users_count = len(self.completed_signup_users)
        self.metrics_client.put_metric('CompletedSignups', self.completed_signup_users_count)
        return self.completed_signup_users_count

    def calc_failed_to_send_signup_notification_email(self):
        failed_email_events = self.auth0_event_client.get_events(constants.FAILED_SENDING_NOTIFICATION_EMAIL, self.x_hours_ago)
        self.failed_email_count = len(failed_email_events)
        self.metrics_client.put_metric('FailedSignupEmails', self.failed_email_count)
        return self.failed_email_count

    def calc_percentage_of_completed_signups(self):
        if self.successful_signup_users_count:
            self.completed_signup_percent = self.completed_signup_users_count * 100 / self.successful_signup_users_count
            self.metrics_client.put_metric('CompletedSignupPercent', self.completed_signup_percent, 'Percent')
            return self.completed_signup_percent

    def calc_average_signup_verification_interval(self):
        one_week_ago = time_x_hours_ago(24 * 7)
        successful_signup_events = self.auth0_event_client.get_events(constants.SUCCESSFUL_SIGNUP, one_week_ago)
        signup_times = {}
        # get all signup data and calculate each elapsed time
        for completed_signup_event in self.completed_signup_events:
            for successful_signup_event in successful_signup_events:
                if successful_signup_event['user_name'] == completed_signup_event['user_name']:
                    signup_time = datetime.datetime.strptime(successful_signup_event['event_date'], constants.DATE_FORMAT)
                    completion_time = datetime.datetime.strptime(completed_signup_event['event_date'], constants.DATE_FORMAT)
                    signup_times[successful_signup_event['user_name']] = (completion_time - signup_time)
        # calculate average - note this could be done in loop above, but explict recording and averaging makes debugging and verification easier
        if signup_times:
            total_elapsed_time = datetime.timedelta()
            for elapsed_time in signup_times.values():
                total_elapsed_time += elapsed_time
            self.average_elapsed_minutes = total_elapsed_time.total_seconds() / len(signup_times) / 60
            self.metrics_client.put_metric('AverageSignupTime', self.average_elapsed_minutes)
        return self.average_elapsed_minutes

    def calc_all(self):
        self.calc_successful_login_users()
        self.calc_password_failures()
        self.calc_failed_login_percent()
        self.calc_successful_signup_users()
        self.calc_completed_signup_users()
        self.calc_failed_to_send_signup_notification_email()
        self.calc_percentage_of_completed_signups()
        self.calc_average_signup_verification_interval()
        self.logger.info('Logging Auth0 metrics', extra={
            'SuccessfulLogins': self.successful_login_users_count,
            'FailedLogins': self.persistent_failed_login_count,
            'FailedLoginPercent': self.failed_login_percent,
            'SuccessfulSignups': self.successful_signup_users_count,
            'FailedSignupEmails': self.failed_email_count,
            'CompletedSignups': self.completed_signup_users_count,
            'CompletedSignupPercent': self.completed_signup_percent,
            'AverageSignupTime': self.average_elapsed_minutes,
        })


def calculate_auth0_metrics(event, context):
    calculator = Auth0MetricsCalculator(event=event)
    calculator.calc_all()

    return {
        "statusCode": HTTPStatus.OK,
    }
