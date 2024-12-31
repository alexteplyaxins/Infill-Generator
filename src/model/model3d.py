from __future__ import print_function

import os.path
import sys
import math
import struct
import re
import matplotlib

from model.point3d import Point3DCache
from model.vector import Vector
from model.facet3d import Facet3DCache
from model.line_segment3d import LineSegment3DCache


def list_methods(obj):
   return [method_name for method_name in dir(obj) if callable(getattr(obj, method_name))]


class ModelEndOfFileException(Exception):
    """Exception class for reaching the end of the STL file while reading."""
    pass


class ModelMalformedLineException(Exception):
    """Exception class for malformed lines in the STL file being read."""
    pass


class ModelData(object):
    """Class to read, write, and validate STL, OBJ, AMF, 3MF, 3MJ file data."""

    def __init__(self):
        """Initialize with empty data set."""
        self.points = Point3DCache()
        self.edges = LineSegment3DCache()
        self.facets = Facet3DCache()
        self.filename = ""
        self.dupe_faces = []
        self.dupe_edges = []
        self.hole_edges = []
        self.layer_facets = {}

    def _read_stl_ascii_line(self, line, watchwords=None):
        if line == "":
            raise ModelEndOfFileException()
        words = line.strip(' \t\n\r').lower().split()
        if not words:
            return []
        if words[0] == 'endsolid':
            raise ModelEndOfFileException()
        argstart = 0
        if watchwords:
            watchwords = watchwords.lower().split()
            argstart = len(watchwords)
            for i in range(argstart):
                if words[i] != watchwords[i]:
                    raise ModelMalformedLineException()
        return [float(val) for val in words[argstart:]]

    def _read_stl_ascii_vertex(self, line):
        point = self._read_stl_ascii_line(line, watchwords='vertex')
        return self.points.add(*point)

    def quantz(self, pt, quanta=1e-3):
        """Quantize the Z coordinate of the given point so that it won't be exactly on a layer."""
        x, y, z = pt
        z = math.floor(z / quanta + 0.5) * quanta
        return (x, y, z)

    def _add_facet(self,v1,v2,v3,quanta=1e-3):
       normal = Vector(0,0,0)             # -- create a dummy
       #print(v1,v2,v3)
       if quanta > 0.0:                   
          v1 = self.quantz(v1, quanta)
          v2 = self.quantz(v2, quanta)
          v3 = self.quantz(v3, quanta)
          if v1 == v2 or v2 == v3 or v3 == v1:
              return        # zero area facet.  Skip to next facet.
          vec1 = Vector(v1) - Vector(v2)
          vec2 = Vector(v3) - Vector(v2)
          if vec1.angle(vec2) < 1e-8:
              return        # zero area facet.  Skip to next facet.
       v1 = self.points.add(*v1)
       v2 = self.points.add(*v2)
       v3 = self.points.add(*v3)
       self.edges.add(v1,v2)
       self.edges.add(v2,v3)
       self.edges.add(v3,v1)
       self.facets.add(v1,v2,v3,normal)

    def _read_stl_ascii_facet(self, f, quanta=1e-3):
        vertex = []
        i = 0
        lines = f.readlines()
        for line in lines:
            i = i+1
            line = line.decode('utf-8')
            if 'endloop' in line or 'endfacet' in line:
                vertex.clear()
            if 'facet normal' in line:
                normal = self._read_stl_ascii_line(line, watchwords='facet normal')
            if  'outer loop' in line:
                self._read_stl_ascii_line(line, watchwords='outer loop')
            if 'vertex' in line:
                vertex.append(self._read_stl_ascii_vertex(line))
            # self._read_stl_ascii_line(f, watchwords='endloop')
            # self._read_stl_ascii_line(f, watchwords='endfacet')
            if len(vertex)==3:
                if quanta > 0.0:
                    for i in range(3):
                        vertex[i] = self.quantz(vertex[i], quanta)
                    if vertex[0] == vertex[1] or vertex[1] == vertex[2] or vertex[2] == vertex[0]:
                        continue  # zero area facet.  Skip to next facet.
                    vec1 = Vector(vertex[0]) - Vector(vertex[1])
                    vec2 = Vector(vertex[2]) - Vector(vertex[1])
                    if vec1.angle(vec2) < 1e-8:
                        continue  # zero area facet.  Skip to next facet.
                    self.edges.add(vertex[0], vertex[1])
                    self.edges.add(vertex[1], vertex[2])
                    self.edges.add(vertex[2], vertex[0])
                self.facets.add(vertex[0], vertex[1], vertex[2], normal)
              #  print(self.facets)
        return self.facets

    def _read_stl_binary_facet(self, f, quanta=1e-3):
        data = struct.unpack('<3f 3f 3f 3f H', f.read(4*4*3+2))
        normal = data[0:3]
        vertex1 = data[3:6]
        vertex2 = data[6:9]
        vertex3 = data[9:12]
        if quanta > 0.0:
            vertex1 = self.quantz(vertex1, quanta)
            vertex2 = self.quantz(vertex2, quanta)
            vertex3 = self.quantz(vertex3, quanta)
            if vertex1 == vertex2 or vertex2 == vertex3 or vertex3 == vertex1:
                return None
            vec1 = Vector(vertex1) - Vector(vertex2)
            vec2 = Vector(vertex3) - Vector(vertex2)
            if vec1.angle(vec2) < 1e-8:
                return None
        v1 = self.points.add(*vertex1)
        v2 = self.points.add(*vertex2)
        v3 = self.points.add(*vertex3)
        self.edges.add(v1, v2)
        self.edges.add(v2, v3)
        self.edges.add(v3, v1)
        return self.facets.add(v1, v2, v3, normal)

    def read_file(self, filename):
        """Read the model data from the given STL, OBJ, OFF, 3MF, AMF, 3MJ file."""
        self.filename = filename
        print("Loading model \"{}\"".format(filename))
        file_size = os.path.getsize(filename)
        ext = re.search(r'\.(\w+)$',filename)
        if ext and ext[1]:
           ext = ext[1].lower()
        else:
          sys.exit(f"ERROR: could not extract file extension to determine file-format <{filename}>, abort")
        if ext == "stl": 
            with open(filename, 'rb') as f:         # -- STL
                line = f.readline(80)
                if line == "":
                   return  # End of file.
                if line[0:6].lower() == b"solid " and len(line) < 80:
                   # Reading ASCII STL file.
                    print("ascii")
                    self._read_stl_ascii_facet(f)
                else:
                   # Reading Binary STL file.
                    chunk = f.read(4)
                    facets = struct.unpack('<I', chunk)[0]
                    print("binary")
                    for n in range(facets):
                        if self._read_stl_binary_facet(f) is None:
                           pass
    
        elif ext == "3mj":           # -- 3MJ
           self._read_3MJ(filename)
        elif ext == "off":           # -- OFF
           self._read_OFF(filename)
        elif ext == "obj":           # -- OBJ
           self._read_OBJ(filename)
        elif ext == "3mf" or ext=="3mfm":  # -- 3MF/3MFM
           self._read_3MF(filename)
        elif ext == "amf":           # -- AMF
           self._read_AMF(filename)
        elif ext == "ply":           # -- PLY
           self._read_PLY(filename)
        else:
            sys.exit(f"ERROR: file-format not supported to import <{filename}>, only STL, OBJ, OFF, 3MF/3MFM, 3MJ, AMF")
            
    def _read_OBJ(self,fn):                 # -- wavefront .obj
        fh = open(fn,"r")
        ps = []
        while 1:
            l = fh.readline()                               # -- we parse line-wise
            if not l:
                break
            if re.search('^v ',l):                          # -- v <x> <y> <z> (coordinate)
                vs = l.split()
                vs.pop(0)
                ps.append([float(x) for x in vs])
            elif re.search('^f ',l):                        # -- f <i0> <i1> <i2> (face)
                fs = l.split()
                fs.pop(0)
                fs = [re.sub('/.*','',x) for x in fs]       # -- remove all /...
                f = [int(x)-1 for x in fs]                  # -- indices start with 1 => start with 0
                self._add_facet(ps[f[0]],ps[f[1]],ps[f[2]])
            else:
                """we ignore anything else silently"""

    def _write_stl_ascii_file(self, filename):
        with open(filename, 'wb') as f:
            f.write(b"solid Model\n")
            for facet in self.facets.sorted():
                f.write(
                    "  facet normal {norm:s}\n"
                    "    outer loop\n"
                    "      vertex {v0:s}\n"
                    "      vertex {v1:s}\n"
                    "      vertex {v2:s}\n"
                    "    endloop\n"
                    "  endfacet\n"
                    .format(
                        v0=facet[0],
                        v1=facet[1],
                        v2=facet[2],
                        norm=facet.norm
                    )
                    .encode('utf-8')
                )
            f.write(b"endsolid Model\n")

    def _write_stl_binary_file(self, filename):
        with open(filename, 'wb') as f:
            f.write('{0:-80s}'.format('Binary STL Model'))
            f.write(struct.pack('<I', len(self.facets)))
            for facet in self.facets.sorted():
                f.write(struct.pack(
                    '<3f 3f 3f 3f H',
                    facet.norm[0], facet.norm[1], facet.norm[2],
                    facet[0][0], facet[0][1], facet[0][2],
                    facet[1][0], facet[1][1], facet[1][2],
                    facet[2][0], facet[2][1], facet[2][2],
                    0
                ))

    def write_file(self, filename, binary=False):
        """Write the model data to an STL, OFF, OBJ, 3MF, 3MJ file."""
        if filename.search("\.stl$",filename,re.IGNORECASE):
           if binary:
               self._write_stl_binary_file(filename)
           else:
               self._write_stl_ascii_file(filename)
        elif filename.search("\.3mj$",filename,re.IGNORECASE):
            self._write_3mj(filename)
        else:
            sys.exit(f"ERR: file-format not supported to export <%s>", filename)
            
    def _check_manifold_duplicate_faces(self):
        return [facet for facet in self.facets if facet.count != 1]

    def _check_manifold_hole_edges(self):
        return [edge for edge in self.edges if edge.count == 1]

    def _check_manifold_excess_edges(self):
        return [edge for edge in self.edges if edge.count > 2]

    def check_manifold(self, verbose=False):
        """Validate if the model is manifold, and therefore printable."""
        is_manifold = True
        self.dupe_faces = self._check_manifold_duplicate_faces()
        for face in self.dupe_faces:
            is_manifold = False
            print("WARN: NON-MANIFOLD DUPLICATE FACE! {0}: {1}"
                  .format(self.filename, face))
        self.hole_edges = self._check_manifold_hole_edges()
        for edge in self.hole_edges:
            is_manifold = False
            print("WARN: NON-MANIFOLD HOLE EDGE! {0}: {1}"
                  .format(self.filename, edge))
        self.dupe_edges = self._check_manifold_excess_edges()
        for edge in self.dupe_edges:
            is_manifold = False
            print("WARN: NON-MANIFOLD DUPLICATE EDGE! {0}: {1}"
                  .format(self.filename, edge))
        return is_manifold

    def get_facets(self):
        return self.facets

    def get_edges(self):
        return self.edges

    def center(self, cp):
        """Centers the model at the given centerpoint cp."""
        cx = (self.points.minx + self.points.maxx)/2.0
        cy = (self.points.miny + self.points.maxy)/2.0
        cz = (self.points.minz + self.points.maxz)/2.0
        self.translate((cp[0]-cx, cp[1]-cy, cp[2]-cz))
    
    def bounding_box(self):
        return [
            [self.points.minx, self.points.maxx],
            [self.points.miny, self.points.maxy],
            [self.points.minz, self.points.maxz]
            ]
    def translate(self, offset):
        """Translates vertices of all facets in the STL model."""
        self.points.translate(offset)
        self.edges.translate(offset)
        self.facets.translate(offset)

    def scale(self, scale): 
        """Scale vertices of all facets in the STL model."""
        self.points.scale(scale)
        self.edges.scale(scale)
        self.facets.scale(scale)
           
    def assign_layers(self, layer_height):
        """
        Calculate which layers intersect which facets, for faster lookup.
        Params:
            layer_height
        """
        self.layer_facets = {}
        for facet in self.facets:
            minz, maxz = facet.z_range()
            minl = int(math.floor(minz / layer_height + 0.01))
            maxl = int(math.ceil(maxz / layer_height - 0.01))
            for layer in range(minl, maxl + 1):
                if layer not in self.layer_facets:
                    self.layer_facets[layer] = []
                self.layer_facets[layer].append(facet)

    def get_layer_facets(self, layer):
        """Get all facets that intersect the given layer."""
        if layer not in self.layer_facets:
            return []
        return self.layer_facets[layer]
    def plot_data_model(self, ax: matplotlib.axes.Axes, size: tuple = (5, 5)):
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

    def slice_at_z(self, z, layer_h):
        """
        Parameters:
            z (float): The height at which to take the slice.
            layer_h (float): The layer height to determine the layer number.
        Returns:
            tuple: A tuple containing two lists:
                - outpaths (list): A list of complete paths (polygons) at the given Z level.
                - deadpaths (list): A list of incomplete paths (polygons) at the given Z level.
        Warns:
            Prints a warning message if there are incomplete polygons at the given Z level.
        Get paths outlines of where this model intersects the given Z level.
        """
        def ptkey(pt):
            return "{0:.5f}, {1:.5f}".format(pt[0], pt[1])
        
        layer = round(math.floor(z / layer_h + 0.5), 2)
        paths = {}
        
        for facet in self.get_layer_facets(layer):
            line = facet.slice_at_z(z)
            if line is None:
                continue
            path = list(line)
            key1 = ptkey(path[0])
            key2 = ptkey(path[-1])

            if key1 not in paths:
                paths[key1] = []
            paths[key1].append(path)

            if key2 not in paths:
                paths[key2] = []
            paths[key2].append(path)

        outpaths = []
        deadpaths = []
        while paths:
            key, path_list = paths.popitem()
            path = path_list.pop(0)
            if not path_list:
                del paths[key]

            while True:
                key1 = ptkey(path[0])
                key2 = ptkey(path[-1])

                if key1 == key2:
                    outpaths.append(path)
                    break

                if key2 in paths:
                    next_path = paths[key2].pop(0)
                    if not paths[key2]:
                        del paths[key2]
                    path.extend(next_path[1:])
                else:
                    deadpaths.append(path)
                    break

        if deadpaths:
            print(f'WARN: Incomplete Polygon at z={z}')

        return (outpaths, deadpaths)
