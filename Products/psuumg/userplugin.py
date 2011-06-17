# -*- coding: utf-8 -*-
import logging
import urllib
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from OFS.SimpleItem import SimpleItem
from Products.PluggableAuthService.utils import (
    classImplements,
    createKeywords,
    createViewName,
    postonly)
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.permissions import ManageUsers
import Products.PlonePAS.plugins.group as PlonePasGroupPlugin
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.psuumg.interfaces import IPSUUserPlugin

# Plugin Interfaces
from Products.PluggableAuthService.interfaces.plugins import (
    IUserEnumerationPlugin,
    IPropertiesPlugin,
    IRolesPlugin)

logger = logging.getLogger('Products.psuumg')


class UserPlugin(BasePlugin):
    implements(IUserManagedGroupsPlugin)
    security = ClassSecurityInfo()
    meta_type = 'User Managed Groups Plugin'
    base_dn = u'dc=psu,dc=edu'
    host = FieldProperty(IUserManagedGroupsPlugin['host'])

    def __init__(self, id, host, email_domain):
        BasePlugin.__init__(self)
        self.host = unicode(host)

    # ########################## #
    #   IUserEnumerationPlugin   #
    # ########################## #
    # This plugin is here so that IGroupIntrospection's methods
    # will return users.
    def enumerateUsers(self, id=None, login=None, exact_match=False, sort_by=None, max_results=None, fullname=None, **kw):
        user_ids = set()  # tuples of (user ID, login)

        # Build list of user IDs we should return:
        if exact_match:  # Should this be case-sensitive?
            if login:
                if login in self._users:
                    user_info = self._verifyUserElsewhere(login)  # See if the user already exists care of another PAS plugin. If so, the user may have an ID that isn't its login name.
                    user_id = user_info and user_info['id'] or login  # If user doesn't exist, it's a user we're dynamically manifesting, so we can assume id == login.
                    user_ids.add((user_id, login))
            if id:
                if id in self._users:  # TODO: IHNI if this block makes sense.
                    user_ids.add((id, id))
        else:  # Do case-insensitive containment searches. Searching on '' returns everything.
            if login is not None:
                login_lower = login.lower()
            if id is not None:
                id_lower = id.lower()
            if fullname is not None:
                fullname_lower = fullname.lower()
            for k, user_info in self._users.iteritems():  # TODO: Pretty permissive. Should we be searching against logins AND IDs? We might also optimize to avoid redundant tests of None-ship.
                k_lower = k.lower()
                if (id is None and login is None and fullname is None) or \
                   (id is not None and id_lower in k_lower) or \
                   (login is not None and login_lower in k_lower) or \
                   (fullname is not None and fullname_lower in user_info['fullname'].lower()):
                    user_ids.add((k, k))

        # For each gathered user ID, flesh out a user info record:
        plugin_id = self.getId()
        user_infos = [{'id': x, 'login': y, 'pluginid': plugin_id} for (x, y) in user_ids]

        # Sort, if requested:
        if sort_by in ['id', 'login']:
            user_infos.sort(key=lambda x: x[sort_by])

        # Truncate, if requested:
        if max_results is not None:
            del user_infos[max_results:]

        return tuple(user_infos)

    security.declarePrivate('_verifyUserElsewhere')
    def _verifyUserElsewhere(self, login):
        """Like PAS's _verifyUser, turn a login into an info dict. However, look only in other enumerator plugins, skipping ours so we don't infinitely recurse."""
        # Ripped off from PAS 1.6.1.
        pas = self._getPAS()
        criteria = {'exact_match': True, 'login': login}
        view_name = createViewName('_verifyUser', login)
        keywords = createKeywords(**criteria)
        cached_info = pas.ZCacheable_get(view_name=view_name,
                                         keywords=keywords,
                                         default=None)  # somewhat evil, sharing a private(?) cache with PAS. But this runs all the time, and that code hasn't changed forever.
        if cached_info is not None:
            return cached_info


    # ##################### #
    #   IPropertiesPlugin   #
    # ##################### #
    def getPropertiesForUser(self, user, request=None):
        login = user.getUserName()
        is_group = getattr(user, 'isGroup', lambda: None)()

        if is_group:
            if login in self._groups:
                return {'title': login}  # title == id == login. Yuck. See comments under enumerateGroups().
        else:
            u = self._users.get(login)
            if u:
                ret = {'fullname': u['fullname'], 'email': u.get('email', None)}
                return ret
        return {}

    # ################ #
    #   IRolesPlugin   #
    # ################ #
    #security.declarePrivate('getRolesForPrincipal')
    #def getRolesForPrincipal(self, principal, request=None):
        #"""See IRolesPlugin."""
        #id = principal.getId()
        #user = self._users.get(id, None)

        #roles = None
        #if user:
            #roles = user.get('roles', None)

        #return roles

    # ################################## #
    #   Zope Managment Interface (ZMI)   #
    # ################################## #
    manage_options = (({'label': 'User Managed Groups',
                        'action': 'manage_umgs'},
                       # {'label': 'Options',
                       # 'action': 'manage_config'},
                       ) + BasePlugin.manage_options
                      )

    security.declareProtected(ManageUsers, 'manage_umgs')
    manage_umgs = PageTemplateFile('www/manage_umgs',
                                    globals(),
                                    __name__='manage_umgs',
                                    )

    security.declareProtected(ManageUsers, 'manage_addUMG')
    def manage_addUMG(self, id, dn, title='', groups=tuple(), roles=tuple(), RESPONSE=None):
        """Add a UMG via the ZMI."""
        if not is_valid_ldap_entry(self.host, dn):
            msg = "The UMG provided did not validate (likely does not " \
                "exist). Please check that you entered it correctly and " \
                "try again."
            if RESPONSE:
                url = "%s/manage_umgs" % self.absolute_url()
                query_data = {
                    'adding': '1',
                    'manage_tabs_message': msg,
                    'id': id, 'dn': dn, 'title': title,
                    'groups': groups, 'roles': roles
                    }
                url = '?'.join([url, urllib.urlencode(query_data)])
                RESPONSE.redirect(url)
                return
            else:
                raise ValueError(msg)
        self.addUMG(id, dn, title=title, groups=groups, roles=roles)
        if RESPONSE:
            message = 'UMG+added'
            RESPONSE.redirect('%s/manage_umgs?manage_tabs_message=%s'
                              % (self.absolute_url(), message))

    security.declareProtected(ManageUsers, 'manage_updateUMG')
    def manage_updateUMG(self, id, dn, title='', groups=tuple(), roles=tuple(), RESPONSE=None):
        """Add a UMG via the ZMI."""
        umg = self._getOb(id)
        umg.dn = unicode(dn)
        umg.title = unicode(title)
        umg.groups = groups
        umg.roles = roles

        if RESPONSE:
            message = 'UMG+updated'
            RESPONSE.redirect('%s/manage_umgs?manage_tabs_message=%s'
                              % (self.absolute_url(), message))


implementedInterfaces = [
    IUserEnumerationPlugin,
    IPropertiesPlugin,
#    IRolesPlugin,
    ]
classImplements(UserManagedGroupsPlugin, *implementedInterfaces)
InitializeClass(UserManagedGroupsPlugin)  # Make the security declarations work.
