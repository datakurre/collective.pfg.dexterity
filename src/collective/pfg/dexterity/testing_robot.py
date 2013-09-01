# -*- coding: utf-8 -*-
from plone.app.robotframework.remote import RemoteLibrary


class RemoteKeywordsLibrary(RemoteLibrary):
    """Robot Framework remote keywords library
    """

    def portal_type_is_installed(self, portal_type):
        ids = self.portal_types.objectIds()
        titles = map(lambda x: x.title, self.portal_types.objectValues())
        assert portal_type in ids + titles,\
            u"'%s' was not found in portal types." % portal_type

    def change_ownership(self, path, user_id):
        from AccessControl.interfaces import IOwned
        obj = self.restrictedTraverse(path)

        acl_users = self.get('acl_users')
        if acl_users:
            user = acl_users.getUser(user_id)
        if not user:
            root = self.getPhysicalRoot()
            acl_users = root.get('acl_users')
            if acl_users:
                user = acl_users.getUser(user_id)

        IOwned(obj).changeOwnership(user, recursive=1)

    def create_type_with_date_field(self, name):
        from plone.dexterity.fti import DexterityFTI
        fti = DexterityFTI(str(name), title=name)
        fti.behaviors = ("plone.app.dexterity.behaviors.metadata.IBasic",)
        fti.model_source = u"""\
<model xmlns="http://namespaces.plone.org/supermodel/schema">
<schema>
<field name="duedate" type="zope.schema.Date">
  <description />
  <required>False</required>
  <title>Due Date</title>
</field>
</schema>
</model>"""
        fti.global_allow = True
        self.portal_types._setObject(str(name), fti)

