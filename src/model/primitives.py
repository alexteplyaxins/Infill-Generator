import matplotlib.axes
import numpy as np
from itertools import combinations
import networkx as nx
import ezdxf
from ezdxf import recover, bbox
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from model.utils import get_intersection, dissolve_segment, set_equal_aspect
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from constants import *
import matplotlib

class Cell:
    """A class representing a 2D geometric unit cell extracted from a DXF file.

    This class reads a DXF file to extract geometric information, including points, 
    edges, width, and height. It processes the geometry to handle intersections and 
    provides methods for visualizing the unit cell and its infill patterns.

    Parameters
    ----------
    file_path : str
        The path to the DXF file containing the geometric definitions.

    Attributes
    ----------
    points : set
        A set of unique points extracted from the DXF file.
    edges : set
        A set of edges representing the geometric structure of the unit cell.
    width : float
        The width of the bounding box enclosing the unit cell.
    height : float
        The height of the bounding box enclosing the unit cell.
    doc : ezdxf.document
        The EZDXF document object representing the loaded DXF file.

    Methods
    -------
    postprocess()
        Processes the edges to find and handle geometric intersections.
    read_dxf(file_path)
        Reads a DXF file, processes its entities, and extracts points, edges, width, 
        height, and the document object.
    plot_dxf(ax)
        Plots the original DXF geometry onto the provided Matplotlib Axes.
    plot(ax)
        Plots the unit cell geometry (edges and points) onto the provided Matplotlib Axes.
    plot_infill(ax, size)
        Plots the infill pattern on the provided Matplotlib Axes based on the specified 
        grid size.
    plot_preview(fig)
        Generates a preview figure displaying both the unit cell and its corresponding 
        infill pattern in a side-by-side layout.
    """

    def __init__(self, file_path, scale):
        """Initializes a Cell instance by reading a DXF file and extracting geometric data.

        Parameters
        ----------
        file_path : str
            The path to the DXF file to be read.
        """
        self.points, self.edges, self.width, self.height, self.doc = self.read_dxf(file_path) #Read dxf
        self.postprocess() #Postprocess
        self.set_scale(scale)


    def postprocess(self):
        """Processes the edges to identify and handle intersections and dissolve segments as necessary.

        This method checks each edge against all others to find intersections, 
        updates the points set, and modifies edges based on intersection points.
        """
        intersections = dict() #Dictionary to keep track of edges with intersections, will be used to dissolve these edges
        # Iterate through each edge to check for intersections with other edges.
        for edge1 in self.edges:
            end_points1 = [(edge1[0], edge1[1]), (edge1[2], edge1[3])]
            for edge2 in self.edges:
                is_intersect, intersection = get_intersection(edge1, edge2) #Check for intersection
                for point in intersection: #Round all intersections to predefined precision
                    temp = tuple(map(lambda x: round(x, PRECISION), point)) 
                    intersection.remove(point)
                    intersection.add(temp)

                if not is_intersect:
                    continue
                
                self.points.update(intersection) #Add intersections to points

                if(intersection not in end_points1): #Add edges an their intersections to dictionary
                    if(edge1 not in intersections.keys()):
                        intersections[edge1] = set()
                    intersections[edge1].update(intersection)

        for edge in intersections.keys(): #Dissolve edges and add new dissolved edges
            new_edges = dissolve_segment(edge, intersections[edge])
            self.edges.remove(edge)
            self.edges.update(new_edges)
                 
    def read_dxf(self, file_path):
        """Reads a DXF file, processes its entities, and extracts points, edges, width, height, and the document object.

        Parameters
        ----------
        file_path : str
            The path to the DXF file to be read.

        Returns
        -------
        tuple
            A tuple containing the extracted points, edges, width, height, and the document object.
        """
        # read dxf file
        try:
            doc, auditor = recover.readfile(file_path)
        except IOError as e:
            raise e
        except ezdxf.DXFStructureError as e:
            raise e

        msp = doc.modelspace()

        #some processing
        for e in msp:
            if e.dxftype() in ["LWPOLYLINE", "POLYLINE"]:
                e.explode()

        for e in msp:
            if e.dxftype() in ["CIRCLE", "ARC"]:
                e.to_ellipse()

        #get bounding box, width, height
        cache = bbox.Cache()
        bounding_box = bbox.extents(msp, cache=cache)
        rect_vertices = bounding_box.rect_vertices()
        width = round(rect_vertices[2][0] - rect_vertices[0][0], PRECISION)
        height = round(rect_vertices[2][1] - rect_vertices[0][1], PRECISION)
        dx, dy = -rect_vertices[0][0], -rect_vertices[0][1]

        points = set()
        edges = set()
        for e in msp: #For all entities in the dxf file
            temp = e.translate(dx=dx, dy=dy, dz=0) #Translate so that the bottom left corner is at (0, 0)
            if temp.dxftype() == "LINE": #Add line
                x1, y1, _ = temp.dxf.start
                x2, y2, _ = temp.dxf.end
                x1 = round(x1, PRECISION)
                y1 = round(y1, PRECISION)
                x2 = round(x2, PRECISION)
                y2 = round(y2, PRECISION)
                if((x1, y1) != (x2, y2)):
                    points.add((x1, y1))
                    points.add((x2, y2))
                    if (x2, y2, x1, y1) not in edges:
                        edges.add((x1, y1, x2, y2))

            if temp.dxftype() == "ELLIPSE": #Add ellipse
                start_angle = temp.dxf.start_param
                end_angle = temp.dxf.end_param
                
                if(start_angle>end_angle):
                    end_angle += 2*np.pi

                angles = np.linspace(start_angle, end_angle, int(np.abs(end_angle-start_angle)*11/np.pi))
                for i in angles:
                    if i > 2*np.pi:
                        i -= 2*np.pi

                temp = None
                for point in e.vertices(angles):
                    i = [round(j, PRECISION) for j in list(point)]
                    points.add((i[0], i[1]))
                    if temp is not None:
                        if (i[0], i[1], temp[0], temp[1]) not in edges:
                            edges.add((temp[0], temp[1], i[0], i[1]))
                    temp = (i[0], i[1])
                
        return points, edges, width, height, doc
            

    def plot_dxf(self, ax):
        """Plots the original DXF geometry onto the provided Matplotlib Axes.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The Matplotlib Axes object where the geometry will be plotted.
        """
        msp = self.doc.modelspace()
        ctx = RenderContext(self.doc)
        out = MatplotlibBackend(ax)
        Frontend(ctx, out).draw_layout(msp, finalize=True)

    def plot(self, ax):
        """Plots the unit cell geometry (edges and points) onto the provided Matplotlib Axes.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The Matplotlib Axes object where the geometry will be plotted.
        """
        # Draw the bounding rectangle of the unit cell.
        ax.add_patch(
            Rectangle(
                (0, 0), self.width, self.height, 
                linewidth=1, 
                edgecolor='lightgrey', 
                facecolor='none', 
                linestyle="--"
            )
        )
        for edge in self.edges: # Draw edges
            x = np.array([edge[0], edge[2]])
            y = np.array([edge[1], edge[3]])
            ax.plot(x, y, color='black', linewidth=1)
        for point in self.points: # Draw points
            x = point[0]
            y = point[1]
            ax.plot(x, y, 'o', color='green', markersize=3)
        ax.set_aspect('equal', 'box')
    
    def plot_infill(self, ax: matplotlib.axes.Axes, size: tuple = (5, 5)):
        """Plots the infill pattern geometry (edges and points) onto the provided Matplotlib Axes.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The Matplotlib Axes object where the geometry will be plotted.
        size: tuple of int
            The size of the infill pattern to be plotted.
        """
        for i in range(size[0]):
            for j in range(size[1]):
                for edge in self.edges:
                    x = [edge[0] + i*self.width, edge[2] + i*self.width]
                    y = [edge[1] + j*self.height, edge[3] + j*self.height]
                    ax.plot(x, y, color='black', linewidth=1)
        
        ax.set_aspect('equal', 'box')

    def plot_preview(self, fig: matplotlib.figure.Figure):
        """Plot both the unit cell and the infill pattern.

        Args:
            fig (matplotlib.figure.Figure): _description_
        """
        ax1, ax2 = fig.subplots(1, 2)
        self.plot(ax1)
        self.plot_infill(ax2)
        ax1.set_title('Unitcell')
        ax2.set_title('Infill preview')
    
    def set_scale(self, factor):
        """Scales the unit cell geometry by a specified factor.

        Parameters
        ----------
        factor : float
            The scaling factor. A factor > 1 will enlarge the unit cell, while
            a factor < 1 will shrink it.
        """
        # Scale points
        scaled_points = set()
        for point in self.points:
            scaled_point = (point[0] * factor, point[1] * factor)
            scaled_points.add(scaled_point)
        self.points = scaled_points

        # Scale edges
        scaled_edges = set()
        for edge in self.edges:
            scaled_edge = (
                edge[0] * factor, edge[1] * factor,
                edge[2] * factor, edge[3] * factor
            )
            scaled_edges.add(scaled_edge)
        self.edges = scaled_edges

        # Scale width and height
        self.width *= factor
        self.height *= factor

class InfillGraph:
    """ A class to represent a graph for the infill pattern of a 3D printing unit cell.

    The graph is constructed based on the geometry of a given `Cell` object,
    representing the unit cell of a 3D print. It creates nodes for points and edges for 
    connections between points, allowing for the computation of Hamiltonian cycles that can be 
    used for infill path generation.

    Attributes:
        cell (Cell): The Cell object representing the geometry of the unit cell.
        graph (networkx.Graph): The graph representation of the unit cell points and edges.
        mapped_points (dict): A mapping of original points to their positions in the graph.
        width (float): The total width of the unit cell array.
        height (float): The total height of the unit cell array.
        cycles (list): A list of cycles found in the graph.
        cycle_comb_list (list): A list of valid combinations of cycles that cover the edges.

    Parameters:
        cell (Cell): The Cell object to initialize the infill graph.
        ncols (int): The number of columns in the unit cell array (default is 1).
        nrows (int): The number of rows in the unit cell array (default is 1).

    Raises:
        Exception: If the unit cell is not connected or if there are not enough splits found.

    Methods:
        remove_invalid_cycles(): Filters out invalid cycles from the cycle list.
        find_cycles(): Finds all Hamiltonian cycles in the graph.
        combine_cycle(n: int): Combines cycles in the graph, checking if they cover all edges.
        get_infill_paths(index: int, scale: float): Retrieves infill paths based on cycle combinations.
        plot_cycle(ax, cycle: tuple): Plots a specific cycle on the provided axis.
        plot(ax): Plots the entire graph on the provided axis.
        get_plot_comb_num(): Returns a list of indices for available cycle combinations.
        plot_comb(index: int, fig): Plots the specified cycle combination in a 3D space.
    """
    def __init__(self, cell: Cell, ncols: int = 1, nrows: int = 1):
        self.cell = cell
        
        self.graph = nx.Graph()
        self.mapped_points = dict()
        self.width = round(self.cell.width*ncols, PRECISION)
        self.height = round(self.cell.height*nrows, PRECISION)

        for i in range(ncols):
            for j in range(nrows):
                for node in self.cell.points:
                    self.graph.add_node((node[0]+i*self.cell.width, node[1]+j*self.cell.height), kind=0)

                for edge in self.cell.edges:
                    point1 = (edge[0] + i*self.cell.width, edge[1] + j*self.cell.height)
                    point2 = (edge[2] + i*self.cell.width, edge[3] + j*self.cell.height)
                    self.graph.add_edge(point1, point2, kind=0)

        connected = False     
        for node in self.cell.points:
            if node[0] == 0 and (self.cell.width, node[1]) in self.cell.points:
                connected = True
                for i in range(nrows):
                    self.graph.nodes[(0, node[1]+i*self.cell.height)]["kind"] = 1
                    self.graph.nodes[(self.cell.width*ncols, node[1]+i*self.cell.height)]["kind"] = 1
                    self.graph.add_edge((0, node[1]+i*self.cell.height), (self.cell.width*ncols, node[1]+i*self.cell.height), kind=1)
                    self.mapped_points[(0, node[1]+i*self.cell.height)] = (self.cell.width*ncols, node[1]+i*self.cell.height)
                    self.mapped_points[(self.cell.width*ncols, node[1]+i*self.cell.height)] = (0, node[1]+i*self.cell.height)
            
            if node[1] == 0 and (node[0], self.cell.height) in self.cell.points:
                connected = True
                for i in range(ncols):
                    self.graph.nodes[(node[0]+i*self.cell.width, 0)]["kind"] = 2
                    self.graph.nodes[(node[0]+i*self.cell.width, self.cell.height*nrows)]["kind"] = 2
                    self.graph.add_edge((node[0]+i*self.cell.width, 0), (node[0]+i*self.cell.width, self.cell.height*nrows), kind=2)
                    self.mapped_points[(node[0]+i*self.cell.width, 0)] = (node[0]+i*self.cell.width, self.cell.height*nrows)
                    self.mapped_points[(node[0]+i*self.cell.width, self.cell.height*nrows)] = (node[0]+i*self.cell.width, 0)
        connected = connected and nx.is_connected(self.graph)
        if connected:
            self.cycles = self.find_cycles()
            self.cycles = self.remove_invalid_cylces()
            if len(self.cycles) < 2:
                raise Exception("Not enough splits found")
        else:
            raise Exception("Unit cell is not connected.")
        
    def remove_invalid_cylces(self):
        def check_cycle(cycle):
            x_cell = 0
            y_cell = 0
            for i in range(1, len(cycle)):
                if cycle[i] in self.mapped_points and cycle[i-1] == self.mapped_points.get(cycle[i], None):
                    if cycle[i][0] == 0:
                        x_cell += 1
                    if cycle[i-1][0] == 0:
                        x_cell -= 1
                    if cycle[i][1] == 0:
                        y_cell += 1
                    if cycle[i-1][1] == 0:
                        y_cell -= 1
            return (x_cell != 0) or (y_cell != 0)
        
        res = []
        for cycle in self.cycles:
            if check_cycle(cycle):
                res.append(cycle)
        return res

    def find_cycles(self):
        num_nodes = len(self.graph)
        cycles = []
        nodes = list(self.graph.nodes())

        def backtrack(path, visited):
            current_node = path[-1]

            def end():
                stop = len(visited) == num_nodes
                stop = stop or ((len(visited) == num_nodes-1) and (current_node in self.mapped_points) and (self.mapped_points.get(current_node, None) not in visited))
                if stop:
                    if path[0] in self.graph.neighbors(current_node):
                        temp = path + [path[0]]
                        if tuple(reversed(temp)) not in cycles:
                            cycles.append(tuple(temp))
                    if self.mapped_points.get(path[0], None) in self.graph.neighbors(current_node):
                        temp = path + [self.mapped_points[path[0]], path[0]]
                        if tuple(reversed(temp)) not in cycles:
                            cycles.append(tuple(temp))

            end()
                    
            for neighbor in self.graph.neighbors(current_node):
                if neighbor not in visited:
                    condition = current_node in self.mapped_points
                    condition = condition and (self.mapped_points.get(current_node, None) != neighbor) 
                    condition = condition and (self.mapped_points.get(current_node, None) not in visited)
                    if condition:
                        visited.add(neighbor)
                        visited.add(self.mapped_points[current_node])
                        backtrack(path + [neighbor], visited)
                        visited.remove(neighbor)
                        visited.remove(self.mapped_points[current_node])
                    else:
                        visited.add(neighbor)
                        backtrack(path + [neighbor], visited)
                        visited.remove(neighbor)
                    
        if len(nodes) == 0:
            return cycles

        backtrack([nodes[0]], {nodes[0]})

        return cycles  
    
    def combine_cycle(self, n: int):
        # Get all edges in the graph, normalized for undirected edges
        graph_edges = {tuple(sorted(edge)) for edge in self.graph.edges() if self.graph.get_edge_data(edge[0], edge[1], default={}).get('kind', None)==0}

        # Check all combinations of n cycles
        cycle_comb_list = []
        if len(self.cycles) < n:
            raise Exception("Not able to split: n is too large.")
        
        for cycle_comb in combinations(self.cycles, n):
            # Get the set of edges covered by this combination of cycles
            covered_edges = set()
            for cycle in cycle_comb:
                # Normalize the edges in the cycle for undirected edges
                cycle_edges = [tuple(sorted((cycle[i], cycle[i+1]))) for i in range(len(cycle) - 1) if self.graph.get_edge_data(cycle[i], cycle[i+1], default={}).get('kind', None)==0]
                covered_edges.update(cycle_edges)
    
            # Check if this set of cycles covers all the edges of the graph
            if covered_edges == graph_edges:
                cycle_comb_list.append(cycle_comb)
        
        # If no such combination is found, return None
        if len(cycle_comb_list) == 0:
            raise Exception("Not able to split: Splits can't cover unit cell.")
        self.cycle_comb_list = cycle_comb_list

    def get_infill_paths(self, index, scale):
        # scale here is not necessary, might remove later
        paths = []
        for cycle in self.cycle_comb_list[index]:
            path = dict()

            if cycle[1] == cycle[-2]:
                cycle = cycle[1:-1]

            for node1, node2 in zip(cycle[:-1], cycle[1:]):
                halt = True if node1 in self.mapped_points and node2 == self.mapped_points.get(node1, None) else False
                
                node1_p = (round(node1[0]*scale, PRECISION), round(node1[1]*scale, PRECISION))
                node2_p = (round(node2[0]*scale, PRECISION), round(node2[1]*scale, PRECISION))

                if node1_p not in path:
                    path[node1_p] = {"backward":None, "forward":None}
                if node2 not in path:
                    path[node2_p] = {"backward":None, "forward":None}

                path[node1_p]["forward"] = (node2_p, halt)
                path[node2_p]["backward"] = (node1_p, halt)

            paths.append(path)
        return paths
                
    def plot_cycle(self, ax, cycle: tuple):
        pos = {point: point for point in self.graph.nodes}
        
        nx.draw_networkx_nodes(self.graph, pos, ax=ax, node_color = 'r', node_size = 10, alpha = 1)
        
        edges = []
        for (node1, node2) in tuple(zip(cycle[:-1], cycle[1:])):
            edges.append((node1, node2, self.graph.get_edge_data(node1, node2)))

        for e in edges:
            connectionstyle = "arc3,rad=0.3" if e[2]["kind"] else "arc3,rad=0"
            color = "0.5" if e[2]["kind"] else "0"
            linestyle = "--" if e[2]["kind"] else "-"
            # if e[2]["kind"]:
            #     continue
            ax.annotate(
                "",
                xy=e[0], xycoords='data',
                xytext=e[1], textcoords='data',
                arrowprops=dict(
                    arrowstyle="<-", color=color,
                    shrinkA=0, shrinkB=0,
                    patchA=None, patchB=None,
                    connectionstyle=connectionstyle,
                    linestyle = linestyle
                ),
            )

        ax.set_aspect('equal', 'box')
    
    def plot(self, ax):
        pos = {point: point for point in self.graph.nodes}
        
        nx.draw_networkx_nodes(self.graph, pos, ax=ax, node_color = 'r', node_size = 10, alpha = 1)
        
        for e in self.graph.edges.data():
            connectionstyle = "arc3,rad=0.3" if e[2]["kind"] else "arc3,rad=0"
            color = "0.5" if e[2]["kind"] else "0"
            linestyle = "--" if e[2]["kind"] else "-"
            ax.annotate(
                "",
                xy=e[0], xycoords='data',
                xytext=e[1], textcoords='data',
                arrowprops=dict(
                    arrowstyle="-", color=color,
                    shrinkA=0, shrinkB=0,
                    patchA=None, patchB=None,
                    connectionstyle=connectionstyle,
                    linestyle = linestyle
                ),
            )

        ax.set_aspect('equal', 'box')
        ax.axis('off')

    def get_plot_comb_num(self):
        return [str(i) for i in range(len(self.cycle_comb_list))]

    def plot_comb(self, index, fig):
        ax = fig.add_subplot(111, projection='3d')
        cycles = self.cycle_comb_list[index]
        # Plot each Hamiltonian cycle
        for i, cycle in enumerate(cycles):
            z_coords = [i, i]
            for (node1, node2) in tuple(zip(cycle[:-1], cycle[1:])):
                if(self.graph.get_edge_data(node1, node2)['kind'] == 0):
                    ax.plot((node1[0], node2[0]), (node1[1], node2[1]), z_coords, color="blue")

        # Set equal aspect
        set_equal_aspect(ax)

        # Labels and legend
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Layers')
