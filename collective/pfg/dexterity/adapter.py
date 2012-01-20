# -*- coding: utf-8 -*-
"""Dexterity content creation adapter for PloneFormGen"""

import logging

import re
from time import time

from ZODB.POSException import ConflictError

from zope.component import getMultiAdapter, getUtility, queryUtility
from zope.schema import TextLine, List, Datetime
from zope.schema.interfaces import IVocabularyFactory
from zope.globalrequest import getRequest
from zope.interface import implements, alsoProvides
from zope.annotation.interfaces import IAnnotations

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager

from AccessControl import ClassSecurityInfo
from AccessControl.interfaces import IOwned

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
from plone.directives.form import IFormFieldProvider

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
            label=_("created_type_label",
                    default=u"Content type"),
            description=_("created_type_help",
                          default=(u"Select the type of new content "
                                   u"to be created."))
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
            label=_("target_folder_label",
                    default=u"Target folder"),
            description=_("target_folder_help",
                          default=(u"Select the target folder, where created "
                                   u"new content should be placed. Please, "
                                   u"make sure that the folder allows adding "
                                   u"content of the selected type.")),
            base_query={"portal_type": ("Folder",
                                        "Dexterity Content Adapter")},
        ),
        relationship="targetFolder",
        allowed_types=("Folder",),
        multiValued=False
    ),
    atapi.BooleanField(
        "giveOwnership",
        required=False,
        write_permission=ModifyPortalContent,
        read_permission=ModifyPortalContent,
        storage=atapi.AnnotationStorage(),
        searchable=False,
        widget=atapi.BooleanWidget(
            label=_("give_ownership_label",
                    default=u"Give ownership"),
            description=_("give_ownership_help",
                          default=(u"Select this to transfer the ownership of "
                                   u"created content to the logged-in user. "
                                   u"This has no effect for anonymous users."))
        ),
        default=False
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
            label=_("field_mapping_label",
                    default=u"Field mapping"),
            description=_("field_mapping_help",
                          default=(u"Map form fields to fields of the "
                                   u"selected content type. Please note, "
                                   u"that you must first select the content "
                                   u"type, then save this adapter, and only "
                                   u"then you'll be able to see the fields "
                                   u"of the selected content type.")),
            columns={
                "form": SelectColumn(
                    _("field_mapping_form_label",
                      default=u"Select a form field"),
                    vocabulary="listFormFields"),
                "content": SelectColumn(
                    _("field_mapping_content_label",
                      default=u"to be mapped to a content field."),
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
            label=_("workflow_transition_label",
                    default=u"Trigger workflow transition"),
            description=_("workflow_transition_help",
                          default=(u"You may select a workflow transition "
                                   u"to be triggered after new content is "
                                   u"created."))
        ),
    ),
    atapi.StringField(
        "createdURL",
        required=False,
        write_permission=ModifyPortalContent,
        read_permission=ModifyPortalContent,
        storage=atapi.AnnotationStorage(),
        searchable=False,
        vocabulary="listOptionalFormFields",
        widget=SelectionWidget(
            label=_("create_url_label",
                    default=u"Save URL"),
            description=_("created_url_help",
                          default=(u"You may select a form field to be "
                                   u"filled with the URL of the created "
                                   u"content. The field may be hidden on "
                                   u"the original form."))
        )
    )
))
finalizeATCTSchema(DexterityContentAdapterSchema)

DexterityContentAdapterSchema["title"].storage =\
    atapi.AnnotationStorage()
DexterityContentAdapterSchema["description"].storage =\
    atapi.AnnotationStorage()


def as_owner(func):
    """Decorator for executing actions as the context owner"""

    @ram.cache(lambda method, context, owner: (owner.getId(), time() // 60))
    def wrapped(context, owner):
        users = context.getPhysicalRoot().restrictedTraverse(
            getToolByName(context, "acl_users").getPhysicalPath())
        return owner.__of__(users)

    def wrapper(context, *args, **kwargs):
        owner = IOwned(context).getOwner()  # get the owner
        old_security_manager = getSecurityManager()
        newSecurityManager(getRequest(), wrapped(context, owner))
        try:
            return func(context, *args, **kwargs)
        except ConflictError:
            raise
        finally:
            # Note that finally is also called before return
            setSecurityManager(old_security_manager)
    return wrapper


class DexterityContentAdapter(FormActionAdapter):
    """Dexterity content creation adapter for PloneFormGen"""
    implements(IPloneFormGenActionAdapter, IDexterityContentAdapter)

    security = ClassSecurityInfo()

    portal_type = "Dexterity Content Adapter"
    schema = DexterityContentAdapterSchema

    _at_rename_after_creation = True

    title = atapi.ATFieldProperty("title")
    description = atapi.ATFieldProperty("description")

    createdType = atapi.ATFieldProperty("createdType")
    targetFolder = atapi.ATFieldProperty("targetFolder")
    fieldMapping = atapi.ATFieldProperty("fieldMapping")
    workflowTransition = atapi.ATFieldProperty("workflowTransition")

    @as_owner
    def _createAsOwner(self, targetFolder, createdType, **kw):
        return createContentInContainer(
            targetFolder, createdType, checkConstraints=True, **kw)

    @as_owner
    def _deleteAsOwner(self, container, obj):
        container.manage_delObjects([obj.getId()])

    @as_owner
    def _setAsOwner(self, context, field, value):
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
                widget = getMultiAdapter((field, getRequest()), IFieldWidget)
                converter = IDataConverter(widget)
                dm = getMultiAdapter((context, field), IDataManager)
                dm.set(converter.toFieldValue(value))
            except ConflictError:
                raise
            except Exception:
                LOG.error(e)
                return u"An unexpected error: %s" % e

    @as_owner
    def _doActionAsOwner(self, wftool, context, transition):
        try:
            wftool.doActionFor(context, transition)
        except ConflictError:
            raise
        except Exception, e:
            LOG.error(e)
            return u"An unexpected error: %s" % e

    @as_owner
    def _reindexAsOwner(self, context):
        context.reindexObject()

    security.declarePublic("onSuccess")
    def onSuccess(self, fields, REQUEST=None):
        createdType = self.getCreatedType()
        targetFolder = self.getTargetFolder()
        fieldMapping = self.getFieldMapping()
        giveOwnership = self.getGiveOwnership()
        workflowTransition = self.getWorkflowTransition()
        urlField = self.getCreatedURL()

        # Support for content adapter chaining
        annotations = IAnnotations(REQUEST)
        if targetFolder.portal_type == "Dexterity Content Adapter":
            targetFolder =\
                annotations["collective.pfg.dexterity"][targetFolder.getId()]
            # TODO: ^ We should fail more gracefully when the annotation
            # doesn't exist, but now we just let the transaction fail
            # and 500 Internal Error to be returned. (That's because a
            # previous adapter may have created content and we don't want
            # it to be persisted.)

        values = {}

        plone_utils = getToolByName(self, "plone_utils")
        site_encoding = plone_utils.getSiteEncoding()

        # Parse values from the submission
        alsoProvides(REQUEST, IFormLayer)  # let us to find z3c.form adapters
        for mapping in fieldMapping:
            field = self._getDexterityField(createdType, mapping["content"])

            if "%s_file" % mapping["form"] in REQUEST:
                value = REQUEST.get("%s_file" % mapping["form"])
            else:
                value = REQUEST.get(mapping["form"], None)
                # Convert strings to unicode
                if isinstance(value, str):
                    value = unicode(value, site_encoding, errors="replace")

            # Convert datetimes to collective.z3cform.datetime-compatible
            if isinstance(field, Datetime):
                value = re.compile("\d+").findall(value)

            # Apply a few controversial convenience heuristics
            if isinstance(field, TextLine) and isinstance(value, unicode):
                # 1) Multiple text lines into the same field
                old_value = values.get(mapping["content"])
                if old_value and value:
                    value = u" ".join((old_value[1], value))
            elif isinstance(field, List) and isinstance(value, unicode):
                # 2) Split keyword (just a guess) string into list
                value = value.replace(u",", u"\n")
                value = [s.strip() for s in value.split(u"\n") if s]

            values[mapping["content"]] = (field, value)

        # Create content with parsed title (or without it)
        try:
            # README: id for new content will be choosed by
            # INameChooser(container).chooseName(None, object),
            # so you should provide e.g. INameFromTitle adapter
            # to generate a custom id
            if "title" in values:
                context = self._createAsOwner(targetFolder, createdType,
                                              title=values.pop("title")[1])
            else:
                context = self._createAsOwner(targetFolder, createdType)
        except ConflictError:
            raise
        except Exception, e:
            LOG.error(e)
            return {FORM_ERROR_MARKER: u"An unexpected error: %s" % e}

        # Set all parsed values for the created content
        for field, value in values.values():
            error_msg = self._setAsOwner(context, field, value)
            if error_msg:
                self._deleteAsOwner(targetFolder, context)
                return {FORM_ERROR_MARKER: error_msg}

        # Give ownership for the logged-in submitter, when that's enabled
        if giveOwnership:
            mtool = getToolByName(self, "portal_membership")
            if not mtool.isAnonymousUser():
                member = mtool.getAuthenticatedMember()
                if "creators" in context.__dict__:
                    context.creators = (member.getId(),)
                IOwned(context).changeOwnership(member.getUser(), recursive=0)
                context.manage_setLocalRoles(member.getId(), ["Owner", ])

        # Trigger a worklfow transition when set
        if workflowTransition:
            wftool = getToolByName(self, "portal_workflow")
            error_msg = self._doActionAsOwner(wftool, context,
                                              workflowTransition)
            if error_msg:
                self._deleteAsOwner(targetFolder, context)
                return {FORM_ERROR_MARKER: error_msg}

        # Reindex at the end
        self._reindexAsOwner(context)

        # Set URL to the created content
        if urlField:
            REQUEST.form[urlField] = context.absolute_url()

        # Store created content also as an annotation
        if not "collective.pfg.dexterity" in annotations:
            annotations["collective.pfg.dexterity"] = {}
        annotations["collective.pfg.dexterity"][self.getId()] = context

    security.declarePrivate("listTypes")
    def listTypes(self):
        types = getToolByName(self, "portal_types")
        dexterity = [(fti.id, fti.title) for fti in types.values()
                     if IDexterityFTI.providedBy(fti)]
        return atapi.DisplayList(dexterity)

    security.declarePrivate("listFormFields")
    def listFormFields(self):
        fields = [(obj.getId(), obj.title_or_id())
                  for obj in self.aq_parent.objectValues()\
                          if IPloneFormGenField.providedBy(obj)]
        return atapi.DisplayList(fields)

    security.declarePrivate("listOptionalFormFields")
    def listOptionalFormFields(self):
        fields = [(obj.getId(), obj.title_or_id())
                  for obj in self.aq_parent.objectValues()\
                          if IPloneFormGenField.providedBy(obj)]
        return atapi.DisplayList([(u"", _(u"Don't save"))] + fields)

    @ram.cache(lambda method, self, portal_type: time() // 60)
    def _getDexteritySchemas(self, portal_type):
        fti = getUtility(IDexterityFTI, name=portal_type)
        schemas = [fti.lookupSchema()]
        # Schemas provided by behaviors can only be looked up by looping
        # through behaviors or asking SCHEMA_CACHE for subtypes...
        for behavior_name in fti.behaviors:
            behavior = queryUtility(IBehavior, name=behavior_name)
            if behavior is not None\
                and IFormFieldProvider.providedBy(behavior.interface):
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

    security.declarePrivate("listContentFields")
    def listContentFields(self):
        types = getToolByName(self, "portal_types")
        createdType = self.getCreatedType()
        if createdType in types.keys():
            mapping = self._getDexterityFields(createdType)
            fields = [(key, mapping[key].title) for key in mapping]
        else:
            fields = []
        return atapi.DisplayList(fields)

    security.declarePrivate("listTransitions")
    def listTransitions(self):
        types = getToolByName(self, "portal_types")
        createdType = self.getCreatedType()
        if createdType in types.keys():
            workflows = getToolByName(self, "portal_workflow")
            candidates = []
            transitions = []
            for workflow in [workflows.get(key) for key in\
                             workflows.getChainForPortalType(createdType)
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
