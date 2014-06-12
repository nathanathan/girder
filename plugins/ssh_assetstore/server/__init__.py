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
import os
import datetime

from girder.utility.abstract_assetstore_adapter import AbstractAssetstoreAdapter
from girder.utility.assetstore_utilities import getAssetstoreAdapter
from girder.utility.model_importer import ModelImporter
from girder import events
from girder.api.v1.assetstore import Assetstore
from girder.api.describe import Description
from girder.api.rest import Resource, RestException


# Module level variable to provide access to the assetstore model
assetStoreModel = ModelImporter().model('assetstore')


################################################################################
# A new assetstore type which uses SSH to access a remote machine and proxy
# files from the remote file system
################################################################################
class SSHAssetstoreAdapter(AbstractAssetstoreAdapter):
    """
    This assetstore type refers to files stored on a remote system
    accessible only through ssh.  This is a read-only assetstore.
    """

    def __init__(self, assetstore):
        """
        :param assetstore: The assetstore to act on.
        """
        self.assetstore = assetstore

    def mountRemoteDirectory(remotePath, folderId, connId):
        print

    def capacityInfo(self):
        return {
            'free': None,
            'total': None
        }  # pragma: no cover

    def initUpload(self, upload):
        return []

    def uploadChunk(self, upload, chunk):
        return []

    def requestOffset(self, upload):
        return 0

    def finalizeUpload(self, upload, file):
        return file

    def downloadFile(self, file, offset=0, headers=True):
        return []

    def deleteFile(self, file):
        return []


################################################################################
# A resource to ease creating new routes related to this assetstore
################################################################################
class HelperResource(Resource):
    def addMountPoint(self, params):
        print 'Inside HelperResource, adding assetstore mount point'
        self.requireParams(('assetstoreid', 'remotepath',
                            'localfolderid', 'connectionid'),
                           params)
        # Params should contain information about:
        #   1) which assetstore
        #   2) remote mount point (full path to folder on remote system)
        #   3) local mount point (girder folder id)
        #   4) remote connection id (for connection to remote machine)
        doc = assetStoreModel.load(params['assetstoreid'])
        print 'I have found the assetstore record I need:'
        print doc
        adapter = SSHAssetstoreAdapter(doc)
        #adapter.mountRemoteDirectory(params['remotepath'], params['localfolderid'],
        return []
    addMountPoint.description = (
        Description('Add a mount point to map a remote folder')
        .param('assetstoreid', 'The assetstore id to use when mounting')
        .param('remotepath', 'Full path to mount on remote system')
        .param('localfolderid', 'Girder folder id to use as root')
        .param('connectionid', 'Remote connection id for user and remote host')
        .errorResponse())


def createHook(evt):
    print "Inside createHook"
    assetStoreModel.save({
            'type': 'ssh',
            'created': datetime.datetime.now(),
            'name': evt.info['params']['name'],
            'host': evt.info['params']['host']
            })
    evt.preventDefault()
    evt.addResponse(['response messsage'])

def getHook(evt):
    print "Inside getHook (bound to 'assetstore.adapter.get')"
    print evt.info
    if evt.info['type'] == 'ssh':
        evt.addResponse(SSHAssetstoreAdapter(evt.info))
        evt.stopPropagation()

def validateHook(evt):
    print 'Inside validateHook'
    print evt.info
    evt.preventDefault()
    return evt.info

def load(info):
    events.bind('rest.post.assetstore.before', 'SSHAssetstoreAdapter', createHook)
    events.bind('assetstore.adapter.get', 'SSHAssetstoreAdapter', getHook)
    events.bind('model.assetstore.validate', 'SSHAssetstoreAdapter', validateHook)

    msg = 'The fully qualified host name for this Assetstore'
    Assetstore.createAssetstore.description.param('host', msg, required=False)

    resource = HelperResource()
    info['apiRoot'].assetstore.route('PUT', ('mount',), resource.addMountPoint)
