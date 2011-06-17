"""Unit tests for IGroups plugin"""
from Products.psuauthz.tests.base_integration import (
    BaseAffilIntegrationTestCase, BaseUMGIntegrationTestCase)


class TestUMGGroupIntrospection(BaseUMGIntegrationTestCase):
    def test_get_group_members(self):
        user_ids = self._plugin.getGroupMembers('Staff')
        self.failUnlessEqual(user_ids, ['asd98', 'pkj12'])


class TestAffilGroupIntrospection(BaseAffilIntegrationTestCase):
    def test_get_group_by_id(self):
        # Check for nothing when group doesn't exist.
        group = self._plugin.getGroupById('no group')
        self.failUnless(group is None, "Expected nothing, got something? "
            "Got %s of type %s" % (group, type(group)))
        # Check for an actual group.
        from Products.psuauthz.affiliation import student
        group = self._plugin.getGroupById(student.id)
        from Products.PlonePAS.plugins.autogroup import VirtualGroup
        self.failUnless(isinstance(group, VirtualGroup), "The returned "
            "object is not what was expected. Got %s" % type(group))

    def test_get_groups(self):
        from Products.psuauthz.affiliation import affiliation_mapping
        aff_group_ids = [ aff.id for aff in affiliation_mapping.values() ]
        groups = self._plugin.getGroups()
        from Products.PlonePAS.plugins.autogroup import VirtualGroup
        for group in groups:
            self.failUnless(isinstance(group, VirtualGroup), "The returned "
                "object is not what was expected. Got %s" % type(group))
            self.failUnless(group.getId() in aff_group_ids)

    def test_get_group_ids(self):
        from Products.psuauthz.affiliation import affiliation_mapping
        actual_group_ids = [ aff.id for aff in affiliation_mapping.values() ]
        actual_group_ids.sort()
        group_ids = self._plugin.getGroupIds()
        group_ids.sort()
        self.failUnlessEqual(group_ids, actual_group_ids)

    def test_get_group_members(self):
        from Products.psuauthz.affiliation import staff
        user_ids = self._plugin.getGroupMembers(staff.id)
        # This should return nothing, because we can't query the entire
        # directory for, example staff members, which contains throusands
        # of entries.
        self.failUnlessEqual(user_ids, tuple())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUMGGroupIntrospection))
    suite.addTest(makeSuite(TestAffilGroupIntrospection))
    return suite
