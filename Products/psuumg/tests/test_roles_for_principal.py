"""Unit tests for IRolesPlugin"""

from Products.psuauthz.tests.base import BaseUMGMockNetworkingUnitTest
from Products.PluggableAuthService.PropertiedUser import PropertiedUser

from Products.psuauthz.tests.mocks import asd98_roles

class TestRolesForPrincipal(BaseUMGMockNetworkingUnitTest):
    def test_roles_for_principal(self):
        roles = list(self._plugin.getRolesForPrincipal(PropertiedUser('asd98')))
        roles.sort()
        self.failUnlessEqual(roles, asd98_roles)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRolesForPrincipal))
    return suite
