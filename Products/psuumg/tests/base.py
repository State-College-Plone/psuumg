"""A testing base class providing some common functionality"""
import os
from unittest import TestCase

from Products.psuumg.utils import tests_directory
from Products.psuumg.tests.mocks import monkeypatch, unmonkeypatch


class BaseTestCase(TestCase):
    """Instantiates a PAS plugin and fills out some sample data."""

    def makeOne(self):
        raise NotImplementedError("You need to create this method in order" \
            "to make a plugin.")

    def setUp(self):
        self._plugin = self.makeOne()

    def tearDown(self):
        del self._plugin


class BaseUMGUnitCase(BaseTestCase):

    plugin_id = 'umg_plugin'
    plugin_host = u'ldap.psu.edu'
    _items = (
        (u'umg/up.tlt.tltstaff', ('Group',),),  # lots of people
        (u'umg/up.weblion.clubsites.admins', ('Group',),),  # few people
        (u'umg/up.weblion.clubsites.interns', ('Group',),),  # doens't exist
        )

    def makeOne(self):
        from Products.psuumg.userplugin import UserPlugin
        plugin = UserPlugin(self.plugin_id, self.plugin_host)
        for dn, groups in self._items:
            id = dn.split('.')[-1]
            plugin.addUMG(id, dn, title=id, groups=groups)
        return plugin


class BaseAffilUnitCase(BaseTestCase):

    plugin_id = 'affil_plugin'
    plugin_host = u'ldap.psu.edu'

    def makeOne(self):
        from Products.psuumg.affiliation import UserAffiliationPlugin
        plugin = UserAffiliationPlugin(self.plugin_id, self.plugin_host)
        return plugin


class BaseUMGMockNetworkingUnitTest(BaseUMGUnitCase):
    """This class rigs it so that the plugin returns sample data and fake
    network interaction."""

    def setUp(self):
        from Products.psuumg.umg import UserManagedGroupsPlugin
        monkeypatch(UserManagedGroupsPlugin)
        super(BaseUMGMockNetworkingUnitTest, self).setUp()

    def tearDown(self):
        from Products.psuumg.umg import UserManagedGroupsPlugin
        super(BaseUMGMockNetworkingUnitTest, self).tearDown()
        unmonkeypatch(UserManagedGroupsPlugin)


class BaseAffilMockNetworkUnitTest(BaseAffilUnitCase):

    def setUp(self):
        from Products.psuumg.affiliation import UserAffiliationPlugin
        monkeypatch(UserAffiliationPlugin)
        self._plugin = self.makeOne()

    def tearDown(self):
        from Products.psuumg.affiliation import UserAffiliationPlugin
        del self._plugin
        unmonkeypatch(UserAffiliationPlugin)
