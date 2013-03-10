# -*- coding: utf-8 -*-
import unittest

import robotsuite
from collective.pfg.dexterity.testing import ROBOT_TESTING
from plone.testing import layered


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("test_date.txt"),
                layer=ROBOT_TESTING),
    ])
    return suite
