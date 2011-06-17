"""Unit tests for user enumeration plugin"""

from Products.psuauthz.tests.base_integration import BaseUMGIntegrationTestCase


class TestEnumeration(BaseUMGIntegrationTestCase):
    def test_exact_match_by_id(self):
        """Make sure we don't get into infinite recursion. This actually
        happens in Plone after all, so we'd better fix it."""
        try:
            u = self._plugin.enumerateUsers(login=u'asd98', exact_match=True)
        except RuntimeError:
            self.fail("Hit a RuntimeError, likely a max recusion depth error"
                "from the user enumerator calling PAS.getUser() and vice "
                "versa.")
        else:
            self.failUnlessEqual(u, (
                {'id': 'asd98',
                 'login': 'asd98',
                 'pluginid': self.plugin_id},)
                )

    def test_fullname(self):
        """Test search by fullname, like Plone 3.1's U&G configlet search."""
        # This is likely impossible with PSU's ldap search capabilities.
        enumerated_user = self._plugin.enumerateUsers(fullname='Pick Jackson')
        expected_results = ({'id': 'pkj12', 'login': 'pkj12',
            'pluginid': self.plugin_id},)
        self.failUnlessEqual(enumerated_user, expected_results)

    def test_find_all(self):
        """Make sure we get some users out of a wide-open search, such as
        called by a click to "Show All" in the Users & Groups configlet."""
        self.failUnless(len(self._plugin.enumerateUsers()) > 0)

    # TODO: borrow some other tests from test_group_enumeration.


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestEnumeration))
    return suite
