# -*- coding: utf-8 -*-
import unittest2 as unittest
from corejet.core import Scenario, story, scenario, given, when, then

from plone.testing import z2

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from collective.pfg.dexterity.testing import (
    COLLECTIVE_PFG_DEXTERITY_FUNCTIONAL_TESTING
)


@story(id="36107035", title=(u"As a 'Site Administrator' I want to save "
                             u"submissions with date values"))
class Story(unittest.TestCase):

    layer = COLLECTIVE_PFG_DEXTERITY_FUNCTIONAL_TESTING

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

    @scenario(u"Date field is supported")
    class Scenario(Scenario):

        @given(u"There's a content type with a date field")
        def givenA(self):
            from plone.dexterity.fti import DexterityFTI
            fti = DexterityFTI("Ticket")
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
            self.portal.portal_types._setObject("Ticket", fti)

        @given(u"There's a published form with a date field")
        def givenB(self):
            setRoles(self.portal, TEST_USER_ID, ["Manager"])
            self.portal.invokeFactory(
                "FormFolder", "send-request", title=u"Send Request")
            del self.portal["send-request"]["replyto"]
            self.portal["send-request"].invokeFactory(
                "FormDateField", "due-date", title=u"Due Date")
            self.portal.portal_workflow.doActionFor(
                self.portal["send-request"], "publish")

        @given(u"The form has properly configured 'Content Adapter'")
        def givenC(self):
            self.portal.invokeFactory(
                "Folder", "tracker", title=u"Tracker")
            self.portal["send-request"].invokeFactory(
                "Dexterity Content Adapter", "factory",
                title=u"Ticket machine")
            self.portal["send-request"].factory.createdType = "Ticket"
            self.portal["send-request"].factory.setTargetFolder(
                self.portal.tracker.UID())
            self.portal["send-request"].factory.setFieldMapping((
                {"content": "title", "form": "topic"},
                {"content": "description", "form": "comments"},
                {"content": "duedate", "form": "due-date"}
            ))
            self.portal["send-request"].factory.setWorkflowTransition("submit")
            self.portal["send-request"].setActionAdapter(("factory",))

        @when(u"I submit the form as an 'Anonymous User'")
        def when(self):
            import transaction
            transaction.commit()

            browser = z2.Browser(self.layer["app"])
            browser.open(self.portal.absolute_url() + "/send-request")
            self.assertIn("Log in", browser.contents,
                          (u"I couldn't submit form as 'Anonymous User', "
                           u"because I was already logged in."))

            browser.getControl("Subject").value = u"Sample ticket"
            browser.getControl("Comments").value = u"This is a test"
            browser.getControl(name="due-date_year").value = ("2013",)
            browser.getControl(name="due-date_month").value = ("01",)
            browser.getControl(name="due-date_day").value = ("01",)
            browser.getControl("Submit").click()

            self.assertIn("Thanks for your input.", browser.contents,
                          ("No 'Thanks for your input.' found "
                           "after submitting the form."))

        @then(u"A content object is created")
        def thenA(self):
            self.portal._p_jar.sync()
            self.assertIn("ticket", self.portal["tracker"],
                          u"Ticket was not created by submitting the form.")
            self.assertEqual(self.portal["tracker"]["ticket"].title,
                             u"Sample ticket",
                             u"Created ticket had wrong title.")
            self.assertEqual(self.portal["tracker"]["ticket"].description,
                             u"This is a test",
                             u"Created ticket had wrong description.")

        @then(u"it has the date field filled")
        def thenB(self):
            self.assertEqual(str(self.portal["tracker"]["ticket"].duedate),
                             "2013-01-01",
                             u"The date field was not filled.")
