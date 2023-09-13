import numpy as np
import pyvista as pv

from .sensor import Sensor
from environment import grid_helpers as helpers


# this class is a child class of sensor and models the lidar
class Lidar(Sensor):
    def __init__(self, position, fov_h, fov_v, detection_range, min_range, name):
        super().__init__(position, name)
        self.fov_h = fov_h
        self.fov_v = fov_v
        self.max_dist = detection_range
        self.min_range = min_range
        self.points = np.array(
            [
                [self.max_dist, self.fov_h / 2, self.fov_v / 2],
                [self.max_dist, -self.fov_h / 2, self.fov_v / 2],
                [self.max_dist, -self.fov_h / 2, -self.fov_v / 2],
                [self.max_dist, self.fov_h / 2, -self.fov_v / 2],
            ]
        )
        self.points = helpers.calculate_cart_from_sph(self.points)
        self.points += np.tile(self.position, (4, 1))
        self.__create_mesh()

    # private function to create a mesh that can be used for visualization, but doesn't have a purpose apart from that
    def __create_mesh(self):
        # create part of a pyvista sphere
        start_theta = 360 - self.fov_h / 2 if self.fov_h != 360 else 0
        end_theta = self.fov_h / 2 if self.fov_h != 360 else 360
        start_phi = 90 - self.fov_v / 2
        end_phi = 90 + self.fov_v / 2
        self.mesh = pv.Sphere(
            radius=self.max_dist,
            center=self.position,
            start_theta=start_theta,
            end_theta=end_theta,
            start_phi=start_phi,
            end_phi=end_phi,
        )
        # add lines from the edges to the sensor origin
        line1 = pv.Line(self.points[0], self.position)
        line2 = pv.Line(self.points[1], self.position)
        line3 = pv.Line(self.points[2], self.position)
        line4 = pv.Line(self.points[3], self.position)
        self.mesh += line1 + line2 + line3 + line4

    # private function to compute the points inside the fov of the lidar. takes a point matrix of shape nx3 as input
    def __is_inside_matrix(self, points_matrix):
        # get the vectors from the sensor position to the points and the transformation matrix to local coordinates
        sensor_position_matrix = np.tile(self.position, (points_matrix.shape[0], 1))
        vectors = points_matrix - sensor_position_matrix
        transf_matrix = np.transpose(self.coordinate_system)

        # transform vectors to local coordinates and translate to spherical coordinates
        vectors = np.matmul(transf_matrix, np.transpose(vectors))
        vectors = helpers.calculate_sph_from_cart(np.transpose(vectors))
        vectors_sph = np.absolute(vectors)

        # check, whether the points fulfill conditions for being inside the fov and assemble conditions to a matrix
        dist = np.logical_and(
            vectors_sph[:, 0] <= self.max_dist, vectors_sph[:, 0] >= self.min_range
        )
        theta = vectors_sph[:, 1] <= self.fov_h / 2
        phi = vectors_sph[:, 2] <= self.fov_v / 2
        vectors_bool = np.vstack((dist, theta, phi))

        # the point is inside, if the corresponding row contains only true. this is checked here
        self.calculation_result = np.all(vectors_bool, axis=0)
        self.covered_indices = np.nonzero(self.calculation_result)[0]
        self.covered_points = np.take(points_matrix, self.covered_indices, axis=0)

    # function that is called by the main program to compute the lidar coverage and set the metrics
    def calculate_coverage(self, grid, occlusion_mesh, indexes=None, all_metrics=True):
        self.__is_inside_matrix(grid.calc_points)
        self.is_occluded_matrix(occlusion_mesh)
        self.covered_indices = np.nonzero(self.calculation_result)[0]
        self.covered_points = np.take(grid.calc_points, self.covered_indices, axis=0)
        self.number_covered_points = self.covered_indices.size

        self.set_metrics(grid, indexes, all_metrics)
