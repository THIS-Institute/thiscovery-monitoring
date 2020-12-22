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
STACK_NAME = 'thiscovery-monitoring'
AUTH0_EVENTS_TABLE_NAME = 'Auth0Events'
METRIC_NAMESPACE = 'Authentication'

# Auth0 event codes
SUCCESSFUL_LOGIN = 's'
FAILED_LOGIN_PASSWORD = 'fp'
FAILED_LOGIN_USER = 'fu'
SUCCESSFUL_SIGNUP = 'ss'
SUCCESSFUL_VERIFICATION_EMAIL = 'sv'
FAILED_SENDING_NOTIFICATION_EMAIL = 'fn'

DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'  # eg 2020-12-22 14:31:31.940
