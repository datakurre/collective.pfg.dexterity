# -*- coding: utf-8 -*-
from plone.app.testing import (
    FunctionalTesting,
    IntegrationTesting,
    PLONE_FIXTURE,
    PloneSandboxLayer,
)
from plone.testing import z2


class Layer(PloneSandboxLayer):
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


FIXTURE = Layer()


INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="Functional")
ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(FIXTURE, z2.ZSERVER_FIXTURE), name="Acceptance")


class RobotLayer(PloneSandboxLayer):
    defaultBases = (FIXTURE,)

    def setUpPloneSite(self, portal):
        # Inject keyword for getting the selenium session id
        import Selenium2Library
        Selenium2Library.keywords._browsermanagement.\
            _BrowserManagementKeywords.get_session_id = lambda self:\
            self._cache.current.session_id
        # Inject remote keywords library into site
        from collective.pfg.dexterity import testing_robot
        portal._setObject("RemoteKeywordsLibrary",
                          testing_robot.RemoteKeywordsLibrary())

    def tearDownPloneSite(self, portal):
        portal._delObject("RemoteKeywordsLibrary")

ROBOT_FIXTURE = RobotLayer()


ROBOT_TESTING = FunctionalTesting(
    bases=(ROBOT_FIXTURE, z2.ZSERVER_FIXTURE), name="Robot")
