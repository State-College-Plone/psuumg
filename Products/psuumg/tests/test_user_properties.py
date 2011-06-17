"""Unit tests for user property provider plugin"""

from Products.psuumg.tests.base import BaseUMGMockNetworkingUnitTest
from Products.PluggableAuthService.PropertiedUser import PropertiedUser


class TestProperties(BaseUMGMockNetworkingUnitTest):
    def test_user_properties(self):
        self.failUnlessEqual(self._plugin.getPropertiesForUser(PropertiedUser('cst45')), {'fullname': 'Cally Turk', 'email': 'cst45@psu.edu'})


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProperties))
    return suite
