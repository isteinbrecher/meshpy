# -*- coding: utf-8 -*-
"""
This script is used to test the mesh creation functions.
"""

# Python imports.
import unittest
import numpy as np
import os

# Meshpy imports.
from meshpy import (mpy, InputFile, MaterialReissner, Beam3rHerm2Lin3,
    MaterialEulerBernoulli, Beam3eb)

# Geometry functions.
from meshpy.mesh_creation_functions.beam_stent import create_beam_mesh_stent
from meshpy.mesh_creation_functions.beam_fibers_in_rectangle import (
    create_fibers_in_rectangle)

# Testing imports.
from tests.testing_utility import testing_input, compare_strings


class TestMeshCreationFunctions(unittest.TestCase):
    """
    Test the mesh creation functions.
    """

    def test_stent(self):
        """
        Test the stent creation function.
        """

        # Set default values for global parameters.
        mpy.set_default_values()

        # Create input file.
        input_file = InputFile(maintainer='Ivo Steinbrecher')

        # Add material and function.
        mat = MaterialReissner()

        # Create mesh.
        create_beam_mesh_stent(input_file, Beam3rHerm2Lin3, mat, 0.11, 0.02,
            5, 8, fac_bottom=0.6, fac_neck=0.52, fac_radius=0.36,
            alpha=0.47 * np.pi, n_el=2)

        # Check the output.
        ref_file = os.path.join(testing_input,
            'test_mesh_stent_reference.dat')
        compare_strings(
            self,
            'test_mesh_stent',
            ref_file,
            input_file.get_string(header=False))

    def test_fibers_in_rectangle(self):
        """
        Test the create_fibers_in_rectangle function.
        """

        # Set default values for global parameters.
        mpy.set_default_values()

        # Create input file.
        input_file = InputFile(maintainer='Ivo Steinbrecher')

        # Create mesh.
        mat = MaterialEulerBernoulli()
        create_fibers_in_rectangle(input_file, Beam3eb, mat,
            4, 1, 45, 0.45, 0.35)
        input_file.translate([0, 0, 1])
        create_fibers_in_rectangle(input_file, Beam3eb, mat,
            4, 1, 0, 0.45, 0.35)
        input_file.translate([0, 0, 1])
        create_fibers_in_rectangle(input_file, Beam3eb, mat,
            4, 1, 90, 0.45, 0.35)
        input_file.translate([0, 0, 1])
        create_fibers_in_rectangle(input_file, Beam3eb, mat,
            4, 1, -90, 0.45, 0.35)
        input_file.translate([0, 0, 1])
        create_fibers_in_rectangle(input_file, Beam3eb, mat,
            4, 1, 235, 0.45, 0.35)
        input_file.translate([0, 0, 1])
        create_fibers_in_rectangle(input_file, Beam3eb, mat,
            1, 4, 30, 0.45, 5)
        input_file.translate([0, 0, 1])
        create_fibers_in_rectangle(input_file, Beam3eb, mat,
            4, 1, 30, 0.45, 0.9)
        input_file.translate([0, 0, 1])

        # Check the output.
        ref_file = os.path.join(testing_input,
            'test_mesh_fiber_rectangle_reference.dat')
        compare_strings(
            self,
            'test_mesh_fiber_rectangle',
            ref_file,
            input_file.get_string(header=False))

    def test_fibers_in_rectangle_offset(self):
        """
        Test the create_fibers_in_rectangle function with using the offset
        option.
        """

        # Set default values for global parameters.
        mpy.set_default_values()

        # Create input file.
        input_file = InputFile(maintainer='Ivo Steinbrecher')

        # Create mesh.
        mat = MaterialEulerBernoulli()
        create_fibers_in_rectangle(input_file, Beam3eb, mat,
            4, 1, 45, 0.45, 0.35)
        create_fibers_in_rectangle(input_file, Beam3eb, mat,
            4, 1, 45, 0.45, 0.35, offset=0.1)

        # Check the output.
        ref_file = os.path.join(testing_input,
            'test_mesh_fiber_rectangle_offset_reference.dat')
        compare_strings(
            self,
            'test_mesh_fiber_rectangle_offset',
            ref_file,
            input_file.get_string(header=False))


if __name__ == '__main__':
    # Execution part of script.
    unittest.main()
