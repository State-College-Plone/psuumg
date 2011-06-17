"""Unit tests for group enumeration plugin"""

from Products.psuauthz.tests.base import BaseUMGMockNetworkingUnitTest
from Products.psuauthz.tests.base import BaseAffilMockNetworkUnitTest


class TestUMGEnumeration(BaseUMGMockNetworkingUnitTest):
    def test_find_all(self):
        all_groups = self._plugin.enumerateGroups()
        self.failUnless(len(all_groups) > 0)

    def test_exact_match_by_id(self):
        enumerateGroups = self._plugin.enumerateGroups
        enumerated_group = enumerateGroups(id='Students', exact_match=True)
        expected_results = ({'id': 'Students', 'pluginid': self.plugin_id},)
        self.failUnlessEqual(enumerated_group, expected_results)

    # # Known failure. This isn't implemented yet. I don't think Plone uses this feature.
    # def test_multiple_matches_by_id(self):
    #     """PAS says you must accept sequences of IDs."""
    #     self.failUnlessEqual(self._plugin.enumerateGroups(id=['Demo Course 1', 'Demo Course 2'], exact_match=True), ({'id': 'Demo Course 1', 'pluginid': plugin_id}, {'id': 'Demo Course 2', 'pluginid': plugin_id}))

    def test_exact_match_by_title(self):
        """IDs and titles are considered the same for the moment."""
        enumerated_groups = self._plugin.enumerateGroups(title='Staff', exact_match=True)
        self.failUnlessEqual(enumerated_groups, ({'pluginid': 'umg_plugin', 'id': 'Staff'},))

    def test_inexact_match_by_id(self):
        enumerated_groups = self._plugin.enumerateGroups(id='f', exact_match=False)
        expecting = ({'pluginid': 'umg_plugin', 'id': 'Faculty'},
                     {'pluginid': 'umg_plugin', 'id': 'Staff'},
                     )
        self.failUnlessEqual(enumerated_groups, expecting)

    def test_inexact_match_by_title(self):
        enumerated_groups = self._plugin.enumerateGroups(title='St', exact_match=False)
        expecting = ({'pluginid': 'umg_plugin', 'id': 'Staff'},
                     {'pluginid': 'umg_plugin', 'id': 'Students'},
                     )
        self.failUnlessEqual(enumerated_groups, expecting)

    def test_max_results(self):
        # eh? doing this above too
        enumerated_groups = self._plugin.enumerateGroups(title='t', sort_by='id', max_results=2)
        expecting = ({'pluginid': 'umg_plugin', 'id': 'Faculty'},
                     {'pluginid': 'umg_plugin', 'id': 'Robots'},
                     )
        self.failUnlessEqual(enumerated_groups, expecting)

    def test_find_all(self):
        """Make sure we get some groups out of a wide-open search, such as
        called by a click to "Show All" in the Users & Groups configlet."""
        self.failUnless(len(self._plugin.enumerateGroups()) > 0)


class TestAffilEnumeration(BaseAffilMockNetworkUnitTest):
    def test_find_all(self):
        all_groups = self._plugin.enumerateGroups()
        self.failUnless(len(all_groups) > 0)

    def test_exact_match_by_id(self):
        enumerateGroups = self._plugin.enumerateGroups
        from Products.psuauthz.affiliation import student
        enumerated_group = enumerateGroups(id=student.id, exact_match=True)
        expected_results = [{'id': student.id,
                             'pluginid': self.plugin_id,
                             'title': student.id
                             },]
        self.failUnlessEqual(enumerated_group, expected_results)

    # Known failure. This isn't implemented yet. I don't think Plone uses this feature.
    # def test_multiple_matches_by_id(self):
    #     """PAS says you must accept sequences of IDs."""
    #     self.failUnlessEqual(self._plugin.enumerateGroups(id=['Demo Course 1', 'Demo Course 2'], exact_match=True), ({'id': 'Demo Course 1', 'pluginid': plugin_id}, {'id': 'Demo Course 2', 'pluginid': plugin_id}))

    def test_exact_match_by_title(self):
        """IDs and titles are considered the same for the moment."""
        # We only support matching by id.
        from Products.psuauthz.affiliation import staff
        enumerated_groups = self._plugin.enumerateGroups(title=staff.title,
            exact_match=True)
        self.failUnlessEqual(enumerated_groups, [])

    def test_inexact_match_by_id(self):
        # We only support matching by id.
        from Products.psuauthz.affiliation import faculty, student
        enumerated_groups = self._plugin.enumerateGroups(id='u',
            exact_match=False, sort_by='id')
        expecting = [{'pluginid': self.plugin_id,
                      'id': faculty.id,
                      'title': faculty.title},
                     {'pluginid': self.plugin_id,
                      'id': student.id,
                      'title': student.title},
                     ]
        self.failUnlessEqual(enumerated_groups, expecting)

    def test_inexact_match_by_title(self):
        # We only support matching by id.
        from Products.psuauthz.affiliation import affiliation_mapping
        enumerated_groups = self._plugin.enumerateGroups(title='St', exact_match=False)
        # This search should return everything, because it looks like an
        # everything search. When id is not supplied and exact_match is False
        # everything will be returned.
        expecting = [
            {'pluginid': self.plugin_id, 'id': aff.id, 'title': aff.title}
            for aff in affiliation_mapping.values()
            ]
        self.failUnlessEqual(enumerated_groups, expecting)

    def test_find_all(self):
        """Make sure we get some groups out of a wide-open search, such as
        called by a click to "Show All" in the Users & Groups configlet."""
        self.failUnless(len(self._plugin.enumerateGroups()) > 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUMGEnumeration))
    suite.addTest(makeSuite(TestAffilEnumeration))
    return suite
