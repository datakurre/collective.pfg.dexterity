# -*- coding: utf-8 -*-
"""Dexterity content creation adapter for PloneFormGen"""

import logging

from zope.component import getUtility
from zope.schema import TextLine, List
from zope.schema.interfaces import IVocabularyFactory

from zope.interface import implements

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager

from AccessControl.User import UnrestrictedUser

from Products.Archetypes import atapi
from Products.Archetypes.Widget import SelectionWidget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.CMFCore.utils import getToolByName

from Products.PloneFormGen.interfaces import IPloneFormGenField
from Products.PloneFormGen.interfaces import IPloneFormGenActionAdapter
from Products.PloneFormGen.content.actionAdapter import FormAdapterSchema
from Products.PloneFormGen.content.actionAdapter import FormActionAdapter
from Products.PloneFormGen.config import FORM_ERROR_MARKER

from Products.DataGridField import DataGridField, DataGridWidget, SelectColumn

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import\
    ReferenceBrowserWidget

from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.schema import SCHEMA_CACHE
from plone.dexterity.utils import createContentInContainer

from plone.namedfile.interfaces import INamedFileField, INamedImageField
from plone.formwidget.namedfile.converter import NamedDataConverter

from jyu.pfg.dexterity.interfaces import IDexterityContentAdapter
from jyu.pfg.dexterity.config import PROJECTNAME

from zope.i18nmessageid import MessageFactory as ZopeMessageFactory
_ = ZopeMessageFactory("jyu.pfg.dexterity")

LOG = logging.getLogger("jyu.pfg.dexterity")
FILE_FIELDS = (INamedFileField, INamedImageField)


DexterityContentAdapterSchema = FormAdapterSchema.copy() + atapi.Schema((
    atapi.StringField(
        "createdType",
        required=True,
        storage=atapi.AnnotationStorage(),
        searchable=False,
        vocabulary="listTypes",
        widget=SelectionWidget(
            label=_(u"Content type"),
            description=_(u"Select the type of new content to be created.")
        ),
    ),
    atapi.ReferenceField(
        "targetFolder",
        required=True,
        storage=atapi.AnnotationStorage(),
        searchable=False,
        widget=ReferenceBrowserWidget(
            label=_(u"Target folder"),
            description=_((u"Select the target folder, where created new "
                           u"content should be placed. Please, make sure "
                           u"that the folder allows adding content of the "
                           u"selected type.")),
            base_query={"portal_type": "Folder"},
        ),
        relationship="targetFolder",
        allowed_types=("Folder",),
        multiValued=False,
    ),
    DataGridField(
        "fieldMapping",
        required=True,
        storage=atapi.AnnotationStorage(),
        searchable=False,
        allow_delete=True,
        allow_insert=True,
        allow_reorder=True,
        columns=("form", "content"),
        widget=DataGridWidget(
            label=_(u"Field mapping"),
            description=_((u"Map form fields to fields of the selected "
                           u"content type. Please note, that you must "
                           u"first select the content type, then save "
                           u"this adapter, and only then you'll be able "
                           u"to see the fields of the selected content "
                           u"type.")),
            columns={
                "form": SelectColumn(
                    _(u"Select a form field"),
                    vocabulary="listFormFields"),
                "content": SelectColumn(
                    _(u"to be mapped to a content field."),
                    vocabulary="listContentFields")
            },
        ),
    ),
    atapi.StringField(
        "workflowTransition",
        required=False,
        storage=atapi.AnnotationStorage(),
        searchable=False,
        vocabulary="listTransitions",
        widget=SelectionWidget(
            label=_(u"Trigger workflow transition"),
            description=_((u"You may select a workflow transition to be "
                           u"triggered after new content is created."))
        ),
    ),
    ### TODO: I've been thinking about enhancing this adapter to be able
    ### to 1) first create a container and 2) then add file types into that
    ### container. Although, this has been delayed, since I'm not yet
    ### convinced, if that's really a good idea.
    #
    # atapi.StringField(
    #     "containedType",
    #     required=False,
    #     storage=atapi.AnnotationStorage(),
    #     searchable=False,
    #     vocabulary="listNamedfileTypes",
    #     widget=SelectionWidget(
    #         label=_(u"Attachment Content type"),
    #         description=_((u"When the selected content type to be created "
    #                        u"is a container type and the form contains file "
    #                        u"fields, you may select a separate type for "
    #                        u"adding those files inside the container."))
    #     ),
    # ),
    # atapi.StringField(
    #     "containedWorkflowTransition",
    #     required=False,
    #     storage=atapi.AnnotationStorage(),
    #     searchable=False,
    #     vocabulary="listNamedfileTransitions",
    #     widget=SelectionWidget(
    #         label=_(u"Trigger attachment"s workflow transition"),
    #         description=_((u"You may select a workflow transition to be "
    #                        u"triggered after new file is added into the"
    #                        u"container. The selected transition will be "
    #                        u"triggered only after the selected transition "
    #                        u"for the container has been triggered."))
    #     ),
    # ),
))
finalizeATCTSchema(DexterityContentAdapterSchema)

DexterityContentAdapterSchema["title"].storage =\
    atapi.AnnotationStorage()
DexterityContentAdapterSchema["description"].storage =\
    atapi.AnnotationStorage()


def unrestricted(func):
    """Decorator for executing methods as unrestricted user"""
    def wrapper(self, *args, **kwargs):
        old_security_manager = getSecurityManager()
        newSecurityManager(
            None, UnrestrictedUser("manager", "", ["Manager"], []))
        try:
            return func(self, *args, **kwargs)
        except:
            pass
        finally:
            # Note that finally is also called before return
            setSecurityManager(old_security_manager)
        return func(self, *args, **kwargs)
    return wrapper


class DexterityContentAdapter(FormActionAdapter):
    """Dexterity content creation adapter for PloneFormGen"""
    implements(IPloneFormGenActionAdapter, IDexterityContentAdapter)

    portal_type = "Dexterity Content Adapter"
    schema = DexterityContentAdapterSchema

    _at_rename_after_creation = True

    title = atapi.ATFieldProperty("title")
    description = atapi.ATFieldProperty("description")

    createdType = atapi.ATFieldProperty("createdType")
    targetFolder = atapi.ATFieldProperty("targetFolder")
    fieldMapping = atapi.ATFieldProperty("fieldMapping")
    workflowTransition = atapi.ATFieldProperty("workflowTransition")

    @property
    def default_encoding(self):
        ptool = getToolByName(self, "portal_properties")
        try:
            return ptool.get("site_properties").default_charset
        except:
            return "utf-8"

    @unrestricted
    def onSuccess(self, fields, REQUEST=None):
        createdType = self.getCreatedType()
        targetFolder = self.getTargetFolder()
        fieldMapping = self.getFieldMapping()
        workflowTransition = self.getWorkflowTransition()

        try:
            # README: id for new content will be choosed by
            # INameChooser(container).chooseName(None, object),
            # so you should provide e.g. INameFromTitle adapter
            # to generate a custom id
            context = createContentInContainer(
                targetFolder, createdType, checkConstraints=True)
        except Exception, e:
            LOG.error(e)
            return {FORM_ERROR_MARKER: u"An unexpected error: %s" % e}

        for mapping in fieldMapping:
            field = self._getDexterityField(createdType, mapping["content"])
            field.bind(context)

            if True in [i.providedBy(field) for i in FILE_FIELDS]:
                # Here we use NamedFile"s data converter adapter...
                upload = REQUEST.get("%s_file" % mapping["form"], None)
                value = NamedDataConverter(field, None).toFieldValue(upload)
            else:
                value = REQUEST.get(mapping["form"], None)
                # Convert strings to unicode
                if isinstance(value, str):
                    value = unicode(value, self.default_encoding,
                                    errors="ignore")

            # Here we apply a few convenience heuristic
            if isinstance(field, TextLine):
                # 1) Multiple text lines into the same field
                try:
                    old_value = field.get(context)
                except AttributeError:
                    old_value = None
                if old_value and value:
                    value = u" ".join((old_value, value))
            if isinstance(field, List) and isinstance(value, unicode):
                # 2) Split keyword (just a guess) string into list
                value = value.replace(u",", u"\n")
                value = [s.strip() for s in value.split(u"\n") if s]

            try:
                field.set(context, value)
            except Exception, e:
                LOG.error(e)
                # Setting value falied, remove incomplete submission
                targetFolder.manage_delObjects([context.getId()])
                return {FORM_ERROR_MARKER: u"An unexpected error: %s" % e}

        # context.reindexObjectSecurity()
        context.reindexObject()

        wftool = getToolByName(self, "portal_workflow")
        try:
            wftool.doActionFor(context, workflowTransition)
        except Exception, e:
            # Transition failed, remove incomplete submission
            targetFolder.manage_delObjects([context.getId()])
            return {FORM_ERROR_MARKER: u"An unexpected error: %s" % e}

    def listTypes(self):
        types = getToolByName(self, "portal_types")
        dexterity = [(fti.id, fti.title) for fti in types.values()
                     if IDexterityFTI.providedBy(fti)]
        return atapi.DisplayList(dexterity)

    def listFormFields(self):
        fields = [(obj.getId(), obj.title_or_id())
                  for obj in self.aq_parent.objectValues()\
                          if IPloneFormGenField.providedBy(obj)]
        return atapi.DisplayList(fields)

    def _getDexterityField(self, portal_type, name):
        schemas = (SCHEMA_CACHE.get(portal_type),)\
            + SCHEMA_CACHE.subtypes(portal_type)
        for schema in schemas:
            if name in schema:
                return schema[name]
        return None

    def _getDexterityFields(self, portal_type):
        fields = {}
        schemas = (SCHEMA_CACHE.get(portal_type),)\
            + SCHEMA_CACHE.subtypes(portal_type)
        for schema in schemas:
            for name in schema:
                fields[name] = name.title()

        return [(key, fields[key]) for key in sorted(
            fields, lambda x, y: cmp(fields[x].lower(), fields[y].lower()))]

    def listContentFields(self):
        types = getToolByName(self, "portal_types")
        createdType = self.getCreatedType()
        if createdType in types.keys():
            fields = self._getDexterityFields(createdType)
        else:
            fields = []
        return atapi.DisplayList(fields)

    def listTransitions(self):
        types = getToolByName(self, "portal_types")
        createdType = self.getCreatedType()
        if createdType in types.keys():
            workflows = getToolByName(self, "portal_workflow")
            candidates = []
            transitions = []
            for workflow in [workflows.get(key) for key in\
                             workflows.getChainForPortalType("Submission")
                             if key in workflows.keys()]:
                candidates.extend(
                    workflow.states.get(workflow.initial_state).transitions)
            for transition in set(candidates):
                transitions.append((transition,
                    workflows.getTitleForTransitionOnType(
                        transition, createdType)))
        else:
            vocabulary = getUtility(IVocabularyFactory,
                name=u"plone.app.vocabularies.WorkflowTransitions")(self)
            transitions = [(term.value, term.title) for term in vocabulary]
        return atapi.DisplayList([(u"", _(u"No transition"))]\
            + sorted(transitions,
                     lambda x, y: cmp(x[1].lower(), y[1].lower())))

atapi.registerType(DexterityContentAdapter, PROJECTNAME)

unrestricted = None  # hide our unholy decorator
