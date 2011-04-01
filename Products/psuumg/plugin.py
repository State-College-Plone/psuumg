from interfaces import IPSUUMGGroupManager
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from BTrees.OOBTree import OOBTree
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PlonePAS.interfaces.group import IGroupManagement, IGroupIntrospection
from Products.PlonePAS.interfaces.capabilities import IGroupCapability, IDeleteCapability
from Products.PluggableAuthService.interfaces.plugins import IGroupEnumerationPlugin, IGroupsPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin


manage_addPSUUMGGroupManagerForm = PageTemplateFile(
    'www/psuumgAdd.zpt', globals(), __name__='manage_addPSUUMGGroupManagerForm')

def addPSUUMGGroupManager(dispatcher, id, title=None, REQUEST=None):
    """Add a PSUUMGGroupManager to a Pluggable Auth Service."""

    pugm = PSUUMGGroupManager(id, title)
    dispatcher._setObject(pugm.getId(), pugm)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
                                '%s/manage_workspace'
                                '?manage_tabs_message='
                                'PSUUMGGroupManager+added.'
                            % dispatcher.absolute_url())

class PSUUMGGroupManager(BasePlugin):
    """PAS plugin for managing UMG-based groups"""
    meta_type = 'PSU UMG Group Manager'    
    security = ClassSecurityInfo()    
    implements(IPSUUMGGroupManager, IGroupEnumerationPlugin, IGroupsPlugin, IGroupIntrospection, IGroupManagement, IGroupCapability, IDeleteCapability)
    
    def __init__(self, id, title=None, host=None, email_domain=None):
        self.id = id
        self.title = title
        self.host = host
        self.email_domain = email_domain
        self._groups = OOBTree()

    # IGroupEnumerationPlugin
    security.declarePrivate('enumerateGroups')
    
    def enumerateGroups(self, id=None, title=None, exact_match=False, sort_by=None, max_results=None, **kw):
        group_info = []
        group_ids = []
        plugin_id = self.getId()
        
        if isinstance(id, basestring):
            id = [id]
            
        if isinstance(title, basestring):
            title = [title]
            
        if exact_match and (id or title):
            if id:
                group_ids.extend(id)
            elif title:
                group_ids.extend(title)
        
        if group_ids:
            group_filter = None
        else:
            group_ids = self.listGroupIds()
            group_filter = _PSUUMGGroupFilter(id, title, **kw)            
            
        for group_id in group_ids:
            if self._groups.get(group_id, None):
                url = '%s/manage_groups' % self.getId()
                gid = 'group_id=%s' % group_id
        
        return tuple(group_info)
    
    # IGroupsPlugin
    security.declarePrivate('getGroupsForPrincipal')
    def getGroupsForPrincipal(self, principal, request=None):
        return ()
    
    # IGroupIntrospection
    def getGroupById(group_id):
        pass
    
    def getGroups():
        pass
    
    def getGroupIds():
        pass
    
    def getGroupMembers(group_id):
        pass
    
    # IGroupManagement
    def addGroup(id, **kw):
        pass
        
    def addPrincipalToGroup(self, principal_id, group_id):
        return False
    
    def updateGroup(id, **kw):
        pass
        
    def setRolesForGroup(group_id, roles=()):
        pass
    
    def removeGroup(group_id):
        pass
    
    def removePrincipalFromGroup(principal_id, group_id):
        return False
    
    # IGroupCapability
    def allowGroupAdd(self, user_id, group_id):
        return 0
    
    def allowGroupRemove(self, user_id, group_id):
        return 0
    
    # IDeleteCapability
    security.declarePublic('allowDeletePrincipal')
    def allowDeletePrincipal(self, principal_id):
        if self._groups.get(principal_id) is not None:
            return 1
        return 0
    
# borrowed from Products.PluggableAuthService.plugins.ZODBGroupManager.py
class _PSUUMGGroupFilter:
    def __init__( self, id=None, title=None, **kw):
        self._filter_ids = id
        self._filter_titles = title

    def __call__( self, group_info ):
        if self._filter_ids:
            key = 'id'
            to_test = self._filter_ids
        elif self._filter_titles:
            key = 'title'
            to_test = self._filter_titles
        else:
            return 1 # TODO:  try using 'kw'
        value = group_info.get( key )
        if not value:
            return 0
        for contained in to_test:
            if value.lower().find(contained.lower()) >= 0:
                return 1
        return 0
