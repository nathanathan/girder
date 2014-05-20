
from girder.constants import AccessType
from girder.utility.model_importer import ModelImporter
from girder.api.rest import Resource, RestException
from girder.models.model_base import AccessException
from girder.events import bind


class PrivateMetadata(Resource):

    def __init__(self):

        self.accessModel = ModelImporter().model('folder')

        # the item key where private metadata is stored
        self.privateKey = 'private'

    def _getPrivate(self, doc):
        """
        Return the private component of a document, create it if it
        does not exist.
        """
        pvt = doc.get(self.privateKey, {})
        doc[self.privateKey] = pvt
        return pvt

    def getPrivateAccessList(self, folder):
        """
        Get private access list for a folder
        """

        # get the private object
        privateDocument = self._getPrivate(folder)

        return self.accessModel.getFullAccessList(privateDocument)

    def setPrivateAccessList(self, folder, access, save=False):
        """
        Set the private access list for a folder
        """

        privateDocument = self._getPrivate(folder)
        self.accessModel.setAccessList(folder, access, save)
        return folder

    def copyPrivateAccessPolicies(self, src, dest, save=False):
        """
        Copy access policy of private metadata from one folder
        to another.
        """
        access = self.getPrivateAccessList(src)
        return self.setPrivateAccessList(dest, access, save)

    def getPrivateAccessLevel(self, folder, user):
        """
        Get the highest access level to the private metadata.
        """
        privateDocument = self._getPrivate(folder)
        return self.accessModel.getAccessLevel(privateDocument, user)

    def requirePrivateAccess(self, folder, user=None, level=AccessType.READ):
        """
        Raise an exception if requested access is not granted by calling
        the standard requireAccess model method.
        """
        privateDocument = self._getPrivate(folder)
        self.accessModel.requireAccess(privateDocument, user, level)

    def afterItemGet(self):
        """
        Returns a function that can be attached to rest.get.item/:id.before
        to augment the item response with private metadata if the user has
        read access.
        """

        itemModel = ModelImporter().model('item')
        folderModel = self.accessModel

        def handler(evt):

            # get the item id
            id = evt.info['id']

            # load the full item document
            item = itemModel.load(id=id, force=True)

            # load the parent folder document
            folder = folderModel.load(id=item['folderId'], force=True)

            # test permissions
            try:
                self.requirePrivateAccess(
                    folder,
                    user=self.getCurrentUser(),
                    level=AccessType.READ
                )
            except AccessException as e:
                return

            evt.info['returnVal'][self.privateKey] = \
                item.get(self.privateKey, {})

        return handler


def load(info):
    pvt = PrivateMetadata()
    bind(
        'rest.get.item/:id.after',
        'private_metadata.get_item',
        pvt.afterItemGet()
    )
