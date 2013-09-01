# -*- coding: utf-8 -*-
from plone.app.robotframework import (
    RemoteLibraryLayer,
    AutoLogin,
    QuickInstaller
)
from plone.app.testing import (
    FunctionalTesting,
    IntegrationTesting,
    PLONE_FIXTURE,
    PloneSandboxLayer,
)
from plone.testing import z2
from collective.pfg.dexterity.testing_robot import RemoteKeywordsLibrary


class CollectivePFGDexterityLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.pfg.dexterity
        self.loadZCML(package=collective.pfg.dexterity)
        z2.installProduct(app, "Products.PloneFormGen")
        z2.installProduct(app, "Products.DataGridField")
        z2.installProduct(app, "collective.pfg.dexterity")

    def setUpPloneSite(self, portal):
        # PLONE_FIXTURE has no default workflow chain set
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")

        self.applyProfile(portal, "plone.app.dexterity:default")
        self.applyProfile(portal, "Products.PloneFormGen:default")
        self.applyProfile(portal, "Products.DataGridField:default")
        self.applyProfile(portal, "collective.pfg.dexterity:default")

    def tearDownZope(self, app):
        z2.uninstallProduct(app, "collective.pfg.dexterity")
        z2.uninstallProduct(app, "Products.DataGridField")
        z2.uninstallProduct(app, "Products.PloneFormGen")

    def testSetUp(self):
        # XXX: How should we invalidate Dexterity fti.lookupSchema() cache?
        import plone.dexterity.schema
        for name in dir(plone.dexterity.schema.generated):
            if name.startswith("plone"):
                delattr(plone.dexterity.schema.generated, name)
        plone.dexterity.schema.SCHEMA_CACHE.clear()


COLLECTIVE_PFG_DEXTERITY_FIXTURE = CollectivePFGDexterityLayer()


COLLECTIVE_PFG_DEXTERITY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_PFG_DEXTERITY_FIXTURE,),
    name="Integration")
COLLECTIVE_PFG_DEXTERITY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_PFG_DEXTERITY_FIXTURE,),
    name="Functional")
COLLECTIVE_PFG_DEXTERITY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_PFG_DEXTERITY_FIXTURE, z2.ZSERVER_FIXTURE),
    name="Acceptance")

ROBOT_REMOTE_LIBRARY_FIXTURE = RemoteLibraryLayer(
    bases=(PLONE_FIXTURE,),
    libraries=(AutoLogin, QuickInstaller, RemoteKeywordsLibrary),
    name="CollectivePFGDexterity:RobotRemote")

ROBOT_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_PFG_DEXTERITY_FIXTURE,
           ROBOT_REMOTE_LIBRARY_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="Robot")
