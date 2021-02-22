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
import pyjokes
import thiscovery_lib.utilities as utils

from http import HTTPStatus
from thiscovery_lib.core_api_utilities import CoreApiClient
from thiscovery_lib.emails_api_utilities import EmailsApiClient
from thiscovery_lib.interviews_api_utilities import InterviewsApiClient
from thiscovery_lib.surveys_api_utilities import SurveysApiClient


@utils.lambda_wrapper
def core_service_alarm_test(event, context):
    client = CoreApiClient(correlation_id=event['correlation_id'])
    response = client.send_transactional_email(template_name='alarm_test', brew_coffee=True)
    assert response['statusCode'] == HTTPStatus.METHOD_NOT_ALLOWED, f'Email service returned unexpected response {response}'


@utils.lambda_wrapper
def email_service_alarm_test(event, context):
    env_name = utils.get_environment_name()
    if env_name == 'prod':
        client = EmailsApiClient(correlation_id=event['correlation_id'])
        response = client.send_email(email_dict={'brew_coffee': True})
        assert response['statusCode'] == HTTPStatus.METHOD_NOT_ALLOWED, f'Email service returned unexpected response {response}'


@utils.lambda_wrapper
def interviews_service_alarm_test(event, context):
    client = InterviewsApiClient(correlation_id=event['correlation_id'])
    response = client.set_interview_url(appointment_id=None, interview_url=None, event_type=None, **{'brew_coffee': True})
    assert response['statusCode'] == HTTPStatus.METHOD_NOT_ALLOWED, f'Interviews service returned unexpected response {response}'


@utils.lambda_wrapper
def surveys_service_alarm_test(event, context):
    client = SurveysApiClient(correlation_id=event['correlation_id'])
    response = client.put_response(**{'brew_coffee': True})
    assert response['statusCode'] == HTTPStatus.METHOD_NOT_ALLOWED, f'Surveys service returned unexpected response {response}'


@utils.lambda_wrapper
def raise_error(event, context):
    joke = pyjokes.get_joke()
    return utils.log_exception_and_return_edited_api_response(
        exception=f'Deliberate error. Here is a joke for you:\n{joke}',
        status_code=HTTPStatus.METHOD_NOT_ALLOWED,
        logger_instance=event['logger'],
        correlation_id=event['correlation_id'],
    )
