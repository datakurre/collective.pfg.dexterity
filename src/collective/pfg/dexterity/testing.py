# -*- coding: utf-8 -*-
"""Testing layers and keywords"""

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import (
    IntegrationTesting,
    FunctionalTesting
)

from plone.testing import z2


class Layer(PloneSandboxLayer):
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

FIXTURE = Layer()


INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="Functional")
ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(FIXTURE, z2.ZSERVER_FIXTURE), name="Acceptance")


class Keywords(object):
    """Robot Framework keyword library"""

    def product_is_installed(self, name):
        from plone import api
        portal = api.portal.get()
        portal._p_jar.sync()

        ids = portal.portal_types.objectIds()
        titles = map(lambda x: x.title, portal.portal_types.objectValues())

        assert name in ids + titles,\
            u"'%s' was not found in portal types." % name

        import transaction
        transaction.commit()

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

        from plone import api
        portal = api.portal.get()
        portal._p_jar.sync()

        portal.portal_types._setObject(str(name), fti)

        import transaction
        transaction.commit()
