"""Thid module contains function that helps to generate print path given a layer decomposition.
"""

from model.primitives import Cell, InfillGraph
from constants import *
from model.greedy import greedy_edge_selection_tsp_general_graph as greedy_selection

from math import ceil



class GridInfill():
    def __init__(self, cell: Cell, infill_graph: InfillGraph, width, height, index):
        
        self.cell = cell
        self.final_paths = []
        self.layer_peroid = 0

        ncols = ceil(height/self.cell.height)
        nrows = ceil(width/self.cell.width)
        
        self.width = nrows*self.cell.width
        self.height = ncols*self.cell.height
        
        self.shift_x = -self.width/2
        self.shift_y = -self.height/2

        path_dicts = infill_graph.get_infill_paths(index, 1) #index, scale

        i = 0
        for path in path_dicts:
            path = self._path_dict_2_grid(path, nrows, ncols)
            if i%2: path = path[:-1]
            i += 1
            self.final_paths.append(path)

        self.layer_peroid = len(self.final_paths)

    def get_grid(self, layer):
        
        return self.final_paths[layer % self.layer_peroid]
    
    def _get_paths(self, path_dict):
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

    def translate_path(self, path, offset_x, offset_y):
        """Translate a single path by the given offsets."""
        return [(round(x + offset_x, PRECISION), 
                 round(y + offset_y, PRECISION)) for (x, y) in path]

    def _connect_paths(self, paths, added_paths):
        """Connects adjacent paths that share endpoints."""
        new_paths = []
        temp_paths1 = []
        temp_paths2 = []
        
        if len(paths) == 0:
            return added_paths

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

    def remove_edge_path(self, grid_paths):
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

    def _assemble_grid(self, unit_cell_paths, m, n):
        """Assemble the paths for an m by n grid of unit cells and connect them."""
        grid_paths = []
        
        for i in range(m):
            for j in range(n):
                offset_x = i * round(self.cell.width, PRECISION)
                offset_y = j * round(self.cell.height, PRECISION)
                
                translated_paths = [self.translate_path(path, offset_x, offset_y) for path in unit_cell_paths]
                grid_paths = self._connect_paths(grid_paths, translated_paths)
        
        grid_paths = self.remove_edge_path(grid_paths)
        return grid_paths

    def connect_grid_paths(self, grid_paths):
        """
        Connect paths in unit cells of a grid to create a continuous print path, with customizable edge and boundary logic.
        Args:
        
            grid_paths (list): Paths in grid after joining unit cells.
        Returns:
            list: List of points in the continuous print path.
        """
        all_paths = grid_paths + [p[::-1] for p in grid_paths]
        endpoint_2_path = dict()
        endpoint_2_id = dict()
        endpoints = []
        top = []
        bottom = []
        left = []
        right = []

        # Function to assign endpoints to boundaries based on conditions
        residual = 0.001
        def assign_edge(endpoint):
            if abs(endpoint[0]) < residual:
                left.append(endpoint)
            elif abs(endpoint[0]- self.width) < residual:
                right.append(endpoint)
            if abs(endpoint[1]) < residual:
                bottom.append(endpoint)
            elif abs(endpoint[1] - self.height)< residual:
                top.append(endpoint)

        # Function to create edges with flexibility for custom edge-building logic
        def make_edges(grid_paths):
            edges = []
            for path in grid_paths:
                start = path[0]
                end = path[-1]
                edges.append((0, endpoint_2_id[start], endpoint_2_id[end]))

            bottom.sort(key=lambda x: x[0])
            top.sort(key=lambda x: x[0], reverse=True)
            right.sort(key=lambda x: x[1])
            left.sort(key=lambda x: x[1], reverse=True)
            
            # Create loop connections between boundary points
            loop = bottom + right + top + left
            loop = loop + [loop[0]]
            for start, end in zip(loop[:-1], loop[1:]):
                distance = abs(start[0] - end[0]) + abs(start[1] - end[1])
                edges.append((distance, endpoint_2_id[start], endpoint_2_id[end]))

            return edges
       
        # Build endpoint and edge dictionaries
        for path in all_paths:
            start = path[0]
            endpoint_2_path[start] = path
            endpoints.append(start)
            assign_edge(start)

        # Map each endpoint to an ID
        for num, node in enumerate(endpoints):
            endpoint_2_id[node] = num

        # Generate edges based on grid_paths and boundaries
        edges = make_edges(grid_paths)

        # Select a path using greedy selection
        id_path = greedy_selection(edges, len(endpoints))
        end_path = [endpoints[i] for i in id_path]

        # Create the final continuous path
        path = []
        for endpoint in end_path[::2]:
            path.extend(endpoint_2_path[endpoint])

        return path
    
    def _path_dict_2_grid(self, path_dict, m, n):
        paths = self._get_paths(path_dict)
        grid_paths = self._assemble_grid(paths, m, n)
        final_path = self.connect_grid_paths(grid_paths)
        final_path = self.translate_path(final_path, self.shift_x, self.shift_y)
        return final_path
    
      
