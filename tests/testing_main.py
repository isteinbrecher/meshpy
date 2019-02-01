# -*- coding: utf-8 -*-
"""
This script is used to call all unit test modules in python.
"""

# Python imports.
import os
import sys
import unittest

# Import testing functions.
from tests.testing_utility import empty_testing_directory

# Set path to find meshpy.
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..')))


if __name__ == '__main__':
    # Ececution part of scritpt.

    empty_testing_directory()

    # Load the test cases.
    testsuite = unittest.TestLoader().discover('.', pattern='testing_*.py')
#     testsuite = unittest.TestLoader().discover('.',
#         pattern='testing_baci.py')
#     testsuite = unittest.TestLoader().discover('.',
#         pattern='testing_meshpy.py')
#     testsuite = unittest.TestLoader().discover('.',
#         pattern='testing_rotations.py')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
