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

        # portal.invokeFactory("Folder", "feedback", title=u"Feedback")

        # from plone.dexterity.fti import DexterityFTI
        # fti = DexterityFTI("Feedback")
        # fti.behaviors = ("plone.app.dexterity.behaviors.metadata.IBasic")
        # portal.portal_types._setObject("Feedback", fti)

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

    def redo(self, name):
        index = [s.name for s in self.scenarios].index(name)
        scenario = self.scenarios[index]
        for clause in scenario.givens + scenario.whens + scenario.thens:
            clause(self)

    def setUp(self):
        self.browser = z2.Browser(self.layer["app"])

    @property
    def portal(self):
        return self.layer["portal"]

    @property
    def portal_url(self):
        return self.portal.absolute_url()

    @scenario("'Content adapter' is available")
    class Content_adapter_is_available(Scenario):

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

        @then("I 'Content Adapter' becomes available to be added")
        def I_Content_Adapter_becomes_available_to_be_added(self):
            try:
                self.browser.getLink("Content Adapter")
            except:
                self.assertTrue(
                    False, u"'Content Adapter' was not available to be added.")

    @scenario("Content adapter can be added and configured")
    class Content_adapter_can_be_added_and_configured(Scenario):

        @given("'Content adapter' is available to be added")
        def Content_adapter_is_available_to_be_added(self):
            self.story.redo("'Content adapter' is available")
            try:
                self.browser.getLink("Content Adapter")
            except:
                self.assertTrue(
                    False, u"'Content Adapter' was not available to be added.")

        @given("There exists a Dexterity type named 'Ticket'")
        def There_exists_a_Dexterity_type_named_Ticket(self):
            pass

        @given("It has at least fields 'Title' and 'Description'")
        def It_has_at_least_fields_Title_and_Description(self):
            pass

        @given("There exists a 'Folder' named 'Tracker'")
        def There_exists_a_Folder_named_Tracker(self):
            pass

        @when("I add a 'Content Adapter'")
        def I_add_a_Content_Adapter(self):
            self.browser.getLink("Content Adapter").click()
            self.browser.getControl("Title").value = u"Content Adapter"
            # ...
            # we cannot complete adding adapter without a dexterity
            # type and target folder

        @when("I configure it to create 'Tickets' under 'Tracker'")
        def I_configure_it_to_create_Tickets_under_Tracker(self):
            pass

        @then("I can create content using the form")
        def I_can_create_content_using_the_form(self):
            self.assertTrue(False, "This test needs to be finished.")
