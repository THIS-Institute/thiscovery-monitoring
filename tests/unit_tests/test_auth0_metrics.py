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
from pprint import pprint
import thiscovery_lib.utilities as utils
from thiscovery_dev_tools import testing_tools as test_tools
from thiscovery_lib.dynamodb_utilities import Dynamodb

import src.common.constants as const
import src.auth0_metrics as azm
import tests.test_data as td
from src.auth0_metrics import Auth0EventLogClient


class TestAuth0EventLogClient(test_tools.BaseTestCase):

    def test_get_unique_users_from_events_ok(self):
        expected_result = {
            'altha@email.co.uk',
            'bernie@email.co.uk',
            'clive@email.co.uk',
            'delia@email.co.uk',
            'eddie@email.co.uk',
            # 'fred@email.co.uk',
            'glenda@email.co.uk',
            'harmony@email.co.uk',
            'henry@email.co.uk',
            'unknown',
        }
        result = Auth0EventLogClient.get_unique_users_from_events(events=td.METRICS_TEST_DATA)
        self.assertEqual(expected_result, result)


class TestAuth0MetricsCalculator(test_tools.BaseTestCase):

    def test_calculator_ok(self):
        def setup():
            ddb_client = Dynamodb(stack_name=const.STACK_NAME)
            ddb_client.delete_all(
                table_name=const.AUTH0_EVENTS_TABLE_NAME,
                key_name=const.AUTH0_EVENTS_TABLE_HASH,
                sort_key_name=const.AUTH0_EVENTS_TABLE_SORT,
            )
            for i in td.METRICS_TEST_DATA:
                i[const.AUTH0_EVENTS_TABLE_SORT] = utils.now_with_tz().strftime(const.DATE_FORMAT)
                ddb_client.put_item(
                    table_name=const.AUTH0_EVENTS_TABLE_NAME,
                    key=i[const.AUTH0_EVENTS_TABLE_HASH],
                    item_type='test_data',
                    item_details=dict(),
                    item=i,
                    key_name=const.AUTH0_EVENTS_TABLE_HASH,
                    sort_key={
                        const.AUTH0_EVENTS_TABLE_SORT: i[const.AUTH0_EVENTS_TABLE_SORT],
                    },
                )
        setup()
        calculator = azm.Auth0MetricsCalculator(dict())
        calculator.calc_all()
        self.assertEqual(2, calculator.successful_login_users_count)
        self.assertEqual(2, calculator.persistent_failed_login_count)
        self.assertEqual(50, calculator.failed_login_percent)
        self.assertEqual(4, calculator.successful_signup_users_count)
        self.assertEqual(1, calculator.completed_signup_users_count)
        self.assertEqual(0, calculator.failed_email_count)
        self.assertEqual(25, calculator.completed_signup_percent)
        self.assertEqual(0, int(calculator.average_elapsed_minutes))
