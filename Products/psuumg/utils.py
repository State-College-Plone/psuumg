import ldap
import os.path
from Globals import package_home
from time import time
from logging import getLogger
from plone.memoize.ram import cache

www_directory = os.path.join(package_home(globals()), 'www')
tests_directory = os.path.join(package_home(globals()), 'tests')
logger = getLogger('Products.psuumg')

def create_member_filter(members):
    """Creates a search filter from the member ids."""
    member_filter = ''
    for m in members:
        member_filter += '(uid=%s)' % m
    if len(members) > 1:
        member_filter = '(|%s)' % member_filter
    return member_filter


def cache_key(fun, host, base_dn, umg_ob):
    return (host, umg_ob.dn, umg_ob.groups, time() // (24 * 60 * 60))


def member_cache_key(fun, host, base_dn, uid):
    return (host, host, base_dn, uid, time() // (24 * 60 * 60))

def valid_entry_cache_key(fun, host, dn):
    return (host, dn, time() // (24 * 60 * 60))

@cache(cache_key)
def umg_member_search(host, base_dn, umg_ob):
    """Returns the ldap search results for the given DN."""
    conn = ldap.open(host)
    member_attr = 'memberUid'
    try:
        # search the user manged group (UMG) for members
        umg = conn.search_s(umg_ob.dn, ldap.SCOPE_SUBTREE, attrlist=[member_attr])
        if len(umg) == 0:
            logger.error("%s is not a valid UMG.")
        else:
            members_list = umg[0][1][member_attr]

        # search for more info about the members of the UMG
        members = []
        # we need to search in increments, otherwise will receive an
        #   ldap.SIZELIMIT_EXCEEDED exception for large groups
        step = 20
        member_list_length = len(members_list)
        for i in range(0, member_list_length, step):
            if not (i + step) > member_list_length:
                end = i + step
            else:
                end = member_list_length
            members_to_lookup = members_list[i:end]
            member_filter = create_member_filter(members_to_lookup)
            members += conn.search_s(base_dn, ldap.SCOPE_ONELEVEL, member_filter)
    except ldap.SERVER_DOWN:
        logger.error("LDAP server @ %s seems to be unresponsive." % host)
        members = []
    return members

def get_member_and_group_data(host, base_dn, umgs):
    users = {}
    groups = set()
    for umg_id, umg in umgs:
        member_data = umg_member_search(host, base_dn, umg)

        for dn, info in member_data:
            id = info['uid'][0]
            # this gets as close to fullname as we are able
            fullname = info.get('displayName', [''])[0]
            # the fullname is in ALL CAPS, so let's make it look readable
            fullname = fullname.title()
            email = info.get('mail', [''])[0] # primary email address

            default_user_data = {'groups': set(),
                                 'roles': set(),
                                 'fullname': fullname,
                                 'email': email,
                                 }
            member = users.setdefault(id, default_user_data)

            # add member groups and to groups
            for group in umg.groups:
                member['groups'].add(group)
            member['groups'].add(umg.title)
            groups.add(umg.title)
            # add member roles to the member
            for role in umg.roles:
                member['roles'].add(role)

    return users, groups

@cache(member_cache_key)
def member_search(host, base_dn, uid):
    """Returns the ldap search results for the given uid. A single result
    is returned"""
    conn = ldap.open(host)
    search_filter = '(uid=%s)' % uid
    try:
        entry = conn.search_s(base_dn, ldap.SCOPE_SUBTREE,
            filterstr=search_filter)
        if not entry:
            entry = ('', {},)
        else:
            # We only want the first entry.
            entry = entry[0] # Results in: (dn, attrs)
    except ldap.SERVER_DOWN:
        msg = "LDAP server @ %s seems to be unresponsive." % host
        logger.error(msg)
        raise LdapUnavailable(msg)
    attribute_data = entry[1]
    return attribute_data

@cache(valid_entry_cache_key)
def is_valid_ldap_entry(host, dn):
    """Returns a boolean value to validate that the element given exists
    in the directory."""
    conn = ldap.open(host)
    try:
        entry = conn.search_s(dn, ldap.SCOPE_BASE)
    except ldap.NO_SUCH_OBJECT:
        return False
    if len(entry) > 0:
        return True
    return False
