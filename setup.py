# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='collective.pfg.dexterity',
    version='1.0.0rc1',
    description='Installs dexterity content creation adapter for PloneFormGen',
    long_description=(open('README.rst').read() + '\n' +
                      open('CHANGELOG.rst').read()),
    # Get more strings from
    # http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone PloneFormGen Dexterity',
    author='Asko Soukka',
    author_email='asko.soukka@iki.fi',
    url='https://github.com/datakurre/collective.pfg.dexterity/',
    license='ZPL',
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.pfg'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'five.globalrequest',
        'plone.autoform',
        'plone.app.dexterity',
        'Products.PloneFormGen',
        'Products.DataGridField>=1.8b1'
    ],
    extras_require={'test': [
        'Pillow',
        'corejet.core',
        'plone.testing',
        'plone.app.testing',
        'plone.app.robotframework',
    ]},
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
