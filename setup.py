# -*- coding: utf-8 -*-
"""collective.pfg.dexterity"""
from setuptools import setup, find_packages

setup(
    name="collective.pfg.dexterity",
    version="0.5.0",
    description="Installs dexterity content creation adapter for PloneFormGen",
    long_description=(open("README.rst").read() + "\n" +
                      open("CHANGES.txt").read()),
    # Get more strings from
    # http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="",
    author="Asko Soukka",
    author_email="asko.soukka@iki.fi",
    url="https://github.com/datakurre/collective.pfg.dexterity/",
    license="ZPL",
    package_dir={"": "src"},
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["collective", "collective.pfg"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "five.globalrequest",
        "plone.app.dexterity",
        "Products.PloneFormGen",
        "Products.DataGridField>=1.8b1",
    ],
    extras_require={"test": [
        "corejet.core",
        "corejet.pivotal",
        "corejet.robot",
        "Pillow",
        "plone.testing",
        "plone.app.testing",
        "robotsuite",
        "robotframework-selenium2library",
        "plone.api",
        "plone.act",
    ]},
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
