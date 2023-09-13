import numpy as np
from scipy.spatial.transform import Rotation as R


# this class contains generic sensor properties and functions that are used by every sensortype. it acts as a parent
# class for camera lidar and radar
class Sensor:
    def __init__(self, position, name):
        self.position = np.array(position)
        self.name = name
        self.points = None
        self.mesh = None
        self.calculation_result = None
        self.covered_points = None
        self.number_covered_points = None
        self.covered_indices = None
        self.occluded_points = None
        self.number_occluded_points = None
        self.occluded_indices = None
        self.coordinate_system = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        self.covered_volume = None
        self.occluded_volume = None
        self.metrics = np.zeros(shape=(18, 1))
        self.fraction_occluded = None

        # plot position is a parameter used in the automatic screenshot creation for every sensor.
        self.plot_position = np.zeros(3)
        if self.position[0] <= 0:
            self.plot_position[0] = self.position[0] - 5
        else:
            self.plot_position[0] = self.position[0] + 5
        if self.position[1] <= 0:
            self.plot_position[1] = self.position[1] - 5
        else:
            self.plot_position[1] = self.position[1] + 5

        self.plot_position[2] = self.position[2] + 5

    # function to rotate the sensor using pyvista functions. if local = false, rotation about global coordinate axis
    def rotate(self, local=True, pitch=0, yaw=0, roll=0):
        # rotate meshes
        if local:
            self.mesh = self.mesh.rotate_vector(
                self.coordinate_system[:, 1], pitch, self.position
            )
            self.mesh = self.mesh.rotate_vector(
                self.coordinate_system[:, 2], yaw, self.position
            )
            self.mesh = self.mesh.rotate_vector(
                self.coordinate_system[:, 0], roll, self.position
            )
        else:
            self.mesh = self.mesh.rotate_y(pitch, self.position)
            self.mesh = self.mesh.rotate_z(yaw, self.position)
            self.mesh = self.mesh.rotate_x(roll, self.position)

        # rotate local coordinate system
        r = R.from_euler("yzx", [pitch, yaw, roll], degrees=True)
        r = r.as_matrix()
        self.coordinate_system = np.matmul(self.coordinate_system, r)

    # function to translate the sensor using a pyvista function
    def translate(self, x=0, y=0, z=0):
        self.mesh = self.mesh.translate((x, y, z))
        self.position = np.array(
            [self.position[0] + x, self.position[1] + y, self.position[2] + z]
        )

    # private function, that checks whether a computed occlusion was correct. It does so by comparing the distance to
    # the occluded point with the distance to the hit point with the vehicle surface
    def __check_occlusion(self, rays, intersection_points, occluded_points):
        # get vectors to hit points and vectors to occluded points and compute length difference
        coll_vectors = intersection_points - np.tile(
            self.position, (np.size(intersection_points, 0), 1)
        )
        vectors = occluded_points - np.tile(
            self.position, (np.size(occluded_points, 0), 1)
        )
        length_coll = np.sqrt((coll_vectors * coll_vectors).sum(axis=1))
        length = np.sqrt((vectors * vectors).sum(axis=1))
        length_diff = length_coll - length

        # find indices, where distance to hit point was bigger than distance to occluded point and delete these indices
        # in rays
        wrong_indices = np.where(length_diff > 0)[0]
        rays = np.delete(rays, wrong_indices)

        return rays

    # callable function to determine the points that are occluded by the vehicle
    def is_occluded_matrix(self, occlusion_mesh):
        # get origins and directions for the ray trace
        origins = np.tile(self.position, (np.size(self.covered_points, 0), 1))
        direction_vectors = self.covered_points - origins

        # get the first points of intersection and index of the corresponding rays from the multi-ray-trace-function
        points, rays = occlusion_mesh.multi_ray_trace(
            origins, direction_vectors, first_point=True
        )[0:2]
        if rays.size != 0:
            # if any occlusions were found, verify them using the check_occlusion function
            occluded_points = self.covered_points[rays]
            rays = self.__check_occlusion(rays, points, occluded_points)
        occluded_indices = np.take(self.covered_indices, rays, axis=0)

        # set the values at the occluded indices in result to false
        result = np.full(self.calculation_result.size, True)
        np.put(result, occluded_indices, False)

        # save results of the calculation
        self.occluded_points = self.covered_points[rays]
        self.calculation_result = self.calculation_result & result
        self.occluded_indices = occluded_indices
        self.number_occluded_points = self.occluded_indices.size

    # function to set the sensor metrics, that is called after the calculation is done
    def set_metrics(self, grid, indexes=None, all_metrics=True):
        # calculate volume metrics
        cell_volume = grid.mesh.spacing[0] ** 3
        self.occluded_volume = round(self.occluded_indices.size * cell_volume, 2)
        self.covered_volume = round(self.covered_indices.size * cell_volume, 2)
        self.fraction_occluded = round(
            100 * self.occluded_volume / (self.covered_volume + self.occluded_volume), 1
        )

        if all_metrics:
            indexes = np.arange(18)

        # get the area indices to calculate the sensors performance in every area
        area_indices = None
        for index in indexes:
            data = self.__single_sensor_data(grid)
            match index:
                case 0:
                    area_indices = grid.far_front_left_indices
                case 1:
                    area_indices = grid.far_front_center_indices
                case 2:
                    area_indices = grid.far_front_right_indices
                case 3:
                    area_indices = grid.near_front_left_indices
                case 4:
                    area_indices = grid.near_front_center_indices
                case 5:
                    area_indices = grid.near_front_right_indices
                case 6:
                    area_indices = grid.far_left_indices
                case 7:
                    area_indices = grid.near_left_indices
                case 8:
                    area_indices = grid.near_right_indices
                case 9:
                    area_indices = grid.far_right_indices
                case 10:
                    area_indices = grid.near_rear_left_indices
                case 11:
                    area_indices = grid.near_rear_center_indices
                case 12:
                    area_indices = grid.near_rear_right_indices
                case 13:
                    area_indices = grid.far_rear_left_indices
                case 14:
                    area_indices = grid.far_rear_center_indices
                case 15:
                    area_indices = grid.far_rear_right_indices
                case 16:
                    area_indices = grid.car_area_indices
                case 17:
                    area_indices = grid.outside_indices

            # divide the covered points in an area by the number of points in an area
            data = data[area_indices]
            indices = np.nonzero(data == 1)[0]
            self.metrics[index] = round((indices.size / area_indices.size) * 100, 1)

    # helper function that is used to bring the number of rows in the sensor calculation_result to the number of total
    # points of the grid. this way, the area indices can be used correctly on the calculation result
    def __single_sensor_data(self, grid):
        data = np.zeros(grid.points.shape[0])
        np.put(data, grid.car_points_indices, 2)
        np.put(data, grid.outside_indices, self.calculation_result)
        return data
