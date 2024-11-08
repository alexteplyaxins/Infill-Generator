import numpy as np
from numpy.linalg import norm, inv
import networkx as nx

# return whether the first line is intersected by the second line and return the intersection
def get_intersection(line1, line2):
    vec_a = np.array([line1[0], line1[1]])
    vec_b = np.array([line1[2], line1[3]])
    vec_c = np.array([line2[0], line2[1]])
    vec_d = np.array([line2[2], line2[3]])
    
    vec_ab = vec_b-vec_a
    vec_ac = vec_c-vec_a
    vec_ad = vec_d-vec_a
    vec_cd = vec_d-vec_c

    is_intersect = False
    intersection = set()
    if np.cross(vec_ac, vec_ad) == 0:
        if np.cross(vec_ab, vec_cd) == 0:
            if (np.dot(vec_ac, vec_ab)/norm(vec_ab) < norm(vec_ab)) and np.dot(vec_ac, vec_ab)>0:
                intersection.add(tuple(vec_c.tolist()))
            if (np.dot(vec_ad, vec_ab)/norm(vec_ab) < norm(vec_ab)) and np.dot(vec_ad, vec_ab)>0:
                intersection.add(tuple(vec_d.tolist()))
            if len(intersection)>0:
                is_intersect = True
    else:
        basis_mat = inv(np.vstack((vec_ac, vec_ad)).T)
        new_ab = np.matmul(basis_mat, vec_ab)
        
        is_intersect = (new_ab[0] >= 0) and (new_ab[1] >= 0) and (norm(new_ab, ord=1) > 1)
        if is_intersect:
            intersection.add(tuple((vec_ab/norm(new_ab, ord=1) + vec_a).tolist()))
    return (is_intersect, intersection)

# return the line segments seperated from a long segment with intersections
def dissolve_segment(segment, intersections):
    vec_a = (segment[0], segment[1])
    vec_b = (segment[2], segment[3])
    vec_ab = (segment[2]-segment[0], segment[3]-segment[1])
    intersections_list = list(point for point in intersections)
    
    if vec_a not in intersections_list:
        intersections_list.append(vec_a)
    if vec_b not in intersections_list:
        intersections_list.append(vec_b)

    intersections_list.sort(key=lambda x: np.dot(vec_ab, x))
    segments = []
    for i in range(1, len(intersections_list)):
        segments.append(
            (intersections_list[i-1][0], 
             intersections_list[i-1][1], 
             intersections_list[i][0], 
             intersections_list[i][1])
        )
    return set(segments)

def set_equal_aspect(ax):
    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    
    x_range = x_limits[1] - x_limits[0]
    y_range = y_limits[1] - y_limits[0]
    
    max_range = max(x_range, y_range)
    
    x_center = (x_limits[0] + x_limits[1]) / 2
    y_center = (y_limits[0] + y_limits[1]) / 2
    
    ax.set_xlim3d([x_center - max_range/2, x_center + max_range/2])
    ax.set_ylim3d([y_center - max_range/2, y_center + max_range/2])