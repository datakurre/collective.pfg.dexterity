# -*- coding: utf-8 -*-
"""Interfaces"""
from zope import interface

class IDexterityContentAdapter(interface.Interface):
    """Dexterity content creation adapter for PloneFormGen"""
    
    ### See: adapter.py for Archetype-schema