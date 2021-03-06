Changelog
=========

1.0.0rc2 (unreleased)
---------------------

- Nothing changed yet.


1.0.0rc1 (2016-08-29)
---------------------

- Add support for Plone 5
  [datakurre]

- Fix field population heuristics to try z3c.form widget adaptation
  at first and direct assignment only the (previously was the opposite)
  [datakurre]

0.10.1 (2014-07-01)
-------------------

- Fix to translate also list with strings to unicode
  [Asko Soukka]
- Add automatic value adaptation from single value list to Choice field
  [Asko Soukka]

0.10.0 (2014-06-27)
-------------------

- Display field ids for TTW fields, which do not have translations
  [Asko Soukka]
- Add trivial transforms for strings to sets and lists for better
  vocabulary field support
  [Asko Soukka]
- Add error classes to error messages to ease debugging type mismatch errors
  [Asko Soukka]

0.9.1 (2014-06-27)
------------------

- Fix issue where content deletion fails (after a submission error), because
  content is not even added to a container yet
  [Asko Soukka]

0.9.0 (2013-12-15)
------------------

- Fix to add created content into container only after its fields have been
  filled (to support custom id adapters)
  [Asko Soukka]

0.8.0 (2013-09-02)
------------------

- Fix to use p.dexterity.utils.getAdditionalSchemata to read behavior based
  schemas
  [Asko Soukka]
- Remove <includeDependencies />
  [Asko Soukka]
- Remove implicit dependency on plone.directives.form
  [Asko Soukka]

0.7.0 (2013-08-31)
------------------

- Fix to allow limit target folder by base folderish interfaces instead of
  portal_type [fixes #6]
  [Asko Soukka]

0.6.0 (2012-09-16)
------------------

- Support coercing of PFG DateTime fields to zope.schema.Date
  (ajung)

0.5.0 (2012-01-20)
------------------

- Added (hidden) support for adapter chaining to allow creation of
  hierarchical structures.

0.4.0 (2012-01-18)
------------------

- Refactored to masquerade as an owner of the adapter while creating content.
- Added option to make logged-in submitter the owner of the created content.
- Added option to save the URL of the created content onto request, for
  example, to be shown on a thanks page.

0.3.0 (2011-09-09)
------------------

- Updated heuristics in adapting PFG values for zope.schema.
  More field combinations should work now.

0.2.3 (2011-09-07)
------------------

- Added French translation (bklups).

0.2.2 (2011-09-06)
------------------

- Fixed broken package.

0.2.1 (2011-09-05)
------------------

- Uses z3c.form adapters to convert data from request to field value.

0.1.0 (2011-08-28)
------------------

- Proof of concept
