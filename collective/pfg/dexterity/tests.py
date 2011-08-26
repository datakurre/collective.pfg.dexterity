# -*- coding: utf-8 -*-
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting, FunctionalTesting

from plone.testing import z2


class MyFixture(PloneSandboxLayer):
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
        self.applyProfile(portal, "plone.app.dexterity:default")
        self.applyProfile(portal, "Products.PloneFormGen:default")
        self.applyProfile(portal, "Products.DataGridField:default")
        self.applyProfile(portal, "collective.pfg.dexterity:default")

    def tearDownZope(self, app):
        z2.uninstallProduct(app, "collective.pfg.dexterity")
        z2.uninstallProduct(app, "Products.DataGridField")
        z2.uninstallProduct(app, "Products.PloneFormGen")

MY_FIXTURE = MyFixture()

MY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(MY_FIXTURE,), name="MyFixture:Integration")
MY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(MY_FIXTURE,), name="MyFixture:Functional")


import unittest2 as unittest
from corejet.core import Scenario, story, scenario, given, when, then

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles

import transaction


@story(id="17475767", title="I want to create dexterity content with PFG-form")
class I_want_to_create_dexterity_content_with_PFGform(unittest.TestCase):

    layer = MY_FUNCTIONAL_TESTING

    def setUp(self):
        self.browser = z2.Browser(self.layer["app"])

    @property
    def portal(self):
        return self.layer["portal"]

    @property
    def portal_url(self):
        return self.portal.absolute_url()

    @scenario("Adapter can be added")
    class Adapter_can_be_added(Scenario):

        @given("I've got 'Manager' role")
        def Ive_got_Manager_role(self):
            portal = self.layer["portal"]
            setRoles(portal, TEST_USER_ID, ["Manager"])
            transaction.commit()

            self.assertTrue("Manager" in
                self.portal.portal_membership.getMemberById(
                    TEST_USER_ID).getRoles(),
                u"I Don't have 'Manager' role.")

        @given("I'm logged in")
        def Im_logged_in(self):
            self.browser.open(self.portal_url + "/login_form")
            self.browser.getControl("Login Name").value = TEST_USER_NAME
            self.browser.getControl("Password").value = TEST_USER_PASSWORD
            self.browser.getControl("Log in").click()

            self.assertFalse(
                self.portal.portal_membership.isAnonymousUser(),
                u"I'm not logged in.")

        @given("I'm on Plone root folder")
        def Im_on_Plone_root_folder(self):
            self.browser.open(self.portal_url)

        @given("'Form Folder' is available to be added")
        def Form_Folder_is_available_to_be_added(self):
            try:
                self.browser.getLink("Form Folder")
            except:
                self.assertTrue(
                    False, u"'Form Folder' was not available to be added.")

        @when("I add a 'Form Folder' named 'Feedback'")
        def I_add_a_Form_Folder_named_Feedback(self):
            self.browser.open(self.portal_url)
            self.browser.getLink("Form Folder").click()
            self.browser.getControl("Title").value = u"Feedback"
            self.browser.getControl("Save").click()

        @when("I move into that folder")
        def I_move_into_that_folder(self):
            self.browser.open(self.portal_url + "/feedback")

        @then("I can add a 'Dexterity Content Adapter'")
        def I_can_add_a_Dexterity_Content_Adapter(self):
            try:
                self.browser.getLink("Content Adapter")
            except:
                self.assertTrue(
                    False, u"'Content Adapter' was not available to be added.")
