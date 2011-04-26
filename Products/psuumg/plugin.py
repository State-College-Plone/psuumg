from interfaces import IPSUUMGGroupManager
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from AccessControl.requestmethod import postonly
from App.class_init import InitializeClass
from BTrees.OOBTree import OOBTree
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PlonePAS.interfaces.group import IGroupManagement, IGroupIntrospection
from Products.PlonePAS.interfaces.capabilities import IGroupCapability, IDeleteCapability
from Products.PlonePAS.plugins.group import PloneGroup
from Products.PluggableAuthService.interfaces.plugins import IGroupEnumerationPlugin, IGroupsPlugin
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin, IRolesPlugin
from Products.PluggableAuthService.permissions import ManageGroups
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
            group_ids = self._groups.keys()
            group_filter = _PSUUMGGroupFilter(id, title, **kw)            
            
        for group_id in group_ids:
            print group_id
            if self._groups.get(group_id, None):
                url = '%s/manage_groups' % self.getId()
                gid = 'group_id=%s' % group_id
                info = {}
                info.update(self._groups[group_id])
                info['pluginid'] = plugin_id
                info['properties_url'] = '%s?%s' % (url, gid)
                info['members_url'] = '%s%s' % (self.prefix, info['id'])
                
                if not group_filter or group_filter(info):
                    group_info.append(info)
        
        return tuple(group_info)
    
    # IGroupsPlugin
    security.declarePrivate('getGroupsForPrincipal')
    def getGroupsForPrincipal(self, principal, request=None):
        # XXX: Test implementation
        print "Asked for groups of principal %s" % principal
        return ()
    
    # IGroupIntrospection
    def getGroupById(self, group_id, default=None):
        plugins = self._getPAS()._getOb('plugins')
        title = None
        if group_id not in self.getGroupIds():
            return default
        
        return self._findGroup(plugins, group_id, title)
    
    def getGroups(self):
        return map(self.getGroupById, self.getGroupIds())
    
    def getGroupIds(self):
        return self._groups.keys()
    
    def getGroupMembers(self, group_id):
        # XXX: Test implementation
        print "Asked for members of UMG %s" % group_id
        if group_id not in self._groups:
            print "Not our group."
            return ()
        return ()
    
    # IGroupManagement
    security.declarePrivate(ManageGroups, 'addGroup')
    def addGroup(self, group_id, title=None, description=None, dn=None, **kw):
        if self._groups.get(group_id) is not None:
            raise KeyError, 'Duplicate group id: %s' % group_id
        
        self._groups[group_id] = { 'id': group_id, 'dn': dn, 'title': title, 'description': description }
        
    security.declareProtected(ManageGroups, 'addPrincipalToGroup')
    def addPrincipalToGroup(self, principal_id, group_id):
        return False
    
    security.declarePrivate(ManageGroups, 'updateGroup')
    def updateGroup(self, group_id, title=None, description=None, dn=None, **kw):
        group = self._groups[group_id]
        if dn is not None:
            group['dn'] = dn
        if title is not None:
            group['title'] = title
        if description is not None:
            group['description'] = description
        self._groups[group_id] = group 
        
    security.declarePrivate(ManageGroups, 'setRolesForGroup')
    def setRolesForGroup(self, group_id, roles=()):
        rmanagers = self._getPlugins().listPlugins(IRoleAssignerPlugin)
        if not (rmanagers):
            raise NotImplementedError, ('There is no plugin that can '
                                        'assign roles to groups')
        for rid, rmanager in rmanagers:
            rmanager.assignRolesToPrincipal(roles, group_id)
        self.invalidateGroup(group_id)
    
    security.declareProtected(ManageGroups, 'removeGroup')
    def removeGroup(self, group_id, **kw):
        del self._groups[ group_id ]
    
    security.declareProtected(ManageGroups, 'removePrincipalFromGroup')
    def removePrincipalFromGroup(self, principal_id, group_id):
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
    
    manage_options = ( ( { 'label': 'Groups', 
                           'action': 'manage_groups', }
                         ,
                       )
                     + BasePlugin.manage_options
                     )

    security.declareProtected( ManageGroups, 'manage_groups' )
    manage_groups = PageTemplateFile( 'www/psuumgGroups'
                                    , globals()
                                    , __name__='manage_groups'
                                    )
    
    security.declareProtected( ManageGroups, 'manage_addUMG' )
    def manage_addUMG( self
                     , group_id
                     , dn
                     , title=None
                     , description=None
                     , RESPONSE=None
                     , REQUEST=None
                     ):
        """ Add a group via the ZMI.
        """
        self.addGroup( group_id, title, description, dn )

        message = 'Group+added'

        if RESPONSE is not None:
            RESPONSE.redirect( '%s/manage_groups?manage_tabs_message=%s'
                             % ( self.absolute_url(), message )
                             )
    manage_addUMG = postonly(manage_addUMG)

    security.declareProtected( ManageGroups, 'manage_updateUMG' )
    def manage_updateUMG( self
                          , group_id
                          , dn
                          , title
                          , description
                          , RESPONSE=None
                          , REQUEST=None
                          ):
        """ Update a group via the ZMI.
        """
        self.updateGroup( group_id, title, description, dn )

        message = 'Group+updated'

        if RESPONSE is not None:
            RESPONSE.redirect( '%s/manage_groups?manage_tabs_message=%s'
                             % ( self.absolute_url(), message )
                             )
    manage_updateUMG = postonly(manage_updateUMG)
            
    security.declareProtected( ManageGroups, 'manage_removeUMGs' )
    def manage_removeUMGs( self
                           , group_ids
                           , RESPONSE=None
                           , REQUEST=None
                           ):
        """ Remove one or more groups via the ZMI.
        """
        group_ids = filter( None, group_ids )

        if not group_ids:
            message = 'no+groups+selected'

        else:

            for group_id in group_ids:
                self.removeGroup( group_id )

            message = 'Groups+removed'

        if RESPONSE is not None:
            RESPONSE.redirect( '%s/manage_groups?manage_tabs_message=%s'
                             % ( self.absolute_url(), message )
                             )
    manage_removeUMGs = postonly(manage_removeUMGs)

    security.declarePrivate('_createGroup')
    def _createGroup(self, plugins, group_id, name):
        """ Create group object. For users, this can be done with a
        plugin, but I don't care to define one for that now. Just uses
        PloneGroup.  But, the code's still here, just commented out.
        This method based on PluggableAuthervice._createUser
        """
        return UMG(group_id, name).__of__(self)

    # this is borrowed from PlonePAS's group.py plugin
    security.declarePrivate('_findGroup')
    def _findGroup(self, plugins, group_id, title=None, request=None):
        """ group_id -> decorated_group
        This method based on PluggableAuthService._findGroup
        """

        view_name = '_findGroup-%s' % group_id
        keywords = { 'group_id' : group_id
                   , 'title' : title
                   }

        group = self._createGroup(plugins, group_id, title)

        propfinders = plugins.listPlugins(IPropertiesPlugin)
        for propfinder_id, propfinder in propfinders:

            data = propfinder.getPropertiesForUser(group, request)
            if data:
                group.addPropertysheet(propfinder_id, data)

        groups = self._getPAS()._getGroupsForPrincipal(group, request
                                            , plugins=plugins)
        group._addGroups(groups)

        rolemakers = plugins.listPlugins(IRolesPlugin)

        for rolemaker_id, rolemaker in rolemakers:
            roles = rolemaker.getRolesForPrincipal(group, request)
            if roles:
                group._addRoles(roles)

        group._addRoles(['Authenticated'])

        return group.__of__(self)
    
    security.declareProtected( ManageGroups, 'listGroupInfo' )
    def listGroupInfo( self ):

        """ -> ( {}, ...{} )

        o Return one mapping per group, with the following keys:

          - 'id' 
        """
        return self._groups.values()

    security.declareProtected( ManageGroups, 'getGroupInfo' )
    def getGroupInfo( self, group_id ):

        """ group_id -> {}
        """
        return self._groups[ group_id ]
    
InitializeClass(PSUUMGGroupManager)

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

class UMG(PloneGroup):
    """Plone expects a user to come, with approximately the same
    behavior as a user.
    """

    security = ClassSecurityInfo()

    security.declarePublic('getId')
    def getId(self, unprefixed=None):
        """ -> user ID
        Modified to accept silly GRUF param.
        """
        return self._id
    
    security.declarePublic('addMember')
    def addMember(self, id):
        """Add the existing member with the given id to the group
        """
        pass

    security.declarePublic('removeMember')
    def removeMember(self, id):
        """Remove the member with the provided id from the group.
        """
        pass

InitializeClass(UMG)
