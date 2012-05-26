# -*- coding: utf-8 -*-
"""CoreJet tests"""
import unittest2 as unittest
from corejet.core import Scenario, story, scenario, given, when, then

from plone.testing import z2

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles

from collective.pfg.dexterity.testing import FUNCTIONAL_TESTING

import transaction


@story(id="17475767", title=("As Site Administrator I want to create "
                             "feedback form that saves submissions as "
                             "tickets"))
class I_want_to_create_feedback_form(unittest.TestCase):

    layer = FUNCTIONAL_TESTING

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

    @scenario("I can get logged in")
    class I_can_get_logged_in(Scenario):

        @given("I'm logged out")
        def Im_logged_out(self):
            self.browser.open(self.portal_url)
            try:
                self.browser.getLink("Log out").click()
            except:
                pass

        @given("I'm on the login form")
        def Im_on_the_login_form(self):
            self.browser.open(self.portal_url + "/login_form")

        @when("I enter my username and password")
        def I_enter_my_username_and_password(self):
            self.browser.getControl("Login Name").value = TEST_USER_NAME
            self.browser.getControl("Password").value = TEST_USER_PASSWORD
            self.browser.getControl("Log in").click()

        @then("I get logged in")
        def I_get_logged_in(self):
            self.assertFalse(
                self.portal.portal_membership.isAnonymousUser(),
                u"I'm not logged in.")

    @scenario("'Folder' is available to be added")
    class Folder_is_available_to_be_added(Scenario):

        @given("I'm logged in as 'Site Administrator'")
        def Im_logged_in_as_Site_Administrator(self):
            setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])
            transaction.commit()
            self.redo("I can get logged in")

        @when("I open the front page")
        def I_open_the_front_page(self):
            self.browser.open(self.portal.absolute_url())

        @then("I see, I could add a new 'Folder'")
        def I_see_I_could_add_a_new_Folder(self):
            try:
                self.browser.getLink("Folder")
            except:
                self.assertTrue(
                    False, u"'Folder' was not available to be added.")

    @scenario("'Ticket' is available to be added")
    class Ticket_is_available_to_be_added(Scenario):

        @given("I'm logged in as 'Site Administrator'")
        def Im_logged_in_as_Site_Administrator(self):
            setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])
            transaction.commit()
            self.redo("I can get logged in")

        @given("There exists a content type named 'Ticket'")
        def There_exists_a_content_type_named_Ticket(self):
            from plone.dexterity.fti import DexterityFTI
            fti = DexterityFTI("Ticket")
            self.portal.portal_types._setObject("Ticket", fti)
            transaction.commit()

        @given("It has fields 'Title' and 'Description'")
        def It_has_fields_Title_and_Description(self):
            fti = self.portal.portal_types.get("Ticket")
            fti.behaviors = ("plone.app.dexterity.behaviors.metadata.IBasic",)
            transaction.commit()

        @when("I open the front page")
        def I_open_the_front_page(self):
            self.browser.open(self.portal.absolute_url())

        @then("I see, I could add a new 'Ticket'")
        def I_see_I_could_add_a_new_Ticket(self):
            try:
                self.browser.getLink("Ticket")
            except:
                self.assertTrue(
                    False, u"'Ticket' was not available to be added.")

    @scenario("'Form Folder' is available to be added")
    class Form_Folder_is_available_to_be_added(Scenario):

        @given("I'm logged in as 'Site Administrator'")
        def Im_logged_in_as_Site_Administrator(self):
            # XXX: Form Folder didn't support Site Administrator out-of-box.
            setRoles(self.portal, TEST_USER_ID,
                     ["Site Administrator", "Manager"])
            transaction.commit()
            self.redo("I can get logged in")

        @when("I open the front page")
        def I_open_the_front_page(self):
            self.browser.open(self.portal.absolute_url())

        @then("I see, I could add a new 'Form Folder'")
        def I_see_I_could_add_a_new_Form_Folder(self):
            try:
                self.browser.getLink("Form Folder")
            except:
                self.assertTrue(
                    False, u"'Form Folder' was not available to be added.")

    @scenario("'Content Adapter' is available to be added")
    class Content_Adapter_is_available_to_be_added(Scenario):

        @given("I'm logged in as 'Site Administrator'")
        def Im_logged_in_as_Site_Administrator(self):
            # XXX: Form Folder didn't support Site Administrator out-of-box.
            setRoles(self.portal, TEST_USER_ID,
                     ["Site Administrator", "Manager"])
            transaction.commit()
            self.redo("I can get logged in")

        @given("'Form Folder' is available to be added")
        def Form_Folder_is_available_to_be_added(self):
            self.redo("'Form Folder' is available to be added")

        @when("I open the front page")
        def I_open_the_front_page(self):
            self.browser.open(self.portal.absolute_url())

        @when("I add a new 'Form Folder' named 'Feedback'")
        def I_add_a_new_Form_Folder_named_Feedback(self):
            self.browser.getLink("Form Folder").click()
            self.browser.getControl("Title").value = u"Feedback"
            self.browser.getControl("Save").click()

        @when("I open it")
        def I_open_it(self):
            self.browser.open(self.portal_url + "/feedback")

        @then("I see, I could add a new 'Content Adapter'")
        def I_see_I_could_add_a_new_Content_Adapter(self):
            try:
                self.browser.getLink("Content Adapter")
            except:
                self.assertTrue(
                    False, u"'Content Adapter' was not available to be added.")

    @scenario("Feedback form can be created")
    class Feedback_form_can_be_created(Scenario):

        @given("I'm logged in as 'Site Administrator'")
        def Im_logged_in_as_Site_Administrator(self):
            # XXX: Form Folder didn't support Site Administrator out-of-box.
            setRoles(self.portal, TEST_USER_ID,
                     ["Site Administrator", "Manager"])
            transaction.commit()
            self.redo("I can get logged in")

        @given("'Ticket' is available to be added")
        def Ticket_is_available_to_be_added(self):
            self.redo("'Ticket' is available to be added")
            # XXX: Form Folder didn't support Site Administrator out-of-box.
            setRoles(self.portal, TEST_USER_ID,
                     ["Site Administrator", "Manager"])
            transaction.commit()

        @given("I've created a new 'Folder' named 'Tracker'")
        def Ive_created_a_new_Folder_named_Tracker(self):
            self.portal.invokeFactory(
                "Folder", "tracker", title=u"Tracker")
            transaction.commit()

        @when("I open the front page")
        def I_open_the_front_page(self):
            self.browser.open(self.portal.absolute_url())

        @when("I add a 'Form Folder' named 'Feedback'")
        def I_add_a_Form_Folder_named_Feedback(self):
            self.browser.getLink("Form Folder").click()
            self.browser.getControl("Title").value = u"Feedback"
            self.browser.getControl("Save").click()

            # XXX: We assume here that Form Folder creates its default form
            # with topic, comments and replyto -fields. Also, because the
            # default form includes Mailer-adapter, we must delete it.
            self.browser.open(self.portal.absolute_url()
                              + "/feedback/folder_contents")
            self.browser.getControl(name="paths:list").value =\
                ["/plone/feedback/mailer"]
            self.browser.getControl("Delete").click()
            self.browser.getLink("Edit").click()
            self.browser.getControl("Save").click()

        @when("I add a 'Content Adapter' named 'Ticket machine'")
        def I_add_a_Content_Adapter_named_Ticket_machine(self):
            self.browser.getLink("Content Adapter").click()
            self.browser.getControl("Title").value = u"Ticket machine"

        @when("I set it to create 'Ticket' from each submission")
        def I_set_it_to_create_Ticket_from_each_submission(self):
            self.browser.getControl(name="createdType").value = (u"Ticket",)

        @when("I set it to use 'Tracker' as its target folder")
        def I_set_it_to_use_Tracker_as_its_target_folder(self):
            results = self.portal.portal_catalog(Title=u"Tracker")
            uuid = results[0].UID
            self.browser.getControl(name="targetFolder").value = uuid

        @when("I set field 'Subject' to be saved to 'Title' on 'Ticket'")
        def I_set_field_Subject_to_be_saved_to_Title_on_Ticket(self):
            # We need to "Save" form once to update field mapping options
            self.browser.getControl(name="form.button.save").click()
            self.browser.getLink("Edit").click()
            # Now we can add the first mapping
            self.browser.getControl(name="fieldMapping.form:records",
                                    index=0).value = ["topic"]
            self.browser.getControl(name="fieldMapping.content:records",
                                    index=0).value = ["title"]
            self.browser.getControl(name="fieldMapping.orderindex_:records",
                                    index=0).value = "1"

        @when("I set field 'Comment' to be saved to 'Description' on 'Ticket'")
        def I_set_field_Comment_to_be_saved_to_Description_on_Ticket(self):
            # We need to "Save" form once to be able to add a new mapping
            self.browser.getControl(name="form.button.save").click()
            self.browser.getLink("Edit").click()
            # Now we can continue to add the second mapping
            self.browser.getControl(name="fieldMapping.form:records",
                                    index=1).value = ["comments"]
            self.browser.getControl(name="fieldMapping.content:records",
                                    index=1).value = ["description"]
            self.browser.getControl(name="fieldMapping.orderindex_:records",
                                    index=1).value = "2"

        @when("I save the adapter")
        def I_save_the_adapter(self):
            self.browser.getControl(name="form.button.save").click()

        @then("I can create a new 'Ticket' by submitting the form")
        def I_can_create_a_new_Ticket_by_submitting_the_form(self):
            self.browser.open(self.portal.absolute_url() + "/feedback")
            self.browser.getControl("Your E-Mail Address").value =\
                u"nobody@example.com"
            self.browser.getControl("Subject").value =\
                u"Sample ticket"
            self.browser.getControl("Comments").value =\
                u"This is a test"
            self.browser.getControl("Submit").click()

            self.assertTrue("ticket" in self.portal["tracker"],
                u"Ticket was not created by submitting the form.")
            self.assertTrue(self.portal["tracker"]["ticket"].title ==\
                u"Sample ticket", u"Created ticket had wrong title.")
            self.assertTrue(self.portal["tracker"]["ticket"].description ==\
                u"This is a test",
                u"Created ticket had wrong description.")

    @scenario("Feedback get saved as ticket")
    class Feedback_get_saved_as_ticket(Scenario):

        @given("I've created a feedback form")
        def Ive_created_a_feedback_form(self):
            self.redo("Feedback form can be created")

        @given("It's been published")
        def Its_been_published(self):
            wftool = self.portal.portal_workflow
            form = self.portal["feedback"]
            wftool.doActionFor(form, "publish")
            transaction.commit()

        @when("I log out")
        def I_log_out(self):
            self.browser.getLink("Log out").click()

        @when("Submit the form as a visitor")
        def Submit_the_form_as_a_visitor(self):
            self.browser.open(self.portal.absolute_url() + "/feedback")
            self.browser.getControl("Your E-Mail Address").value =\
                u"customer@example.com"
            self.browser.getControl("Subject").value =\
                u"Customer feedback"
            self.browser.getControl("Comments").value =\
                u"Please, contact us soon."
            self.browser.getControl("Submit").click()

        @then("A ticket is created")
        def A_ticket_is_created(self):
            self.assertTrue("ticket-1" in self.portal["tracker"],
                u"Ticket was not created by submitting the form.")
            self.assertTrue(self.portal["tracker"]["ticket-1"].title ==\
                u"Customer feedback", u"Created ticket had wrong title.")
            self.assertTrue(self.portal["tracker"]["ticket-1"].description ==\
                u"Please, contact us soon.",
                u"Created ticket had wrong description.")
