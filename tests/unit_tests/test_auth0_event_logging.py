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
import time
from thiscovery_dev_tools import testing_tools as test_tools
from thiscovery_dev_tools.test_data.auth0_events import SUCCESSFUL_LOGIN
from thiscovery_lib.dynamodb_utilities import Dynamodb
from thiscovery_lib.eb_utilities import ThiscoveryEvent, EventbridgeClient

import src.common.constants as const


class TestAuth0EventPersistence(test_tools.BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ddb_client = Dynamodb(stack_name=const.STACK_NAME)
        cls.ddb_client.delete_all(
            table_name=const.AUTH0_EVENTS_TABLE_NAME,
            key_name=const.AUTH0_EVENTS_TABLE_HASH,
            sort_key_name=const.AUTH0_EVENTS_TABLE_SORT,
        )
        cls.eb_client = EventbridgeClient()

    def test_ddb_dump_ok(self):
        test_event = ThiscoveryEvent(
            event={
                **SUCCESSFUL_LOGIN,
                'event_source': 'Auth 0',
            }
        )
        self.eb_client.put_event(
            thiscovery_event=test_event,
            event_bus_name='auth0-event-bus'
        )
        time.sleep(1)
        events = self.ddb_client.scan(
            table_name=const.AUTH0_EVENTS_TABLE_NAME
        )
        self.assertEqual(1, len(events))
        self.assertEqual(events[0]['user_name'], SUCCESSFUL_LOGIN['detail']['data']['user_name'])
