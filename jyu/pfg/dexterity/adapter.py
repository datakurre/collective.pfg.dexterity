# -*- coding: utf-8 -*-
"""Dexterity content creation adapter for PloneFormGen"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.Archetypes.Widget import SelectionWidget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.CMFCore.utils import getToolByName

from Products.PloneFormGen.interfaces import IPloneFormGenField
from Products.PloneFormGen.interfaces import IPloneFormGenActionAdapter
from Products.PloneFormGen.content.actionAdapter import FormAdapterSchema
from Products.PloneFormGen.content.actionAdapter import FormActionAdapter

from Products.DataGridField import DataGridField, DataGridWidget, SelectColumn

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

from jyu.pfg.dexterity.interfaces import IDexterityContentAdapter
from jyu.pfg.dexterity.config import PROJECTNAME

from zope.i18nmessageid import MessageFactory as ZopeMessageFactory
_ = ZopeMessageFactory("jyu.pfg.dexterity")


DexterityContentAdapterSchema = FormAdapterSchema.copy() + atapi.Schema((
    atapi.StringField(
        'contentType',
        required=True,
        storage=atapi.AnnotationStorage(),
        searchable=False,
        vocabulary='listTypes',
        widget=SelectionWidget(
            label=_(u"Content type")
        ),
    ),
    atapi.ReferenceField(
        'targetFolder',
        required=True,
        storage=atapi.AnnotationStorage(),
        searchable=False,
        widget=ReferenceBrowserWidget(
            label=_(u"Target Folder"),
            description=_((u"Select folder, where content "
                           u"types should be created")),
            base_query={'portal_type': 'Folder'},
        ),
        relationship='targetFolder',
        allowed_types=('Folder',),
        multiValued=False,
    ),
    DataGridField(
        'fieldMapping',
        required=True,
        storage=atapi.AnnotationStorage(),
        searchable=False,
        allow_delete=True,
        allow_insert=True,
        allow_reorder=True,
        columns=('form', 'content'),
        widget=DataGridWidget(
            label=_(u"Form-to-content field mapping"),
            description=_((u"Maps specific form fields to available payables. "
                           u"Each payable will be added into shopping cart "
                           u"with the quantity defined by its mapped field's "
                           u"value 'true' will be interpreted as '1'.")),
            columns={
                'form': SelectColumn(_(u"Map form field"),vocabulary='listFormFields'),
                'content': SelectColumn(_(u"to content"), vocabulary='listContentFields')
            },
        ),
    ),
    atapi.StringField(
        'workflowTransition',
        required=True,
        storage=atapi.AnnotationStorage(),
        searchable=False,
        vocabulary='listTransitions',
        widget=SelectionWidget(
            label=_(u"Trigger Workflow Event")
        ),
    ),
))
finalizeATCTSchema(DexterityContentAdapterSchema)

DexterityContentAdapterSchema["title"].storage = atapi.AnnotationStorage()
DexterityContentAdapterSchema["description"].storage = atapi.AnnotationStorage()


class DexterityContentAdapter(FormActionAdapter):
    """Dexterity content creation adapter for PloneFormGen"""
    implements(IPloneFormGenActionAdapter, IDexterityContentAdapter)
    
    portal_type = 'Dexterity Content Adapter'
    schema = DexterityContentAdapterSchema

    _at_rename_after_creation = True
    
    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    fieldMapping = atapi.ATFieldProperty('fieldMapping')

    def onSuccess(self, fields, REQUEST=None):
        import pdb; pdb.set_trace()

    def listTypes(self):
        types = getToolByName(self.context, "portal_types")
        import pdb; pdb.set_trace()
        return atapi.DisplayList(())

    def listFormFields(self):
        fields = [(obj.getId(), obj.title_or_id())
                  for obj in self.aq_parent.objectValues()\
                          if IPloneFormGenField.providedBy(obj)]
        return atapi.DisplayList(fields)

    def listContentFields(self):
        import pdb; pdb.set_trace()
        return atapi.DisplayList(())

    def listTransition(self):
        wftool = getToolByName(self.context, "portal_workflow")
        import pdb; pdb.set_trace()
        return atapi.DisplayList(())


atapi.registerType(DexterityContentAdapter, PROJECTNAME)

#        reference_catalog = getToolByName(self, "reference_catalog")
#
#        cart = component.getUtility(interfaces.IShoppingCartUtility).get(self)
#        if cart is not None and self.emptyCart:
#           cart = component.getUtility(interfaces.IShoppingCartUtility).destroy(self)
#        if cart is None:
#            cart = component.getUtility(interfaces.IShoppingCartUtility)\
#                            .get(self, create=True)
#
#        for mapping in self.fieldMapping:
#            amount = REQUEST and self.toInt(REQUEST.form.get(mapping['field'], 0)) or 0
#            payable = reference_catalog.lookupObject(mapping['payable'])
#            if amount > 0 and payable is not None:
#                item_factory = component.getMultiAdapter((cart, payable),
#                                                         interfaces.ILineItemFactory)
#                item_factory.create(amount)
#        # See Products.PloneFormGen.content.actionAdapter.onSuccess() for return options
#        return None

#    def toInt(self, value):
#        if value in [True, 'True']:
#            return 1
#        elif value:
#            try:
#                return int(value)
#            except:
#                return 1
#        else:
#            return 0
                
#    def listPayables(self):
#        portal_catalog = getToolByName(self, 'portal_catalog')
#        portal_url = getToolByName(self, 'portal_url')
#        portal_path = '/'.join(portal_url.getPortalObject().getPhysicalPath())
#        query = portal_catalog.searchResults({
#          'object_provides': IPayableMarker.__identifier__,
#          'path': portal_path
#        })
#        payables = [
#          (o.UID(), "%s (%s)" % (o.title, self.with_currency(interfaces.IPayable(o).price))) \
#          for o in [brain.getObject() for brain in query]
#        ]
#        return atapi.DisplayList(payables)