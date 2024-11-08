import math
import pyclipper

SCALING_FACTOR = 1000

def offset(paths, amount):
    """
        Offset a set of paths by a specified amount using the pyclipper library.

        Parameters:
        - paths (list of list of tuples): Input paths where each path is represented as a list of (x, y) tuples.
        - amount (float or int): The amount by which the paths are to be offset.

        Returns:
        - list of list of tuples: Resulting paths after the offset operation.

        Notes:
        - The function assumes that the input paths might not be in the clipper scale. Therefore, it scales the input paths
          to the clipper scale using `pyclipper.scale_to_clipper` and then scales the resulting paths back from the clipper scale.
        - The ArcTolerance property is set to control the maximum deviation from true arcs for arc approximation. This is set as
          the SCALING_FACTOR divided by 40.
        - The offset operation uses the 'JT_SQUARE' join type and assumes paths are closed polygons with 'ET_CLOSEDPOLYGON'.
        - The given offset amount is also scaled using the SCALING_FACTOR for accurate offsetting in the clipper scale.
    """
    pco = pyclipper.PyclipperOffset()
    pco.ArcTolerance = SCALING_FACTOR / 40
    paths = pyclipper.scale_to_clipper(paths, SCALING_FACTOR)
    pco.AddPaths(paths, pyclipper.JT_SQUARE, pyclipper.ET_CLOSEDPOLYGON)
    outpaths = pco.Execute(amount * SCALING_FACTOR)
    outpaths = pyclipper.scale_from_clipper(outpaths, SCALING_FACTOR)
    return outpaths


def union(paths1, paths2):
    """
    Perform a union operation between two sets of paths using the pyclipper library.
    Parameters:
    - paths1 (list of list of tuples): First set of paths. Each path is represented as a list of (x, y) tuples.
    - paths2 (list of list of tuples): Second set of paths.

    Returns:
    - list of list of tuples: Resulting paths after the union operation.

    Notes:
    - If either paths1 or paths2 is empty, the function will return the other path.
    - The function assumes that the input paths might not be in the clipper scale. Therefore, it scales the input paths
    to the clipper scale using `pyclipper.scale_to_clipper` and then scales the resulting paths back from the clipper scale.
    - A ClipperException is raised if any path in paths1 or paths2 starts with a tuple containing an int or a float.
    This check seems to be in place to ensure that paths contain valid point tuples.
    - If the union operation fails for some reason, the function prints the scaled paths1 and paths2 for debugging purposes.

    Raises:
    - pyclipper.ClipperException: If the initial point of either paths1 or paths2 contains just an int or float.
    """
    if not paths1:
        return paths2
    if not paths2:
        return paths1
    pc = pyclipper.Pyclipper()
    if paths1:
        if paths1[0][0] in (int, float):
            raise pyclipper.ClipperException()
        paths1 = pyclipper.scale_to_clipper(paths1, SCALING_FACTOR)
        pc.AddPaths(paths1, pyclipper.PT_SUBJECT, True)
    if paths2:
        if paths2[0][0] in (int, float):
            raise pyclipper.ClipperException()
        paths2 = pyclipper.scale_to_clipper(paths2, SCALING_FACTOR)
        pc.AddPaths(paths2, pyclipper.PT_CLIP, True)
    try:
        out_paths = pc.Execute(pyclipper.CT_UNION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
    except:
        print("paths1={}".format(paths1))
        print("paths2={}".format(paths2))
    out_paths = pyclipper.scale_from_clipper(out_paths, SCALING_FACTOR)
    return out_paths

#  computes the difference between two sets of paths (polygons or polylines) using the Pyclipper library, 
# returning the paths that are in the subject but not in the clipping paths
def diff(subj, clip_paths, subj_closed=True):
    """
    Compute the difference between a set of subject paths and clipping paths. The difference operation, in this context,
    means subtracting the area covered by the clipping paths from the subject paths, resulting in paths that represent
    the parts of the subject that are outside the clipping paths.

    Parameters:
    - subj (list of list of tuples): The subject paths, each represented as a list of (x, y) tuples.
        This is the main shape or set of shapes you start with.
    - clip_paths (list of list of tuples): The clipping paths, each represented as a list of (x, y) tuples.
        These paths define the areas you want to subtract from the subject.
    - subj_closed (bool, optional): Specifies if the subject paths are closed polygons. Default is True.

    Returns:
    - list of list of tuples: Paths that represent the portions of the subject paths that remain after subtracting
        the areas covered by the clipping paths.

    Notes:
    - If `subj` is empty, the function returns an empty list because there's nothing to subtract from.
    - If `clip_paths` is empty, the function returns the entire `subj` because there's no clipping path to subtract.
    - To ensure compatibility with the `pyclipper` library, which operates in a different coordinate scale,
        both the subject and clipping paths are scaled using `pyclipper.scale_to_clipper` before performing the operation.
        The resulting paths are then scaled back to the original scale using `pyclipper.scale_from_clipper`.
    - The `pyclipper.Pyclipper` object (`pc`) is instantiated to manage and execute the clipping operations.
    - `pc.AddPaths` adds paths to this object, designating them as either subject or clipping paths.
    - The actual difference operation is performed using `pc.Execute` with the `CT_DIFFERENCE` operation type, which
        calculates the areas of the subject paths that are not overlapped by the clipping paths.
    - The even-odd fill type (`PFT_EVENODD`) is used for both subject and clipping paths. This rule determines
        the "insideness" of a point in a polygon by drawing a ray from the point to infinity in any direction and
        counting the number of path segments from the given shape that the ray crosses.
    """
    if not subj:
        return []
    if not clip_paths:
        return subj
    pc = pyclipper.Pyclipper()
    if subj:
        subj = pyclipper.scale_to_clipper(subj, SCALING_FACTOR)
        pc.AddPaths(subj, pyclipper.PT_SUBJECT, subj_closed)
    if clip_paths:
        clip_paths = pyclipper.scale_to_clipper(clip_paths, SCALING_FACTOR)
        pc.AddPaths(clip_paths, pyclipper.PT_CLIP, True)
    outpaths = pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
    outpaths = pyclipper.scale_from_clipper(outpaths, SCALING_FACTOR)
    return outpaths


def clip(subj, clip_paths, subj_closed=True):
    """
    Perform a clipping operation on a set of subject paths using the provided clipping paths. Clipping, in this context,
    refers to the process of finding the areas of overlap (intersection) between the subject paths and the clipping paths.
    The output consists only of those portions of the subject paths that lie inside the clipping paths.

    Parameters:
    - subj (list of list of tuples): The subject paths where each path is represented as a list of (x, y) tuples.
    - clip_paths (list of list of tuples): The clipping paths which define the areas to be used to clip the subject paths.
    - subj_closed (bool, optional): Specifies if the subject paths are closed. Default is True.

    Returns:
    - list of list of tuples: The resulting paths after the clipping operation.

    Notes:
    - If either subj or clip_paths is empty, the function returns an empty list.
    - The function scales the input paths to the clipper scale using `pyclipper.scale_to_clipper` and scales the resulting paths
        back from the clipper scale using `pyclipper.scale_from_clipper`.
    - The `Execute2` method is used to perform the clipping operation, which retrieves the results as a PolyTree.
    The `PolyTreeToPaths` method then converts this PolyTree into a list of paths.
    - It's assumed that both the subject and clip paths should be processed with even-odd fill type (`PFT_EVENODD`).
    """
    if not subj:
        return []
    if not clip_paths:
        return []
    pc = pyclipper.Pyclipper()
    if subj:
        subj = pyclipper.scale_to_clipper(subj, SCALING_FACTOR)
        pc.AddPaths(subj, pyclipper.PT_SUBJECT, subj_closed)
    if clip_paths:
        clip_paths = pyclipper.scale_to_clipper(clip_paths, SCALING_FACTOR)
        pc.AddPaths(clip_paths, pyclipper.PT_CLIP, True)
    out_tree = pc.Execute2(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
    out_paths = pyclipper.PolyTreeToPaths(out_tree)
    out_paths = pyclipper.scale_from_clipper(out_paths, SCALING_FACTOR)
    return out_paths


def paths_contain(pt, paths):
    """
    Check if a given point lies inside any of the provided paths.

    Parameters:
    - pt (tuple): The point to check, represented as an (x, y) tuple.
    - paths (list of list of tuples): The paths against which the point's position is checked. Each path is a
     list of (x, y) tuples.

    Returns:
    - bool: True if the point lies inside any of the paths, False otherwise.

    Notes:
    - The function uses the winding number rule: If the winding number is zero, the point lies outside the path.
    Otherwise, it lies inside.
    - Both the point and paths are scaled to the clipper scale using `pyclipper.scale_to_clipper` before checking.
    - The function maintains a count `cnt` that is toggled every time the point is found inside a path.
      If `cnt` is odd at the end, the point lies inside an odd number of paths, indicating it's inside the overall
      structure formed by the paths.
      If `cnt` is even, it lies outside or is contained within an even number of nested paths, indicating it's outside
      the overall structure.
    """
    cnt = 0
    pt = pyclipper.scale_to_clipper([pt], SCALING_FACTOR)[0]
    for path in paths:
        path = pyclipper.scale_to_clipper(path, SCALING_FACTOR)
        if pyclipper.PointInPolygon(pt, path):
            cnt = 1 - cnt
    return cnt % 2 != 0


def orient_path(path, dir):
    """
    Ensure the orientation of a given path matches the specified direction.

    Parameters:
    - path (list of tuples): The path to orient, represented as a list of (x, y) tuples.
    - dir (bool): The desired orientation of the path. True for clockwise, False for counter-clockwise.

    Returns:
    - list of tuples: The oriented path.

    Notes:
    - The function checks the current orientation of the path using `pyclipper.Orientation`.
    - If the current orientation doesn't match the desired direction (`dir`), the path is reversed.
    - To ensure compatibility with the `pyclipper` library, the path is scaled using `pyclipper.scale_to_clipper`
          before checking its orientation and reversing. The oriented path is then scaled back to the original scale
          using `pyclipper.scale_from_clipper`.
    """

    orient = pyclipper.Orientation(path)
    path = pyclipper.scale_to_clipper(path, SCALING_FACTOR)
    if orient != dir:
        path = pyclipper.ReversePath(path)
    path = pyclipper.scale_from_clipper(path, SCALING_FACTOR)
    return path


def orient_paths(paths):
    """
    Ensure the orientation of each path in a list of paths is consistent based on its position relative to the other
    paths.

    Parameters:
    - paths (list of list of tuples): The paths to orient. Each path is represented as a list of (x, y) tuples.

    Returns:
    - list of list of tuples: The oriented paths.

    Notes:
    - The function processes each path in the input `paths` list:
          * The orientation for each path is determined based on whether the path lies inside any of the other paths.
          * If a path lies inside another path, its orientation should be opposite to the containing path.
    - The `orient_path` function is used to actually adjust the orientation of each individual path based on the
    determined direction.
    - The `paths_contain` function checks if the first point of the current path lies inside any of the other paths
          to determine the desired orientation.
    """
    out = []
    while paths:
        path = paths.pop(0)
        path = orient_path(path, not paths_contain(path[0], paths))
        out.append(path)
    return out


def paths_bounds(paths):
    """
    Compute the bounding box (rectangular bounds) for a list of paths.
    Parameters:
    - paths (list of list of tuples): A list of paths where each path is represented as a list of (x, y) tuples.
    Returns:
    - tuple: A tuple (minx, miny, maxx, maxy) representing the bounding box of the provided paths.
    Notes:
    - If the input paths list is empty, the function returns a bounding box with all values set to 0.
    """
    if not paths:
        return (0, 0, 0, 0)
    minx, miny = (None, None)
    maxx, maxy = (None, None)
    for path in paths:
        for x, y in path:
            if minx is None or x < minx:
                minx = x
            if maxx is None or x > maxx:
                maxx = x
            if miny is None or y < miny:
                miny = y
            if maxy is None or y > maxy:
                maxy = y
    bounds = (minx, miny, maxx, maxy)
    return bounds


def close_path(path):
    """
    Ensure a path is closed by appending its starting point to the end if not already done.

    Parameters:
    - path (list of tuples): The path represented as a list of (x, y) tuples.

    Returns:
    - list of tuples: The possibly closed path.
    """
    if not path:
        return path
    if path[0] == path[-1]:
        return path
    return path + path[0:1]


def close_paths(paths):
    """
    Ensure that each path in a list of paths is closed.
    Parameters:
    - paths (list of list of tuples): A list of paths where each path is represented as a list of (x, y) tuples.
    Returns:
    - list of list of tuples: A list of closed paths.
    """
    return [close_path(path) for path in paths]


############################################################


def make_infill_pat(rect, baseang, spacing, rots):
    """
    Generate infill patterns (lines) within a specified rectangle based on given angles and spacing.

    Parameters:
    - rect (list): A bounding rectangle specified as (minx, miny, maxx, maxy).
    - baseang (float): The base angle for the infill lines in degrees.
    - spacing (float): The distance between infill lines.
    - rots (list of floats): A list of angles to rotate the base infill pattern.

    Returns:
    - list of list of tuples: A list of infill paths.
    """
    minx, miny, maxx, maxy = rect
    w = maxx - minx
    h = maxy - miny
    cx = math.floor((maxx + minx)/2.0/spacing)*spacing
    cy = math.floor((maxy + miny)/2.0/spacing)*spacing
    r = math.hypot(w, h) / math.sqrt(2)
    n = int(math.ceil(r / spacing))
    out = []
    for rot in rots:
        c1 = math.cos((baseang+rot)*math.pi/180.0)
        s1 = math.sin((baseang+rot)*math.pi/180.0)
        c2 = math.cos((baseang+rot+90)*math.pi/180.0) * spacing
        s2 = math.sin((baseang+rot+90)*math.pi/180.0) * spacing
        for i in range(1-n, n):
            cp = (cx + c2 * i, cy + s2 * i)
            line = [
                (cp[0] + r * c1, cp[1] + r * s1),
                (cp[0] - r * c1, cp[1] - r * s1)
            ]
            out.append( line )
    return out


def make_infill_lines(rect, base_ang, density, ewidth):
    """
    Generate infill lines pattern within a specified rectangle.

    Parameters:
    - rect, base_ang, density, ewidth are inputs defining the bounding box, orientation, density, and width of infill.

    Returns:
    - list of list of tuples: A list of infill paths formed by lines.
    """
    if density <= 0.0:
        return []
    if density > 1.0:
        density = 1.0
    spacing = ewidth / density
    return make_infill_pat(rect, base_ang, spacing, [0])
