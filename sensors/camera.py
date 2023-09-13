import numpy as np
import pyvista as pv

from .sensor import Sensor
from environment import grid_helpers as helpers


# this class is a child class of sensor and models a camera
class Camera(Sensor):
    def __init__(
        self, position, fov, max_dist, image_width, image_height, name, min_dist=0
    ):
        super().__init__(position, name)
        self.aspect_ratio = image_width / image_height
        self.max_dist = max_dist
        self.min_dist = min_dist
        self.fov = fov

        self.faces = None
        self.height = None
        self.width = None
        self.__create_mesh()

    # private function used to create the mesh of the camera. mesh is a pyvista polydata
    def __create_mesh(self):
        self.width = helpers.calculate_width(self.max_dist, self.fov)
        self.height = self.width / self.aspect_ratio
        self.faces = helpers.get_faces(self.min_dist)
        self.points = helpers.get_points(
            self.position,
            self.max_dist,
            self.min_dist,
            self.width,
            self.height,
            self.fov,
            self.aspect_ratio,
        )
        self.mesh = pv.PolyData(self.points, self.faces)

    # private function to compute the points inside the fov of the camera. takes a point matrix of shape nx3 as input
    def __is_inside_matrix(self, points_matrix):
        # get the vectors from the sensor position to the points and the side-facing normals of the fov
        sensor_position_matrix = np.tile(self.position, (points_matrix.shape[0], 1))
        difference_matrix = points_matrix - sensor_position_matrix
        face_normals = self.mesh.face_normals[1:5]
        face_normals_transposed = np.transpose(face_normals)

        # compute, whether points are inside the side faces of the fov
        dot_product = np.matmul(difference_matrix, face_normals_transposed)
        bool_dot_product = np.invert(np.any(dot_product <= 0, axis=1))

        # compute, whether points are within min and max range of the fov
        dist = np.matmul(difference_matrix, self.coordinate_system[:, 0])
        is_in_distance = np.logical_and(dist >= self.min_dist, dist <= self.max_dist)

        # combine the calculated boolean results to obtain points inside the fov
        self.calculation_result = bool_dot_product & is_in_distance
        self.covered_indices = np.nonzero(self.calculation_result)[0]
        self.covered_points = np.take(points_matrix, self.covered_indices, axis=0)

    # function that is called by the main program to compute the camera coverage and set the metrics
    def calculate_coverage(self, grid, occlusion_mesh, indexes=None, all_metrics=True):
        self.__is_inside_matrix(grid.calc_points)
        self.is_occluded_matrix(occlusion_mesh)
        self.covered_indices = np.nonzero(self.calculation_result)[0]
        self.covered_points = np.take(grid.calc_points, self.covered_indices, axis=0)
        self.number_covered_points = self.covered_indices.size

        self.set_metrics(grid, indexes, all_metrics)
