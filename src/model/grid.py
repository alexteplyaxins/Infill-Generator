"""Thid module contains function that helps to generate print path given a layer decomposition.
"""

import matplotlib.pyplot as plt
from model.primitives import (
    Cell, 
    InfillGraph
)
from constants import *
import numpy as np
from model.greedy import greedy_edge_selection_tsp_general_graph as greedy_selection

def get_paths(path_dict):
    """Transform a paths dict to a paths list

    Args:
        path_dict (dict): A dictionary that defines a path in a unitcell.
        See more at model.primitives.InfillGraph.get_infill_paths

    Returns:
        list: A list of point along a path in a unitcell.
    """
    for node in path_dict.keys():
        if path_dict[node]["backward"][1]:
            start = node
            break

    paths = []
    temp = [start]
    node = path_dict[node]["forward"][0]
    while node != start:
        temp.append(node)
        node, halt = path_dict[node]["forward"]
        if halt:
            paths.append(temp)
            temp = []

    return paths

def translate_path(path, offset_x, offset_y):
    """Translate a single path by the given offsets."""
    return [(round(x + offset_x, PRECISION), round(y + offset_y, PRECISION)) for (x, y) in path]

def connect_paths(paths, added_paths):
    """Connects adjacent paths that share endpoints."""
    new_paths = []
    temp_paths1 = []
    temp_paths2 = []
    
    if len(paths) == 0:
        return added_paths
    
    joined = set()

    for path1 in paths:
        for path2 in added_paths:
            if path1[-1] == path2[0]:
                temp = path1 + path2[1:]
                temp_paths1.append(temp)
                break
        else:
            temp_paths2.append(path1)

    for path2 in added_paths:
        for path1 in paths:
            if path1[-1] == path2[0]:
                break
        else:
            temp_paths1.append(path2)

    for path1 in temp_paths1:
        for path2 in temp_paths2:
            if path1[-1] == path2[0]:
                temp = path1 + path2[1:]
                new_paths.append(temp)
                break
        else:
            new_paths.append(path1)

    for path2 in temp_paths2:
        for path1 in temp_paths1:
            if path1[-1] == path2[0]:
                break
        else:
            new_paths.append(path2)

    return new_paths

def remove_edge_path(grid_paths):
    """Remove print paths along the edge of the infill because of overlap.

    Args:
        grid_paths (list): list of paths in the infill before joining.

    Returns:
        list: list of paths but with path along edge removed.
    """
    paths = []
    for path in grid_paths:
        if path[0][0] == 0 and path[1][0]==0:
            path = path[1:]
        elif path[0][1] == 0 and path[1][1]==0:
            path = path[1:]
        elif path[-1][0] == 0 and path[-2][0]==0:
            path = path[:-1]
        elif path[-1][1] == 0 and path[-2][1]==0:
            path = path[:-1]
        if(len(path)>2):
            paths.append(path)
    return paths

def assemble_grid(unit_cell_paths, m, n, cell_width, cell_height):
    """Assemble the paths for an m by n grid of unit cells and connect them."""
    grid_paths = []
    
    for i in range(m):
        for j in range(n):
            offset_x = i * cell_width
            offset_y = j * cell_height
            
            translated_paths = [translate_path(path, offset_x, offset_y) for path in unit_cell_paths]
            grid_paths = connect_paths(grid_paths, translated_paths)
    
    grid_paths = remove_edge_path(grid_paths)
    return grid_paths

def connect_grid_paths(grid_paths, width, height):
    """Connect all paths in all unitcell in a grid to a continuous print path.

    Args:
        grid_paths (list): paths in grid after joining unit cells.
        width (float): grid width
        height (_type_): grid height

    Returns:
        list: list of points in the print path.
    """
    all_paths = grid_paths + [p[::-1] for p in grid_paths]
    endpoint_2_path = dict()
    endpoint_2_id = dict()
    endpoints = []
    top = []
    bottom = []
    left = []
    right = []
    
    def assign_edge(endpoint): #Get all point on the 4 boundaries
        if endpoint[0] == 0:
            left.append(endpoint)
        if endpoint[0] == width:
            right.append(endpoint)
        if endpoint[1] == 0:
            bottom.append(endpoint)
        if endpoint[1] == height:
            top.append(endpoint)
        
        
    
    def make_edges(grid_paths): #Build a paths graph for greedy expansion
        edges = []
        for path in grid_paths:
            start = path[0]
            end = path[-1]
            edges.append((0, endpoint_2_id[start], endpoint_2_id[end]))
        
        bottom.sort(key=lambda x: x[0])
        top.sort(key=lambda x: x[0], reverse=True)
        right.sort(key=lambda x: x[1])
        left.sort(key=lambda x: x[1], reverse=True)
        loop = bottom + right + top + left
        loop = loop + [loop[0]]
        
        for start, end in zip(loop[:-1], loop[1:]):
            length = abs(start[0]-end[0]) + abs(start[1]-end[1])
            edges.append((length, endpoint_2_id[start], endpoint_2_id[end]))

        return edges

    for path in all_paths:
        start = path[0]
        endpoint_2_path[start] = path
        endpoints.append(start)
        assign_edge(start)

    for num, node in enumerate(endpoints):
        endpoint_2_id[node] = num

    edges = make_edges(grid_paths)
    id_path = greedy_selection(edges, len(endpoints))
    end_path = [endpoints[i] for i in id_path]
    path = []
    for endpoint in end_path[::2]:
        path.extend(endpoint_2_path[endpoint])
    return path
    
def plot_paths(paths):
    """
    Plots the paths of a rectangular unit cell.

    Parameters:
        paths (list of list of tuple): A list where each element is a path (a list of points),
                                       and each point is represented by a tuple (x, y).

    Example:
        paths = [
            [(0, 0), (1, 1), (2, 0)],
            [(1, 0), (1, 1), (1, 2)]
        ]
        plot_paths(paths)
    """

    for path in paths:
        # print(path)
        x_coords, y_coords = zip(*path)
        # print(x_coords, y_coords)
        plt.plot(x_coords, y_coords, marker='o')

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Paths in Rectangular Unit Cell')
    plt.grid(True)
    plt.gca().set_aspect('equal', adjustable='box')
    # plt.show()

def path_dict_2_grid(path_dict, m, n, width, height):
    paths = get_paths(path_dict)
    grid_paths = assemble_grid(paths, m, n, width, height)
    final_path = connect_grid_paths(grid_paths, round(m*width, PRECISION), round(n*height, PRECISION))
    return final_path

if __name__ == "__main__":
    cell = Cell(r"../DXF files/arrowhead.DXF")
    a = 2
    b = 2
    graph = InfillGraph(cell, a, b)
    graph.combine_cycle(3)
    path_dicts = graph.get_infill_paths(2, 1)
    fig = plt.figure()
    # graph.plot_comb(1, fig)
    # plt.show()
    path_dict = path_dicts[2]
    paths = get_paths(path_dict)
    grid_paths = assemble_grid(paths, 5, 5, round(a*cell.width, PRECISION), round(b*cell.height, PRECISION))
    final_path = path_dict_2_grid(path_dict, 5, 5, round(a*cell.width, PRECISION), round(b*cell.height, PRECISION))
    # plot_paths(grid_paths)
    plot_paths([final_path])
    plt.show()