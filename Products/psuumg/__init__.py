from AccessControl.Permissions import manage_users
from Products.PluggableAuthService import registerMultiPlugin
from zope.i18nmessageid import MessageFactory
psuumgMessageFactory = MessageFactory('Products.psuumg')

from plugin import manage_addPSUUMGGroupManagerForm, addPSUUMGGroupManager, PSUUMGGroupManager
try:
    registerMultiPlugin(PSUUMGGroupManager.meta_type)
except RuntimeError:
    # make refresh users happy
    pass

def initialize(context):
    context.registerClass(PSUUMGGroupManager,
                          permission=manage_users,
                          constructors=(manage_addPSUUMGGroupManagerForm,
                                        addPSUUMGGroupManager),
                          visibility=None,
                          icon='www/multiplugin.gif')
