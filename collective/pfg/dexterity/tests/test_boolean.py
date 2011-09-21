# -*- coding: utf-8 -*-
"""CoreJet tests"""
import unittest2 as unittest
from corejet.core import Scenario, story, scenario, given, when, then

from plone.testing import z2

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from collective.pfg.dexterity.testing import FUNCTIONAL_TESTING


@story(id="18094419", title=(u"As a 'Site Administrator' I want to save "
                             u"submissions with boolean values"))
class Story(unittest.TestCase):

    layer = FUNCTIONAL_TESTING

    @property
    def portal(self):
        return self.layer["portal"]

    @given(u"'Form Folder' is installed")
    def givenA(self):
        self.assertIn("FormFolder", self.portal.portal_types.objectIds(),
            u"'FormFolder' was not found in portal types.")

    @given(u"'Content Adapter' is installed")
    def givenB(self):
        self.assertIn("Dexterity Content Adapter",
                      self.portal.portal_types.objectIds(),
                      (u"'Dexterity Content Adapter' was not found on in "
                       u"portal types."))

    @scenario("Boolean field is supported")
    class Scenario(Scenario):

        @given("There's a content type with a boolean field")
        def givenA(self):
            from plone.dexterity.fti import DexterityFTI
            fti = DexterityFTI("Ticket")
            fti.behaviors = ("plone.app.dexterity.behaviors.metadata.IBasic",)
            fti.model_source = u"""\
<model xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="important" type="zope.schema.Bool">
      <description />
      <required>False</required>
      <title>This is important</title>
    </field>
  </schema>
</model>"""
            self.portal.portal_types._setObject("Ticket", fti)

        @given("There's a published form with a boolean field")
        def givenB(self):
            setRoles(self.portal, TEST_USER_ID, ["Manager"])
            self.portal.invokeFactory(
                "FormFolder", "feedback", title=u"Send Feedback")
            del self.portal.feedback["replyto"]
            self.portal.feedback.invokeFactory(
                "FormBooleanField", "important", title=u"This is important")
            self.portal.portal_workflow.doActionFor(
                self.portal.feedback, "publish")

        @given("The form has properly configured 'Content Adapter'")
        def givenC(self):
            self.portal.invokeFactory(
                "Folder", "tracker", title=u"Tracker")
            self.portal.feedback.invokeFactory(
                "Dexterity Content Adapter", "factory",
                title=u"Ticket machine")
            self.portal.feedback.factory.createdType = "Ticket"
            self.portal.feedback.factory.setTargetFolder(
                self.portal.tracker.UID())
            self.portal.feedback.factory.setFieldMapping((
                {"content": "title", "form": "topic"},
                {"content": "description", "form": "comments"},
                {"content": "important", "form": "important"}
            ))
            self.portal.feedback.factory.setWorkflowTransition("submit")
            self.portal.feedback.setActionAdapter(("factory",))

        @when("I submit the form as an 'Anonymous User'")
        def when(self):
            import transaction
            transaction.commit()

            browser = z2.Browser(self.layer["app"])
            browser.open(self.portal.absolute_url() + "/feedback")
            self.assertIn("Log in", browser.contents,
                (u"I couldn't support form as 'Anonymous User', "
                 u"because I was already logged in."))

            browser.getControl("Subject").value = u"Sample ticket"
            browser.getControl("Comments").value = u"This is a test"
            browser.getControl("This is important").click()
            browser.getControl("Submit").click()

        @then("A content object is created")
        def thenA(self):
            self.assertIn("ticket", self.portal["tracker"],
                u"Ticket was not created by submitting the form.")
            self.assertEqual(self.portal["tracker"]["ticket"].title,
                u"Sample ticket", u"Created ticket had wrong title.")
            self.assertEqual(self.portal["tracker"]["ticket"].description,
                u"This is a test",
                u"Created ticket had wrong description.")

        @then("It has boolean field filled")
        def thenB(self):
            self.assertTrue(self.portal["tracker"]["ticket"].important,
                u"The boolean field was not filled.")
