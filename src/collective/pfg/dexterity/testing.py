# -*- coding: utf-8 -*-
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting, FunctionalTesting

from plone.testing import z2


class Fixture(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)

        import Products.PloneFormGen
        self.loadZCML(package=Products.PloneFormGen)
        z2.installProduct(app, "Products.PloneFormGen")

        import Products.DataGridField
        self.loadZCML(package=Products.DataGridField)
        z2.installProduct(app, "Products.DataGridField")

        import collective.pfg.dexterity
        self.loadZCML(package=collective.pfg.dexterity)
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

FIXTURE = Fixture()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="Fixture:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="Fixture:Functional")
