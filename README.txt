Description

    Allows use of Penn State UMGs in Plone.


Current Status

This product is a "work in progress" and is not ready for production use.

It's thought that the product is able to pull down groups but might run into all
sorts of exciting problems if any of the users in the group didn't already exist
in the Plone site. The next logical step would be to enumerate the users in the
group and add the non-existing ones to the Plone site using LDAP to get the
information on the person.

It's unknown which version of Plone this product was developed for but based on
the version of LDAP that setup.py calls for, the guess is Plone 3.x

For those who want to develop this product further, be aware that PlonePAS
monkey patches the heck out of PluggableAuthService (PAS) and makes it really 
difficult to figure out what is going on. It looks like over the years PlonePAS
made some assumptions about groups that go beyond the "required" interfaces, so
only implementing the PAS interfaces for anything group-related is not sufficient
to make a plugin work.
