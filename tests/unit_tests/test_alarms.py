#
#   Thiscovery API - THIS Institute’s citizen science platform
#   Copyright (C) 2019 THIS Institute
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
import local.dev_config
import local.secrets
import json
from http import HTTPStatus
from thiscovery_dev_tools import testing_tools as test_tools
from thiscovery_dev_tools.test_data.auth0_events import SUCCESSFUL_LOGIN
from pprint import pprint

import src.alarms as alarms


class TestAlarms(test_tools.BaseTestCase):

    def common_routine(self, func):
        result = func(dict(), None)
        body = json.loads(result['body'])
        self.assertEqual(HTTPStatus.METHOD_NOT_ALLOWED, result['statusCode'])
        self.assertEqual('Coffee is not available', body['error'])

    def test_core_service_alarm_ok(self):
        self.common_routine(alarms.core_service_alarm_test)

    def test_interviews_service_alarm_ok(self):
        self.common_routine(alarms.interviews_service_alarm_test)

    def test_surveys_service_alarm_ok(self):
        self.common_routine(alarms.surveys_service_alarm_test)
