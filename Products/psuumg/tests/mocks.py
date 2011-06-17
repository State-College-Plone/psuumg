"""Mocked out functions for testing"""

import os

from Products.psuumg.utils import tests_directory


class MonkeyWrench(object):
    """A monkey wrench"""

    orig_func = None
    func = None
    name = None
    attr = None

    def __init__(self, cls_name, cls_attr, mock_func, is_property=False):
        self.name = cls_name
        self.attr = cls_attr
        if is_property:
            self.func = property(mock_func)
        else:
            self.func = mock_func


class ToolBox(object):
    """A toolbox (singleton) for monkey wrenches."""

    wrenches = {}

    def reg(self, cls_name, cls_attr, func, is_property=False):
        self.reg_wrench(MonkeyWrench(cls_name, cls_attr, func, is_property))

    def reg_wrench(self, wrench):
        if not isinstance(wrench, MonkeyWrench):
            raise TypeError('Excepted a MonkeyWrench, got a %s' % type(wrench))
        self.wrenches[wrench.name] = wrench

    # def unreg(self):
    #     pass


toolbox = ToolBox()

def monkeypatch(plugin_cls):
    """Replace the networking code with stuff that returns test data."""
    cls_name = plugin_cls.__name__
    monkey_wrench = toolbox.wrenches[cls_name]
    monkey_wrench.original_func = getattr(plugin_cls, monkey_wrench.attr)
    setattr(plugin_cls, monkey_wrench.attr, monkey_wrench.func)

def unmonkeypatch(plugin_cls):
    """Put the networking code back."""
    cls_name = plugin_cls.__name__
    monkey_wrench = toolbox.wrenches[cls_name]
    setattr(plugin_cls, monkey_wrench.attr, monkey_wrench.original_func)


# ################################# #
# Mocks for UserManagedGroupsPlugin #
# ################################# #

# separate declaration because we are testing the users groups
asd98_groups = ['Faculty', 'Staff']
asd98_roles = ['Manager']

def mock_data(obj):
    users = {
        u'cst45': {u'fullname': "Cally Turk",
                   u'groups': set(['Students']),
                   },
        u'pkj12': {u'fullname': "Pick Jackson",
                   u'groups': set(['Staff', 'Students']),
                   },
        u'asd98': {u'fullname': "Al Dwelt",
                   u'groups': set(asd98_groups),
                   u'roles': set(asd98_roles),
                   },
        u'jfive': {u'fullname': "Johnny Five",
                   u'groups': set(['Robots']),
                   },
        }
    groups = set(['Students', 'Staff', 'Faculty', 'Robots'])
    return users, groups

toolbox.reg('UserManagedGroupsPlugin', '_data', mock_data, is_property=True)


# ############################### #
# Mocks for UserAffiliationPlugin #
# ############################### #

affiliation_data = {
    u'cst45': 'STAFF',
    u'pkj12': 'FACULTY',
    u'cas11': 'FACULTY',
    u'asd98': 'MEMBER',
    u'jfive': 'ROBOT',
    }

def mock_get_member_affiliation(obj, uid):
    affiliation_attr = 'eduPersonPrimaryAffiliation'
    return affiliation_data[uid]

toolbox.reg('UserAffiliationPlugin', 'get_member_affiliation',
    mock_get_member_affiliation)
