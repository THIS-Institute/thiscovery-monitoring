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
import random
from pprint import pprint
from thiscovery_lib.dynamodb_utilities import Dynamodb

import src.common.constants as const


def anonymise_data(items):
    test_users = [
        'altha@email.co.uk',  #0
        'bernie@email.co.uk',  #1
        'clive@email.co.uk',  #2
        'delia@email.co.uk',  #3
        'eddie@email.co.uk',  #4
        'fred@email.co.uk',  #5
        'glenda@email.co.uk',  #6
    ]
    event_type_to_sample = {
        const.SUCCESSFUL_SIGNUP: test_users[:4],
        const.SUCCESSFUL_VERIFICATION_EMAIL: test_users[:3],
        const.SUCCESSFUL_LOGIN: test_users[:2],
        const.FAILED_LOGIN_PASSWORD: test_users[3:5],
        const.FAILED_LOGIN_USER: test_users[5:]
    }
    for i in items:
        if i['user_name'] != 'unknown':
            event_type = i[const.AUTH0_EVENTS_TABLE_HASH]
            sample = event_type_to_sample.get(
                event_type, ['henry@email.co.uk', 'harmony@email.co.uk']
            )
            i['user_name'] = random.choice(sample)

    return items


def main(output_filename='test_data_draft.py', items_n=100, depth=None):
    ddb_client = Dynamodb(stack_name=const.STACK_NAME)
    items = ddb_client.scan(
        table_name=const.AUTH0_EVENTS_TABLE_NAME,
    )
    selected_items = anonymise_data(random.sample(items, items_n))
    with open(output_filename, 'w') as f:
        pprint(selected_items, stream=f, depth=depth)


if __name__ == '__main__':
    main(
        depth=2
    )
