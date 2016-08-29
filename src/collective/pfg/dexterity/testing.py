# -*- coding: utf-8 -*-
from plone.app.robotframework import AutoLogin
from plone.app.robotframework import QuickInstaller
from plone.app.robotframework import RemoteLibraryLayer
from plone.app.robotframework.remote import RemoteLibrary
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.interface import alsoProvides

import pkg_resources


try:
    from plone.protect.interfaces import IDisableCSRFProtection
    HAS_CSRF_PROTECTION = True
except ImportError:
    HAS_CSRF_PROTECTION = False

try:
    HAVE_PLONE_5 = False
    if pkg_resources.get_distribution('Products.CMFPlone>=5.0'):
        HAVE_PLONE_5 = True
        import plone.app.contenttypes
except pkg_resources.VersionConflict:
    pass


class CollectivePFGDexterityLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.pfg.dexterity
        self.loadZCML(package=collective.pfg.dexterity)

        z2.installProduct(app, 'Products.PloneFormGen')
        z2.installProduct(app, 'Products.DataGridField')
        z2.installProduct(app, 'collective.pfg.dexterity')

        if HAVE_PLONE_5:
            self.loadZCML(package=plone.app.contenttypes)

    def setUpPloneSite(self, portal):
        # PLONE_FIXTURE has no default workflow chain set
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')

        self.applyProfile(portal, 'plone.app.dexterity:default')
        self.applyProfile(portal, 'Products.PloneFormGen:default')
        self.applyProfile(portal, 'Products.DataGridField:default')
        self.applyProfile(portal, 'collective.pfg.dexterity:default')

        if HAVE_PLONE_5:
            self.applyProfile(portal, 'plone.app.contenttypes:default')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'collective.pfg.dexterity')
        z2.uninstallProduct(app, 'Products.DataGridField')
        z2.uninstallProduct(app, 'Products.PloneFormGen')

    def testSetUp(self):
        # XXX: How should we invalidate Dexterity fti.lookupSchema() cache?
        import plone.dexterity.schema
        for name in dir(plone.dexterity.schema.generated):
            if name.startswith('plone'):
                delattr(plone.dexterity.schema.generated, name)
        plone.dexterity.schema.SCHEMA_CACHE.clear()


COLLECTIVE_PFG_DEXTERITY_FIXTURE = CollectivePFGDexterityLayer()


COLLECTIVE_PFG_DEXTERITY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_PFG_DEXTERITY_FIXTURE,),
    name='Integration')
COLLECTIVE_PFG_DEXTERITY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_PFG_DEXTERITY_FIXTURE,),
    name='Functional')
COLLECTIVE_PFG_DEXTERITY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_PFG_DEXTERITY_FIXTURE, z2.ZSERVER_FIXTURE),
    name='Acceptance')


class RemoteKeywordsLibrary(RemoteLibrary):
    """Robot Framework remote keywords library
    """

    def portal_type_is_installed(self, portal_type):
        ids = self.portal_types.objectIds()
        titles = map(lambda x: x.title, self.portal_types.objectValues())
        assert portal_type in ids + titles, \
            u"'{0:s}' was not found in portal types.".format(portal_type)

    def change_ownership(self, path, user_id):
        from AccessControl.interfaces import IOwned
        obj = self.restrictedTraverse(path)

        acl_users = self.get('acl_users')
        user = None
        if acl_users:
            user = acl_users.getUser(user_id)
        if not user:
            root = self.getPhysicalRoot()
            acl_users = root.get('acl_users')
            if acl_users:
                user = acl_users.getUser(user_id)

        IOwned(obj).changeOwnership(user, recursive=1)

        if HAS_CSRF_PROTECTION:
            alsoProvides(self.REQUEST, IDisableCSRFProtection)

    def create_type_with_date_field(self, name):
        from plone.dexterity.fti import DexterityFTI
        fti = DexterityFTI(str(name), title=name)
        fti.behaviors = ('plone.app.dexterity.behaviors.metadata.IBasic',)
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


ROBOT_REMOTE_LIBRARY_FIXTURE = RemoteLibraryLayer(
    bases=(PLONE_FIXTURE,),
    libraries=(AutoLogin, QuickInstaller, RemoteKeywordsLibrary),
    name='CollectivePFGDexterity:RobotRemote')

ROBOT_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_PFG_DEXTERITY_FIXTURE,
           ROBOT_REMOTE_LIBRARY_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name='Robot')
