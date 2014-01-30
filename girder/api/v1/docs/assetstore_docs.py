#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright 2013 Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

from ..api_docs import Describe

apis = []

apis.append({
    'path': '/assetstore',
    'resource': 'file',
    'operations': [{
        'httpMethod': 'POST',
        'nickname': 'createAssetstore',
        'type': 'Assetstore',
        'summary': 'Create a new assetstore.',
        'parameters': [
            Describe.param('name', "Unique name for the assetstore."),
            Describe.param('type', "Type of the assetstore.",
                           dataType='integer'),
            Describe.param('root', 'For filesystem assetstores, this is the '
                           'root directory of the assetstore.',
                           required=False),
            Describe.param('db', 'For GridFS assetstores, this is the name of'
                           'the database to store files inside of.',
                           required=False)
            ],
        'errorResponses': [
            Describe.errorResponse(),
            Describe.errorResponse('You are not an administrator.', 403)
            ]
        }, {
        'httpMethod': 'GET',
        'nickname': 'listAssetstores',
        'type': 'array',
        'items': { '$ref': 'Assetstore' },
        'summary': 'List assetstores.',
        'parameters': [
            Describe.param(
                'limit', "Result set size limit (default=50).", required=False,
                dataType='integer'),
            Describe.param(
                'offset', "Offset into result set (default=0).", required=False,
                dataType='integer'),
            Describe.param(
                'sort', "Field to sort the assetstore list by (default=name)",
                required=False),
            Describe.param(
                'sortdir', "1 for ascending, -1 for descending (default=1)",
                required=False, dataType='integer')
            ],
        'errorResponses': [
            Describe.errorResponse(),
            Describe.errorResponse('You are not an administrator.', 403)
            ]
        }]
    })

Describe.declareApi('assetstore', apis=apis)

Describe.declareModel('Assetstore', {
    'id': 'Assetstore',
    'properties': {
        '_id': {
            'type': 'string',
            'required': True,
            'description': 'The resource ID'
        },
        'type': {
            'type': 'integer',
            'required': True,
            'description': 'The assetstore type'
        },
        'current': {
            'type': 'boolean',
            'required': True,
            'description': 'Whether this is the current assetstore'
        },
        'name': {
            'type': 'string',
            'required': True
        },
        'created': {
            'type': 'date',
            'required': True,
            'description': 'When this assetstore was created'
        },
        'root': {
            'type': 'string',
            'description': 'For filesystem assetstores, the root directory of '
                'the assetstore'
        },
        'db': {
            'type': 'string',
            'description': 'For GridFS assetstores, the database name for the '
                'file collections to be stored in'
        }
    }
})
