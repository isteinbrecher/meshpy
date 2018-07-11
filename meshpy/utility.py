# -*- coding: utf-8 -*-
"""
This module implements some basic functions that are used in the meshpy
application.
"""

# Python modules.
import subprocess
import os
import numpy as np
import xml.etree.ElementTree as ET

# Meshpy modules.
from . import mpy, find_close_nodes


def get_section_string(section_name):
    """Return the string for a section in the dat file."""
    return ''.join(
        ['-' for i in range(mpy.dat_len_section - len(section_name))]
        ) + section_name


def get_git_data(repo):
    """Return the hash and date of the current git commit."""
    out_sha = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=repo,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    out_date = subprocess.run(['git', 'show', '-s', '--format=%ci'], cwd=repo,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if not out_sha.returncode + out_date.returncode == 0:
        return None, None
    else:
        sha = out_sha.stdout.decode('ascii').strip()
        date = out_date.stdout.decode('ascii').strip()
        return sha, date


# Set the git version in the global configuration object.
mpy.git_sha, mpy.git_date = get_git_data(
    os.path.dirname(os.path.realpath(__file__)))


def flatten(data):
    """Flatten out all list items in data."""
    flatten_list = []
    if type(data) == list:
        for item in data:
            flatten_list.extend(flatten(item))
        return flatten_list
    else:
        return [data]


def get_close_nodes(nodes, eps=mpy.eps_pos):
    """
    Find nodes that are close to each other.

    Args
    ----
    nodes: list(Node)
        Nodes that are checked for partners.
    eps: double
        Spherical value that the nodes have to be within, to be identified
        as overlapping.

    Return
    ----
    partner_nodes: list(list(Node))
        A list of lists with partner nodes.
    """

    # Remove dat nodes from list
    node_list = [node for node in nodes if not node.is_dat]

    # Get array of coordinates.
    coords = np.zeros([len(node_list), 3])
    for i, node in enumerate(node_list):
        if not node.is_dat:
            coords[i, :] = node.coordinates

    # Get list of closest pairs.
    has_partner, n_partner = find_close_nodes(coords, eps=eps)

    # Create list with nodes.
    partner_nodes = [[] for i in range(n_partner)]
    for i, node in enumerate(node_list):
        if not has_partner[i] == -1:
            partner_nodes[has_partner[i]].append(node)

    return partner_nodes


def xml_to_dict(xml):
    """Convert a XML to a nested dictionary."""

    # Get and sort keys.
    keys = xml.keys()
    keys.sort()

    # Get string for this XML element.
    string = xml.tag
    for key in keys:
        string += ' '
        string += key
        string += '="'
        string += xml.get(key)
        string += '"'

    # Add data.
    if not xml.text.strip() == '':
        string += '\n'
        string += xml.text.strip()

    # Get data for this item.
    xml_dict = {}
    n_childs = len(xml.getchildren())
    if not n_childs == 0:
        for child in xml.getchildren():
            key, value = xml_to_dict(child)
            xml_dict[key] = value

    # Return key for this item and all child items.
    return string, xml_dict


def xml_dict_to_string(xml_dict):
    """The nested XML dictionary to a string."""

    # Sort the keys
    keys = list(xml_dict.keys())
    keys.sort()

    # Add content.
    string = ''
    for key in keys:
        string += key
        string += '\n'
        string += xml_dict_to_string(xml_dict[key])
        string += '\n'

    # Return the value
    return string


def compare_xml(path1, path2):
    """Compare the xml files at path1 and path2."""

    tree1 = ET.parse(path1)
    tree2 = ET.parse(path2)

    key, value = xml_to_dict(tree1.getroot())
    hash1 = hash((xml_dict_to_string({key: value})))

    key, value = xml_to_dict(tree2.getroot())
    hash2 = hash((xml_dict_to_string({key: value})))

    return hash1 == hash2



#
#
# def _get_close_coordinates(coordinate_list, eps=1e-8):
#     """
#     Go through coordinates and return a list with all nodes that have the same
#     coordinates (within eps). Loop over all coordinates, no division
#     """
#
#     # number of coordinates
#     n_coordinates = len(coordinate_list)
#
#     # nodes that have are partner are true
#     is_single_coordinate = np.full(n_coordinates, True)
#
#     # node indices
#     coordinate_indices = np.arange(n_coordinates)
#
#     # loop over nodes
#     partner_list = []
#     for i in range(n_coordinates):
#         # check if node already has a partner
#         if is_single_coordinate[i]:
#             # get distance with all the other nodes and check if the node was already found
#             partner_nodes = (np.linalg.norm(coordinate_list - coordinate_list[i],axis=1) < eps) * is_single_coordinate
#             # check if there are partner nodes
#             if np.sum(partner_nodes) > 1:
#                 partner_indices = np.extract(partner_nodes, coordinate_indices)
#                 partner_list.append(partner_indices)
#                 is_single_coordinate[partner_indices] = False
#
#     return partner_list
#
#
# def get_close_coordinates(coordinate_list, sections=10, eps=1e-8):
#     """
#     Go through coordinates and return a list with all nodes that have the same
#     coordinates (within eps).
#
#     The global domain will be divided into n_sections in x-y-z.
#     if n_sections is an array with len 3 the segments in x, y and z can be
#     given seperately.
#     """
#
#     # check input
#     if type(coordinate_list) == np.ndarray:
#         if not (len(np.shape(coordinate_list)) == 2 and np.shape(coordinate_list)[1] == 3):
#             print('Error get_close_coordinates, not 2d array')
#             return
#         n_coordinates = np.shape(coordinate_list)[0]
#     else:
#         print('Error in get_close_coordinates, coordinates is type {}'.format(type(coordinate_list)))
#         return
#
#     if type(sections) == int:
#         n_sections = np.array([sections for i in range(3)])
#     elif type(sections == list) and len(sections) == 3:
#         n_sections = np.zeros(3)
#         for i, item in enumerate(sections):
#             if not(type(item) == int and item > 0):
#                 print('Error section not as expected!')
#             n_sections[i] = item
#     else:
#         print('Error sections is not of expected type!')
#
#     # get the spatial dimensions
#     coord_min = np.min(coordinate_list,0)
#     dimensions = np.max(coordinate_list,0) - coord_min
#     for i in range(3):
#         if abs(dimensions[i]) < eps:
#             # if dimensions are low in one direction only use one segment there
#             n_sections[i] = 1
#
#     # modify the dimensions so that integers wont be hit as much
#     eps_vector = np.array([eps for i in range(3)])
#     coord_min = coord_min - 661*eps_vector
#     dimensions = dimensions + 661*eps_vector
#
#     # group the coordinates
#     section_size = dimensions / n_sections
#     current_max = np.array([0.,0.,0.])
#     current_min = np.array([0.,0.,0.])
#     partner_list = []
#     coordinate_indices = np.arange(n_coordinates)
#     is_single_coordinate = np.full(n_coordinates, True)
#     for ix in range(n_sections[0]):
#         for iy in range(n_sections[1]):
#             for iz in range(n_sections[2]):
#
#                 # limits of current section
#                 current_min = coord_min + [ix,iy,iz]*section_size - eps_vector
#                 current_max = coord_min + [ix+1,iy+1,iz+1]*section_size + eps_vector
#
#                 # array with nodes in this section
#                 diff_max = (current_max - coordinate_list) > 0
#                 diff_min = (current_min - coordinate_list) < 0
#                 section_nodes = np.all(diff_min*diff_max,1) * is_single_coordinate
#
#                 # get matching nodes for this section
#                 section_indices = np.extract(section_nodes, coordinate_indices)
#                 partners_local = _get_close_coordinates(np.take(coordinate_list, section_indices, 0), eps=eps)
#
#                 for item in partners_local:
#                     partners_global = np.take(section_indices, item)
#                     partner_list.append(list(partners_global))
#                     is_single_coordinate[partners_global] = False
#
#     print(len(partner_list))
