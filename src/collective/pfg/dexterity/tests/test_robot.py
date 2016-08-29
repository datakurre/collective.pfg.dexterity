# -*- coding: utf-8 -*-
from collective.pfg.dexterity.testing import ROBOT_TESTING
from plone.testing import layered

import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite('test_date.robot'),
                layer=ROBOT_TESTING),
    ])
    return suite
