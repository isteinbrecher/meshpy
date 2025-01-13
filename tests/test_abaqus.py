# -*- coding: utf-8 -*-
# MeshPy: A beam finite element input generator
#
# MIT License
#
# Copyright (c) 2018-2025
#     Ivo Steinbrecher
#     Institute for Mathematics and Computer-Based Simulation
#     Universitaet der Bundeswehr Muenchen
#     https://www.unibw.de/imcs-en
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""This script is used to test the creation of Abaqus input files."""

import numpy as np

from meshpy import GeometrySet, Mesh, Rotation
from meshpy.abaqus import (
    AbaqusBeamMaterial,
    AbaqusBeamNormalDefinition,
    AbaqusInputFile,
    generate_abaqus_beam,
)
from meshpy.mesh_creation_functions.beam_basic_geometry import create_beam_mesh_line


def test_abaqus_helix(assert_results_equal, get_corresponding_reference_file_path):
    """Create a helix and check the created Abaqus input file."""

    # Helix parameters
    n_el = 10
    turns = 1.5
    length = 1.0
    r = 0.5

    mesh = Mesh()
    mat = AbaqusBeamMaterial("beam_material")
    beam_type = generate_abaqus_beam("B32H")
    helix_set = create_beam_mesh_line(
        mesh,
        beam_type,
        mat,
        [r, 0, 0],
        [r, r * 2.0 * np.pi * turns, length],
        n_el=n_el,
    )
    mesh.wrap_around_cylinder()

    start_set = helix_set["start"]
    start_set.name = "fix_node"
    mesh.add(start_set)

    end_set = helix_set["end"]
    end_set.name = "load_node"
    mesh.add(end_set)

    end_set = helix_set["line"]
    end_set.name = "beam_elements"
    mesh.add(end_set)

    input_file = AbaqusInputFile(mesh)
    assert_results_equal(
        get_corresponding_reference_file_path(extension="inp"),
        input_file.get_input_file_string(
            AbaqusBeamNormalDefinition.smallest_rotation_of_triad_at_first_node
        ),
        string_splitter=",",
        atol=1e-14,
    )


def test_abaqus_frame(assert_results_equal, get_corresponding_reference_file_path):
    """Create a frame out of connected beams with different materials."""

    mesh = Mesh()
    mat_1 = AbaqusBeamMaterial("beam_material_1")
    mat_2 = AbaqusBeamMaterial("beam_material_2")
    beam_type_b23 = generate_abaqus_beam("B32H")
    beam_type_b33 = generate_abaqus_beam("B33H")

    create_beam_mesh_line(mesh, beam_type_b23, mat_1, [0, 0, 0], [1, 0, 0], n_el=2)
    mesh.rotate(Rotation([1, 0, 0], np.pi * 0.5))
    create_beam_mesh_line(mesh, beam_type_b23, mat_2, [1, 0, 0], [1, 1, 0], n_el=2)
    create_beam_mesh_line(mesh, beam_type_b33, mat_1, [1, 1, 0], [1, 1, 1], n_el=2)
    create_beam_mesh_line(mesh, beam_type_b33, mat_2, [1, 1, 1], [0, 1, 1], n_el=2)
    mesh.couple_nodes()

    fix_set = GeometrySet(mesh.nodes[0], name="fix_node")
    load_set = GeometrySet(mesh.nodes[-1], name="load_node")
    mesh.add(fix_set, load_set)

    input_file = AbaqusInputFile(mesh)
    assert_results_equal(
        get_corresponding_reference_file_path(extension="inp"),
        input_file.get_input_file_string(
            AbaqusBeamNormalDefinition.smallest_rotation_of_triad_at_first_node
        ),
        string_splitter=",",
        atol=1e-15,
    )