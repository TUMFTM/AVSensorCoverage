import math
import numpy as np

# this file contains helper functions that are used by different classes


# function that calculates the width of a cameras fov
def calculate_width(max_dist, fov):
    angle = math.radians(fov)
    width = 2 * max_dist * math.tan(angle / 2)
    return width


# function that calculates the 4 points of a plane given the center, a distance, width and height
def calculate_plane_points(apex, dist, width, height):
    p1 = np.array(apex)
    x = p1[0]
    y = p1[1]
    z = p1[2]
    p2 = np.array([x + dist, y - (width / 2), z - (height / 2)])
    p3 = np.array([x + dist, y - (width / 2), z + (height / 2)])
    p4 = np.array([x + dist, y + (width / 2), z + (height / 2)])
    p5 = np.array([x + dist, y + (width / 2), z - (height / 2)])
    points = np.array([p2, p3, p4, p5])
    return points


# function that calculates all the points for the mesh of a cameras fov
def get_points(apex, max_dist, min_dist, width, height, fov, aspect_ratio):
    if min_dist == 0:
        p1 = np.array(apex)
        points = np.vstack((p1, calculate_plane_points(apex, max_dist, width, height)))
        return points
    else:
        width_near = calculate_width(min_dist, fov)
        height_near = width_near / aspect_ratio
        far_points = calculate_plane_points(apex, max_dist, width, height)
        near_points = calculate_plane_points(apex, min_dist, width_near, height_near)
        points = np.vstack((far_points, near_points))
        return points


# function that defines the faces of the viewing frustum by using indexes of the point list
def get_faces(min_dist):
    if min_dist == 0:
        faces = np.hstack(
            [[4, 1, 2, 3, 4], [3, 0, 1, 2], [3, 0, 2, 3], [3, 0, 3, 4], [3, 0, 4, 1]]
        )
        return faces
    else:
        faces = np.hstack(
            [
                [4, 0, 1, 2, 3],
                [4, 0, 1, 5, 4],
                [4, 1, 2, 6, 5],
                [4, 2, 3, 7, 6],
                [4, 0, 3, 7, 4],
                [4, 4, 5, 6, 7],
            ]
        )
        return faces


# function that translates from cartesian to spherical coordinates. points has to be a nx3 matrix. angular output is in
# degrees
def calculate_sph_from_cart(points):
    new_points = np.zeros(points.shape)
    xy_sq = points[:, 0] ** 2 + points[:, 1] ** 2
    new_points[:, 0] = np.sqrt(xy_sq + points[:, 2] ** 2)
    new_points[:, 2] = np.degrees(np.arctan2(points[:, 2], np.sqrt(xy_sq)))
    new_points[:, 1] = np.degrees(np.arctan2(points[:, 1], points[:, 0]))
    return new_points


# function that translates from spherical to cartesian coordinates. points has to be a nx3 matrix and angles in degrees
def calculate_cart_from_sph(points):
    new_points = np.zeros(points.shape)
    theta = np.radians(points[:, 1])
    phi = np.radians(points[:, 2])
    new_points[:, 2] = points[:, 0] * np.sin(phi)
    new_points[:, 1] = points[:, 0] * np.sin(theta) * np.cos(phi)
    new_points[:, 0] = points[:, 0] * np.cos(theta) * np.cos(phi)
    return new_points


# function that translates from cartesian to cylindrical coordinates. points has to be a nx3 matrix. angular output is
# in degrees
def calculate_cyl_from_cart(points):
    new_points = np.zeros(points.shape)
    phi = np.degrees(np.arctan2(points[:, 1], points[:, 0]))
    r = np.sqrt(points[:, 0] ** 2 + points[:, 1] ** 2)
    new_points[:, 0] = r
    new_points[:, 1] = phi
    new_points[:, 2] = points[:, 2]
    return new_points


# function that determines, which indices of a given point matrix lie within and which lie without a rectangular
# bounding box. the bounding box is defined by the bounds (xmin, xmax, ymin, ymax, zmin, zmax)
def get_bounding_box_indices(points, bounds):
    x = np.logical_and(points[:, 0] >= bounds[0], points[:, 0] <= bounds[1])
    y = np.logical_and(points[:, 1] >= bounds[2], points[:, 1] <= bounds[3])
    z = np.logical_and(points[:, 2] >= bounds[4], points[:, 2] <= bounds[5])
    points_bool = np.vstack((x, y, z))

    bounding_box_indices = np.nonzero(np.all(points_bool, axis=0))[0]
    outside_indices = np.nonzero(np.all(points_bool, axis=0) == 0)[0]
    outside_indices = np.reshape(outside_indices, (outside_indices.size, 1))

    return bounding_box_indices, outside_indices
