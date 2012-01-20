Dexterity PFG Adapter
=====================

This product installs a custom PloneFormGen adapter for creating new dexterity
content objects from PloneFormGen form submissions.

Dexterity content types must be defined by other packages or be created using
the dexterity schema editor, but otherwise the installed *Content Adapter* can
be used as a part of existing PloneFormGen adapter chains.

Also *Content Adapters* can be chained: the first adapter can be used to
create a folder and selecting the adapter as a target folder for the next
adapter, it will try to create content below that newly created folder.

When the form is published, also visitors may create content by submitting it.

By default the content is created using the permissions of the owner of the
*Content Adapter* object, but there's an option to allow logged-in form
submitter to own the content after creation.

This product could be used with other known packages to create a more complete
*through-the-web* -experience on Plone. For example:

1. Create a new custom submission content type through-the-web using
   `plone.app.dexterity <http://pypi.python.org/pypi/plone.app.dexterity>`_.
2. Create a custom tracker workflow for it using
   `plone.app.workflowmanager <http://pypi.python.org/pypi/plone.app.workflowmanager>`_.
3. Create a custom submission form using
   `PloneFormGen <http://pypi.python.org/pypi/Products.PloneFormGen>`_
   and this adapter.
4. ...
5. Profit.

This product may not yet support all of the PloneFormGen's or Dexterity's
fields. If you like the idea and think this could be useful, please,
contribute at: https://github.com/datakurre/collective.pfg.dexterity

P.S. If you find it redundant to first create a PloneFormGen-form and then
define a similar dexterity content type, check out if `uwosh.pfg.d2c
<http://pypi.python.org/pypi/uwosh.pfg.d2c>`_ is a better fit for you.
