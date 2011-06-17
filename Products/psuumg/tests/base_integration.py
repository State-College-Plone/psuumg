"""Base class for integration tests"""

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from Products.CMFCore.utils import getToolByName
from Testing import ZopeTestCase

from Products.psuauthz.tests.mocks import monkeypatch, unmonkeypatch

@onsetup
def setup_umgplugin():
    # Load the ZCML configuration
    fiveconfigure.debug_mode = True
    import Products.psuauthz
    zcml.load_config('configure.zcml', Products.psuauthz)
    fiveconfigure.debug_mode = False

    # Tell the testing framework the package is available
    ZopeTestCase.installPackage('Products.psuauthz')

setup_umgplugin()
PloneTestCase.setupPloneSite(products=['Products.psuauthz'])


class BaseIntegrationTestCase(PloneTestCase.PloneTestCase):

    plugin_id = 'plugin'
    plugin_host = 'host'

    def makeOne(self):
        raise NotImplementedError("You much define how to make a plugin.")

    def destroyOne(self):
        self._acl_users.manage_delObjects(self.plugin_id)

    def beforeTearDown(self):
        self._acl_users.manage_delObjects(self.plugin_id)
        from Products.psuauthz.tests.mocks import unmonkeypatch
        from Products.psuauthz.umg import UserManagedGroupsPlugin
        unmonkeypatch(UserManagedGroupsPlugin)

    @property
    def _acl_users(self):
        """Return the acl_users folder in the Plone site."""
        return getToolByName(self.portal, 'acl_users')

    @property
    def _plugin(self):
        return self._acl_users[self.plugin_id]


class BaseUMGIntegrationTestCase(BaseIntegrationTestCase):

    plugin_id = 'umg_plugin'
    plugin_host = u'ldap.psu.edu'
    plugin_email_domain = u'psu.edu'
    _items = (
        (u'umg/up.tlt.tltstaff', ('Group',),), # lots of people
        (u'umg/up.weblion.clubsites.admins', ('Group',),), # few people
        (u'umg/up.weblion.clubsites.interns', ('Group',),), # doens't exist
        )

    def makeOne(self):
        # Install an umgplugin plugin:
        acl_users = self._acl_users
        # http://wiki.zope.org/zope2/ObjectManager
        constructors = acl_users.manage_addProduct['Products.psuauthz']
        constructors.manage_addUMGPlugin(self.plugin_id, self.plugin_host)

        # Activate it:
        # plugins is a PluginRegistry
        plugins = acl_users['plugins']
        from Products.psuauthz.umg import implementedInterfaces
        for interface in implementedInterfaces:
            plugins.activatePlugin(interface, self.plugin_id)

    def afterSetUp(self):
        from Products.psuauthz.umg import UserManagedGroupsPlugin
        monkeypatch(UserManagedGroupsPlugin)
        self.makeOne()

    def beforeTearDown(self):
        self.destroyOne()
        from Products.psuauthz.umg import UserManagedGroupsPlugin
        unmonkeypatch(UserManagedGroupsPlugin)


class BaseAffilIntegrationTestCase(BaseIntegrationTestCase):

    plugin_id = 'affil_plugin'
    plugin_host = u'ldap.psu.edu'

    def makeOne(self):
        # Install an umgplugin plugin:
        acl_users = self._acl_users
        # http://wiki.zope.org/zope2/ObjectManager
        constructors = acl_users.manage_addProduct['Products.psuauthz']
        constructors.manage_addAffiliationPlugin(self.plugin_id, self.plugin_host)

        # Activate it:
        # plugins is a PluginRegistry
        plugins = acl_users['plugins']
        from Products.psuauthz.affiliation import implementedInterfaces
        for interface in implementedInterfaces:
            plugins.activatePlugin(interface, self.plugin_id)

    def afterSetUp(self):
        from Products.psuauthz.affiliation import UserAffiliationPlugin
        monkeypatch(UserAffiliationPlugin)
        self.makeOne()

    def beforeTearDown(self):
        self.destroyOne()
        from Products.psuauthz.affiliation import UserAffiliationPlugin
        unmonkeypatch(UserAffiliationPlugin)
