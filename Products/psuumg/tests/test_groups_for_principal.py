"""Unit tests for IGroups plugin"""

from Products.psuauthz.tests.base import \
    BaseAffilMockNetworkUnitTest, BaseUMGMockNetworkingUnitTest
from Products.psuauthz.tests.mocks import asd98_groups, affiliation_data


class UMGTestGroupsForPrincipal(BaseUMGMockNetworkingUnitTest):
    def test_groups_for_principal(self):
        from Products.PluggableAuthService.PropertiedUser import \
            PropertiedUser
        puser = PropertiedUser('asd98')
        groups = list(self._plugin.getGroupsForPrincipal(puser))
        groups.sort()
        self.failUnlessEqual(groups, asd98_groups)


class AffiliationTestGroupsForPrincipal(BaseAffilMockNetworkUnitTest):
    def test_groups_for_principal(self):
        from Products.PluggableAuthService.PropertiedUser import \
            PropertiedUser
        uid = 'asd98'
        puser = PropertiedUser(uid)
        puser.isGroup = lambda: False
        groups = list(self._plugin.getGroupsForPrincipal(puser))
        groups.sort()
        from Products.psuauthz.affiliation import affiliation_mapping
        expected_results = [affiliation_mapping[affiliation_data[uid]].id]
        self.failUnlessEqual(groups, expected_results)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(UMGTestGroupsForPrincipal))
    suite.addTest(makeSuite(AffiliationTestGroupsForPrincipal))
    return suite
