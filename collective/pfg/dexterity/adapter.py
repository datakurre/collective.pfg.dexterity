# -*- coding: utf-8 -*-
"""Dexterity content creation adapter for PloneFormGen"""

import logging

import re
from time import time

from ZODB.POSException import ConflictError

from zope.component import getMultiAdapter, getUtility, queryUtility
from zope.schema import TextLine, List, Datetime
from zope.schema.interfaces import IVocabularyFactory

from zope.interface import implements, alsoProvides

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager

from AccessControl.User import UnrestrictedUser

from Products.Archetypes import atapi
from Products.Archetypes.Widget import SelectionWidget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent

from Products.PloneFormGen.interfaces import IPloneFormGenField
from Products.PloneFormGen.interfaces import IPloneFormGenActionAdapter
from Products.PloneFormGen.content.actionAdapter import FormAdapterSchema
from Products.PloneFormGen.content.actionAdapter import FormActionAdapter
from Products.PloneFormGen.config import FORM_ERROR_MARKER

from Products.DataGridField import DataGridField, DataGridWidget, SelectColumn

from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget

from z3c.form.interfaces import\
    IFormLayer, IFieldWidget, IDataConverter, IDataManager

from plone.memoize import ram
from plone.behavior.interfaces import IBehavior

from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer

from collective.pfg.dexterity.interfaces import IDexterityContentAdapter
from collective.pfg.dexterity.config import PROJECTNAME

from zope.i18nmessageid import MessageFactory as ZopeMessageFactory
_ = ZopeMessageFactory("collective.pfg.dexterity")

LOG = logging.getLogger("collective.pfg.dexterity")


DexterityContentAdapterSchema = FormAdapterSchema.copy() + atapi.Schema((
    atapi.StringField(
        "createdType",
        required=True,
        write_permission=ModifyPortalContent,
        read_permission=ModifyPortalContent,
        storage=atapi.AnnotationStorage(),
        searchable=False,
        vocabulary="listTypes",
        widget=SelectionWidget(
            label=_(u"Content type"),
            description=_(u"Select the type of new content to be created.")
        )
    ),
    atapi.ReferenceField(
        "targetFolder",
        required=True,
        write_permission=ModifyPortalContent,
        read_permission=ModifyPortalContent,
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
        multiValued=False
    ),
    DataGridField(
        "fieldMapping",
        required=True,
        write_permission=ModifyPortalContent,
        read_permission=ModifyPortalContent,
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
        )
    ),
    atapi.StringField(
        "workflowTransition",
        required=False,
        write_permission=ModifyPortalContent,
        read_permission=ModifyPortalContent,
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
    #     write_permission=ModifyPortalContent,
    #     read_permission=ModifyPortalContent,
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
    """Decorator for executing actions as unrestricted user"""
    def wrapper(self, *args, **kwargs):
        old_security_manager = getSecurityManager()
        newSecurityManager(
            None, UnrestrictedUser("manager", "", ["Manager"], []))
        try:
            return func(self, *args, **kwargs)
        except ConflictError:
            raise
        finally:
            # Note that finally is also called before return
            setSecurityManager(old_security_manager)
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
        except ConflictError:
            raise
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
        except ConflictError:
            raise
        except Exception, e:
            LOG.error(e)
            return {FORM_ERROR_MARKER: u"An unexpected error: %s" % e}

        alsoProvides(REQUEST, IFormLayer)  # let us to find z3c.form adapters
        for mapping in fieldMapping:
            field = self._getDexterityField(createdType, mapping["content"])

            if "%s_file" % mapping["form"] in REQUEST:
                value = REQUEST.get("%s_file" % mapping["form"])
            else:
                value = REQUEST.get(mapping["form"], None)
                # Convert strings to unicode
                if isinstance(value, str):
                    value = unicode(value, self.default_encoding,
                                    errors="ignore")

            # Convert datetimes to collective.z3cform.datetime-compatible
            if isinstance(field, Datetime):
                value = re.compile("\d+").findall(value)

            # XXX: Here we apply a few controversial convenience heuristics
            if isinstance(field, TextLine):
                # 1) Multiple text lines into the same field
                try:
                    old_value = field.get(context)
                except AttributeError:
                    old_value = None
                if old_value and value:
                    value = u" ".join((old_value, value))
            elif isinstance(field, List) and isinstance(value, unicode):
                # 2) Split keyword (just a guess) string into list
                value = value.replace(u",", u"\n")
                value = [s.strip() for s in value.split(u"\n") if s]

            # Try to set the value on creted object
            try:
                # 1) Try to set it directly
                bound_field = field.bind(context)
                bound_field.validate(value)
                bound_field.set(context, value)
            except ConflictError:
                raise
            except Exception, e:
                try:
                    # 2) Try your luck with z3c.form adapters
                    widget = getMultiAdapter((field, REQUEST), IFieldWidget)
                    converter = IDataConverter(widget)
                    dm = getMultiAdapter((context, field), IDataManager)
                    dm.set(converter.toFieldValue(value))
                except ConflictError:
                    raise
                except Exception:
                    LOG.error(e)
                    # Setting value failed, remove incomplete submission
                    targetFolder.manage_delObjects([context.getId()])
                    return {FORM_ERROR_MARKER: u"An unexpected error: %s" % e}

        if workflowTransition:
            wftool = getToolByName(self, "portal_workflow")
            try:
                wftool.doActionFor(context, workflowTransition)
            except ConflictError:
                raise
            except Exception, e:
                # Transition failed, remove incomplete submission
                targetFolder.manage_delObjects([context.getId()])
                return {FORM_ERROR_MARKER: u"An unexpected error: %s" % e}

        context.reindexObject()

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

    @ram.cache(lambda method, self, portal_type: time() // 60)
    def _getDexteritySchemas(self, portal_type):
        fti = getUtility(IDexterityFTI, name=portal_type)
        schemas = [fti.lookupSchema()]
        # Schemas provided by behaviors can only be looked up by looping
        # through behaviors or asking SCHEMA_CACHE for subtypes...
        for behavior_name in fti.behaviors:
            behavior = queryUtility(IBehavior, name=behavior_name)
            if behavior is not None:
                if behavior.marker is not None:
                    schemas.append(behavior.marker)
                elif behavior_name.startswith(
                    "plone.app.dexterity.behaviors.metadata"):
                    # ...except, for some good reason the default metadata
                    # -behaviors don't have marker interface and therefore
                    # won't appear when querying schemas using
                    # SCHEMA_CACHE.subtypes.
                    schemas.append(behavior.interface)
        return schemas

    def _getDexterityFields(self, portal_type):
        fields = {}
        for schema in self._getDexteritySchemas(portal_type):
            for name in schema:
                fields[name] = schema[name]
        return fields

    def _getDexterityField(self, portal_type, name):
        return self._getDexterityFields(portal_type).get(name, None)

    def listContentFields(self):
        types = getToolByName(self, "portal_types")
        createdType = self.getCreatedType()
        if createdType in types.keys():
            mapping = self._getDexterityFields(createdType)
            fields = [(key, mapping[key].title) for key in mapping]
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
            + sorted(transitions, lambda x, y: cmp(x[1].lower(),\
                                                   y[1].lower())))

atapi.registerType(DexterityContentAdapter, PROJECTNAME)

unrestricted = None  # hide our unholy decorator
