# -*- coding: utf-8 -*-
"""jyu.pfg.dexterity"""
from setuptools import setup, find_packages

version = "1.0"

setup(name="jyu.pfg.dexterity",
      version=version,
      description="Installs dexterity content creation adapter for PloneFormGen.",
      long_description=open("README.txt").read() + "\n" +
                       open("HISTORY.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords="",
      author="Asko Soukka",
      author_email="asko.soukka@iki.fi",
      url="",
      license="GPL",
      packages=find_packages(exclude=["ez_setup"]),
      namespace_packages=["jyu", "jyu.pfg"],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "setuptools",
        "Products.PloneFormGen",
        "Products.DataGridField",
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
