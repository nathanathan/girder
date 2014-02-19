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

import cherrypy
import pymongo
import os
import paramiko
import sys

from ..rest import Resource, RestException
from ...models.model_base import ValidationException
from ...utility import ziputil
from ...constants import AccessType


### Convenience function to check if all keys are in a dictionary
def allIn(keyTuple, dictionary) :
    return all(k in dictionary for k in keyTuple)

class RemoteConnection(Resource):
    """
    API endpoint for remote connections.  This is a throwaway class, just
    designed to achieve my goals for demo purposes.  This class will need
    to be re-written to fit within the Girder plugin framework whenever
    we come up with that thing.

    Interaction with this REST component is as follows:

    1) Create a new connection to remote host 'mayall':

        http://localhost:8080/api/v1/remoteconnection/create?fqhn=mayall

    2) Actually connect to the host corresponding to this connection:

        http://localhost:8080/api/v1/remoteconnection/connect?connId=08b8b44e-9800-11e3-b3d4-3ca9f4373d8&username=yyyyyyy&password=xxxxxxx

    3) Send a command on the connection:

        http://localhost:8080/api/v1/remoteconnection/command?connId=08b8b44e-9800-11e3-b3d4-3ca9f4373d8c&cmdStr=ls%20-al

    4) Close an existing connection:

        http://localhost:8080/api/v1/remoteconnection/disconnect?connId=08b8b44e-9800-11e3-b3d4-3ca9f4373d8c
    """

    def __init__(self, pathToConnModule) :
        sys.path.insert(0, pathToConnModule)
        rcm = __import__('RemoteConnection')
        self.remoteConnMgr = rcm.RemoteConnectionManager()
        Resource.__init__(self)

    def handleRemoteConnectionRequest(self, todo, params) :
        """
        Does the work of interpreting the part of the path which corresponds
        to the command I want to execute, getting the necessary parameters,
        and then executing the command, whether the goal it to create a
        new connection, connect on that connection, send a command if it
        is connected, or close the connection.
        """
        if todo == 'create' :
            if allIn(('fqhn',), params) :
                connId = self.remoteConnMgr.create({'fqhn': params['fqhn']})
                return { 'connId': connId }
            else :
                return [ 'Should have received a hostname as fqhn: ' + str(params) ]
        elif todo == 'connect' :
            if allIn(('connId', 'username', 'password'), params) :
                conn = self.remoteConnMgr.retrieve(params['connId'])
                if conn is not None and conn.connected is not True :
                    try :
                        conn.connect(params['username'], params['password'])
                        return [ 'Connection ' + params['connId'] + ' connected' ]
                    except Exception as inst :
                        return [ "Error connecting id %s: %s" % (params['connId'], str(inst)) ]
                else :
                    return [ 'Unable to connect for connId ' + params['connId'] ]
            else :
                return [ 'Should have received a connection id, username, and password: ' + str(params) ]
        elif todo == 'command' :
            if allIn(('connId', 'cmdStr'), params) :
                conn = self.remoteConnMgr.retrieve(params['connId'])
                if conn is not None :
                    return conn.sendCommand(params['cmdStr'])
                else :
                    return [ 'Found no connection with id ' + params['connId'] ]
            else :
                return [ 'You must supply a connection id and a command string to run' ]
        elif todo == 'disconnect' :
            if allIn(('connId',), params) :
                conn = self.remoteConnMgr.retrieve(params['connId'])
                if conn is not None :
                    conn.close()
                    return [ 'Connection ' + params['connId'] + ' is now closed' ]
                else :
                    return [ 'Found no connection with id ' + params['connId'] ]
            else :
                return [ 'You must supply an id to close a connection: ' + str(params) ]
        else :
            return [ 'I do not know what ' + todo + ' means' ]

    @Resource.endpoint
    def GET(self, path, params):
        user = self.getCurrentUser()
        if not path:
            return self.find(user, params)
        elif len(path) == 1:
            return self.handleRemoteConnectionRequest(path[0], params)
        else:
            raise RestException('Unrecognized remoteconnection GET endpoint.')
