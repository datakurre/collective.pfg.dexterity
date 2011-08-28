Dexterity PFG Adapter
=====================

This is an experimental PloneFormGen adapter for creating dexterity content
using a form created with PloneFormGen through-the-web.

At least the basic text input fields and file field should work.

If the form is published, also visitors may create content submitting it.

Why would anyone want to create Dexterity content using PFG?

Well...

1. Create a new custom submission content type through-the-web using
   `plone.app.dexterity <http://pypi.python.org/pypi/plone.app.dexterity>`_.
2. Create a custom tracker workflow for it using
   `uwosh.northstar <http://pypi.python.org/pypi/uwosh.northstar>`_.
3. Create a custom submission form using
   `PloneFormGen <http://pypi.python.org/pypi/Products.PloneFormGen>`_
   and this adapter.
4. Profit.

If you like the idea and think this could be useful, please, contribute at:
https://github.com/datakurre/collective.pfg.dexterity
