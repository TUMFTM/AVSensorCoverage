import numpy as np
import pyvista as pv
from scipy.spatial import ConvexHull, Delaunay

from . import grid_helpers as helpers


# this class models the environment of the vehicle as a uniform grid
class Grid:
    def __init__(
        self,
        dim_x,
        dim_y,
        dim_z,
        spacing,
        center,
        car,
        cells=True,
        advanced=False,
        alpha=15,
        beta=10,
        dist=5,
    ):
        self.spacing = spacing
        x = int(dim_x / self.spacing)
        y = int(dim_y / self.spacing)
        z = int(dim_z / self.spacing)
        origin = (center[0] - dim_x / 2, center[1] - dim_y / 2, center[2])
        self.mesh = pv.ImageData(
            dimensions=(x + 1, y + 1, z + 1),
            spacing=(self.spacing, self.spacing, self.spacing),
            origin=origin,
        )
        self.car = car
        self.car_value = 0
        self.car_points_indices = None
        self.outside_indices = None
        self.remove_indices = None
        self.metrics = np.zeros(shape=(18, 9))
        self.blind_spot_volume = None
        self.blind_spots = None
        self.car_area_indices = np.empty(1, dtype=np.int8)

        # if-clause to set the points used for calculation as the vertices or the cell centers of the grid
        if not cells:
            self.points = self.mesh.points
        else:
            self.points = self.mesh.cell_centers().points

        # define, which points are inside the vehicle and shall not be used for calculation (mode normal)
        self.car_points_indices = helpers.get_bounding_box_indices(
            self.points, self.car.bounds
        )[0]
        self.remove_indices, self.outside_indices = helpers.get_bounding_box_indices(
            self.points,
            (
                self.car.bounds[0],
                self.car.bounds[1],
                self.car.bounds[2],
                self.car.bounds[3],
                0,
                dim_z,
            ),
        )
        # define, which points are inside the vehicle and shall not be used for calculation (mode advanced)
        if advanced:
            # call function to set the remove_indices and the outside_indices
            self.__get_indices_advanced()
            # additionally set the indices for car_area
            high_box_indices = helpers.get_bounding_box_indices(
                self.points,
                (
                    self.car.bounds[0],
                    self.car.bounds[1],
                    self.car.bounds[2],
                    self.car.bounds[3],
                    0,
                    dim_z,
                ),
            )[0]
            same_indices = np.isin(
                high_box_indices, self.remove_indices, assume_unique=True
            )
            same_indices = np.nonzero(same_indices)[0]
            self.car_area_indices = np.delete(high_box_indices, same_indices, axis=0)

        # remove the points at remove_indices for the calculation
        self.calc_points = np.delete(self.points, self.remove_indices, axis=0)

        # ------------------------------- surrounding Area indices are set in this block ------------------------------
        bounds = self.car.bounds
        corner_fl = np.array([bounds[1], bounds[3], 0])
        corner_fr = np.array([bounds[1], bounds[2], 0])
        corner_rl = np.array([bounds[0], bounds[3], 0])
        corner_rr = np.array([bounds[0], bounds[2], 0])

        # first assume every area is a rectangular box and set the indices
        self.far_front_left_indices = helpers.get_bounding_box_indices(
            self.points,
            (
                bounds[1],
                center[0] + dim_x / 2,
                bounds[3],
                center[1] + dim_y / 2,
                0,
                center[2] + dim_z,
            ),
        )[0]

        self.far_front_center_indices = helpers.get_bounding_box_indices(
            self.points,
            (
                bounds[1] + dist,
                center[0] + dim_x / 2,
                bounds[2],
                bounds[3],
                0,
                center[2] + dim_z,
            ),
        )[0]

        self.far_front_right_indices = helpers.get_bounding_box_indices(
            self.points,
            (
                bounds[1],
                center[0] + dim_x / 2,
                center[1] - dim_y / 2,
                bounds[2],
                0,
                center[2] + dim_z,
            ),
        )[0]

        self.near_front_left_indices = helpers.get_bounding_box_indices(
            self.points,
            (
                bounds[1],
                center[0] + dim_x / 2,
                bounds[3],
                center[1] + dim_y / 2,
                0,
                center[2] + dim_z,
            ),
        )[0]

        self.near_front_center_indices = helpers.get_bounding_box_indices(
            self.points,
            (bounds[1], bounds[1] + dist, bounds[2], bounds[3], 0, center[2] + dim_z),
        )[0]

        self.near_front_right_indices = helpers.get_bounding_box_indices(
            self.points,
            (
                bounds[1],
                center[0] + dim_x / 2,
                center[1] - dim_y / 2,
                bounds[2],
                0,
                center[2] + dim_z,
            ),
        )[0]

        self.far_left_indices = helpers.get_bounding_box_indices(
            self.points,
            (
                bounds[0],
                bounds[1],
                bounds[3] + dist,
                center[1] + dim_y / 2,
                0,
                center[2] + dim_z,
            ),
        )[0]

        self.near_left_indices = helpers.get_bounding_box_indices(
            self.points,
            (bounds[0], bounds[1], bounds[3], bounds[3] + dist, 0, center[2] + dim_z),
        )[0]

        self.near_right_indices = helpers.get_bounding_box_indices(
            self.points,
            (bounds[0], bounds[1], bounds[2] - dist, bounds[2], 0, center[2] + dim_z),
        )[0]

        self.far_right_indices = helpers.get_bounding_box_indices(
            self.points,
            (
                bounds[0],
                bounds[1],
                center[1] - dim_y / 2,
                bounds[2] - dist,
                0,
                center[2] + dim_z,
            ),
        )[0]

        self.near_rear_left_indices = helpers.get_bounding_box_indices(
            self.points,
            (
                center[0] - dim_x / 2,
                bounds[0],
                bounds[3],
                center[1] + dim_y / 2,
                0,
                center[2] + dim_z,
            ),
        )[0]

        self.near_rear_center_indices = helpers.get_bounding_box_indices(
            self.points,
            (bounds[0] - dist, bounds[0], bounds[2], bounds[3], 0, center[2] + dim_z),
        )[0]

        self.near_rear_right_indices = helpers.get_bounding_box_indices(
            self.points,
            (
                center[0] - dim_x / 2,
                bounds[0],
                center[1] - dim_y / 2,
                bounds[2],
                0,
                center[2] + dim_z,
            ),
        )[0]

        self.far_rear_left_indices = helpers.get_bounding_box_indices(
            self.points,
            (
                center[0] - dim_x / 2,
                bounds[0],
                bounds[3],
                center[1] + dim_y / 2,
                0,
                center[2] + dim_z,
            ),
        )[0]

        self.far_rear_center_indices = helpers.get_bounding_box_indices(
            self.points,
            (
                center[0] - dim_x / 2,
                bounds[0] - dist,
                bounds[2],
                bounds[3],
                0,
                center[2] + dim_z,
            ),
        )[0]

        self.far_rear_right_indices = helpers.get_bounding_box_indices(
            self.points,
            (
                center[0] - dim_x / 2,
                bounds[0],
                center[1] - dim_y / 2,
                bounds[2],
                0,
                center[2] + dim_z,
            ),
        )[0]

        # now further edit the indices of the areas that are not rectangular

        # for the 4 center areas add the angular pieces left and right of the rectangular box
        self.near_front_center_indices = np.hstack(
            (
                self.near_front_center_indices,
                self.__get_corner_indices(
                    self.near_front_right_indices, corner_fr, dist, -alpha, 0
                ),
                self.__get_corner_indices(
                    self.near_front_left_indices, corner_fl, dist, 0, alpha
                ),
            )
        )
        self.far_front_center_indices = np.hstack(
            (
                self.far_front_center_indices,
                self.__get_corner_indices(
                    self.near_front_right_indices, corner_fr, dist, -alpha, 0, far=True
                ),
                self.__get_corner_indices(
                    self.near_front_left_indices, corner_fl, dist, 0, alpha, far=True
                ),
            )
        )
        self.near_rear_center_indices = np.hstack(
            (
                self.near_rear_center_indices,
                self.__get_corner_indices(
                    self.near_rear_right_indices, corner_rr, dist, -180, -180 + beta
                ),
                self.__get_corner_indices(
                    self.near_rear_left_indices, corner_rl, dist, 180 - beta, 180
                ),
            )
        )
        self.far_rear_center_indices = np.hstack(
            (
                self.far_rear_center_indices,
                self.__get_corner_indices(
                    self.far_rear_right_indices,
                    corner_rr,
                    dist,
                    -180,
                    -180 + beta,
                    far=True,
                ),
                self.__get_corner_indices(
                    self.far_rear_left_indices,
                    corner_rl,
                    dist,
                    180 - beta,
                    180,
                    far=True,
                ),
            )
        )

        # for the 8 corner areas only keep the indices of the rectangular box, that are within the specified angles
        # (alpha and beta) and distances
        self.near_front_left_indices = self.__get_corner_indices(
            self.near_front_left_indices, corner_fl, dist, alpha, 90
        )
        self.far_front_left_indices = self.__get_corner_indices(
            self.far_front_left_indices, corner_fl, dist, alpha, 90, far=True
        )
        self.near_front_right_indices = self.__get_corner_indices(
            self.near_front_right_indices, corner_fr, dist, -90, -alpha
        )
        self.far_front_right_indices = self.__get_corner_indices(
            self.far_front_right_indices, corner_fr, dist, -90, -alpha, far=True
        )
        self.near_rear_left_indices = self.__get_corner_indices(
            self.near_rear_left_indices, corner_rl, dist, 90, 180 - beta
        )
        self.far_rear_left_indices = self.__get_corner_indices(
            self.far_rear_left_indices, corner_rl, dist, 90, 180 - beta, far=True
        )
        self.near_rear_right_indices = self.__get_corner_indices(
            self.near_rear_right_indices, corner_rr, dist, -180 + beta, -90
        )
        self.far_rear_right_indices = self.__get_corner_indices(
            self.far_rear_right_indices, corner_rr, dist, -180 + beta, -90, far=True
        )
        # ------------------------------- surrounding Area indices setting is done -----------------------------------

    # callable function to create a cross-section of the grid using the pyvista slice
    def slice_coordinate_axis(self, dist, normal="z"):
        if normal == "x":
            origin = (dist, 0, 0)
        elif normal == "y":
            origin = (0, dist, 0)
        elif normal == "z":
            origin = (0, 0, dist)
        my_slice = self.mesh.slice(normal, origin=origin)
        return my_slice

    # private function, that creates the convex hull of the corresponding vehicle and checks, which points are inside
    # the indices of the points, that are inside are set as the remove_indices. function is only used if mode=advanced
    def __get_indices_advanced(self):
        # create convex hull and delauney of convex hull vertices
        hull = ConvexHull(self.car.points)
        delaunay = Delaunay(self.car.points[hull.vertices])
        points = self.points[self.car_points_indices]

        # find the simplexes, simplex = -1 corresponds to outside of the convex hull
        simplexes = delaunay.find_simplex(points)
        wrong_indices = np.where(simplexes == -1)[0]
        self.remove_indices = np.delete(self.car_points_indices, wrong_indices)
        mask = np.ones(self.points.shape[0])
        mask[self.remove_indices] = False
        self.outside_indices = np.nonzero(mask)[0]
        self.outside_indices = np.reshape(
            self.outside_indices, (self.outside_indices.size, 1)
        )

    # private function, that determines which points lie in an angular section
    # is used to set the indices of the surrounding areas
    def __get_corner_indices(
        self, indices, corner, dist, angle_start, angle_end, far=False
    ):
        # get the vectors from corner to points in cylindrical coordinates
        points = self.points[indices]
        vectors = points - np.tile(corner, (indices.size, 1))
        vectors = helpers.calculate_cyl_from_cart(vectors)

        # check which points fulfill the conditions (first distance, then angle) and return their indices
        if far:
            dist = vectors[:, 0] >= dist
        else:
            dist = vectors[:, 0] <= dist
        angle = np.logical_and(vectors[:, 1] <= angle_end, vectors[:, 1] >= angle_start)
        vectors_bool = np.vstack((dist, angle))
        result = np.all(vectors_bool, axis=0)
        indices = indices[np.nonzero(result)[0]]

        return indices

    # callable function that combines the calculated data of each sensor using addition and boolean operations
    # the obtained data describes the coverage of the total sensorset and is stored as cell_data in self.mesh
    def combine_data(self, sensors):
        combined_results = np.zeros((self.calc_points.shape[0], 9))

        # for every sensor combine their calculation result to get the combined results
        for sensor in sensors:
            combined_results[:, 0] = np.logical_or(
                combined_results[:, 0], sensor.calculation_result
            )
            combined_results[:, 1] += sensor.calculation_result

            if sensor.__class__.__name__ == "Camera":
                combined_results[:, 3] = np.logical_or(
                    combined_results[:, 3], sensor.calculation_result
                )
                combined_results[:, 6] += sensor.calculation_result
            elif sensor.__class__.__name__ == "Lidar":
                combined_results[:, 4] = np.logical_or(
                    combined_results[:, 4], sensor.calculation_result
                )
                combined_results[:, 7] += sensor.calculation_result
            elif sensor.__class__.__name__ == "Radar":
                combined_results[:, 5] = np.logical_or(
                    combined_results[:, 5], sensor.calculation_result
                )
                combined_results[:, 8] += sensor.calculation_result

            combined_results[:, 2] = (
                combined_results[:, 3] + combined_results[:, 4] + combined_results[:, 5]
            )

        # for the calculation, only the calc_points are used. Now the combined results are combined with the points
        # corresponding to the car, to obtain same number of rows as self.points. For each point of the car a scalar
        # value (max value that appears in combined data +1) is set
        expanded_data = np.full((self.points.shape[0], 9), -1)
        self.car_value = int(np.amax(combined_results[:, 1])) + 1
        expanded_data[self.car_points_indices, :] = self.car_value
        np.put_along_axis(expanded_data, self.outside_indices, combined_results, axis=0)

        self.mesh.cell_data["sensorset"] = expanded_data

    # callable function, that sets the metrics with no condition
    def set_metrics_no_condition(self, metrics_array=None, all_metrics=True):
        blind_spot_indices = np.nonzero(self.mesh.cell_data["sensorset"][:, 0] == 0)[0]
        self.blind_spots = self.points[blind_spot_indices]
        self.blind_spot_volume = round(
            blind_spot_indices.size * self.mesh.spacing[0] ** 3, 2
        )

        # construct a matrix that defines in which order the metrics are set. first traverse areas, then metrics
        if all_metrics:
            array1 = np.repeat(np.arange(18), 4, axis=0)
            array2 = np.tile(np.array([[0, 3, 4, 5]]), (1, 18)).T
            metrics_array = np.column_stack((array1, array2))

        # traverse through the matrix and calculate the metrics
        for row in metrics_array:
            area_indices = self.__get_area_indices(row[0])
            area_data = self.mesh.cell_data["sensorset"][:, row[1]][area_indices]

            # check which points are covered (which elements equal to 1)
            covered = np.nonzero(area_data == 1)[0]
            if row[0] == 17:
                # for the total area divide number of covered points by the number of calc_points
                self.metrics[17, row[1]] = round(
                    (covered.size / self.calc_points.shape[0]) * 100, 1
                )
            else:
                # for the areas divide number of covered points by the number of points inside the area
                self.metrics[row[0], row[1]] = round(
                    (covered.size / area_indices.size) * 100, 1
                )

    # callable function, that sets the metrics with a condition. conditions can be passed, otherwise defaults are used
    def set_metrics_condition(
        self, metrics_array=None, all_metrics=True, n1=3, n2=2, n6=2, n7=2, n8=2
    ):
        # construct a matrix, that defines in which order the metrics are set. column 0 contains the areas,
        # column 1 contains the metrics, column 2 contains the start condition, column 3 contains the end condition
        if all_metrics:
            areas = np.repeat(np.arange(18), 5, axis=0)
            metrics = np.tile(np.array([[1, 2, 6, 7, 8]]), (1, 18)).T
            start_cond = np.tile(np.array([n1, n2, n6, n7, n8]), (1, 18)).T
            end_cond = np.full((90, 1), self.car_value)

            metrics_array = np.column_stack((areas, metrics, start_cond, end_cond))

        # traverse through the matrix and calculate the metrics accordingly
        for row in metrics_array:
            area_indices = self.__get_area_indices(row[0])

            # check, that start and end condition are fulfilled
            cond1 = self.mesh.cell_data["sensorset"][:, row[1]][area_indices] >= row[2]
            cond2 = self.mesh.cell_data["sensorset"][:, row[1]][area_indices] <= row[3]
            covered = np.nonzero(np.logical_and(cond1, cond2))[0]
            if row[0] == 17:
                # for the total area divide number of covered points by the number of calc_points
                self.metrics[17, row[1]] = round(
                    (covered.size / self.calc_points.shape[0]) * 100, 1
                )
            else:
                # for the areas divide number of covered points by the number of points inside the area
                self.metrics[row[0], row[1]] = round(
                    (covered.size / area_indices.size) * 100, 1
                )

    # helper function used to translate from integers to the corresponding area indices
    def __get_area_indices(self, index):
        area_indices = None
        match index:
            case 0:
                area_indices = self.far_front_left_indices
            case 1:
                area_indices = self.far_front_center_indices
            case 2:
                area_indices = self.far_front_right_indices
            case 3:
                area_indices = self.near_front_left_indices
            case 4:
                area_indices = self.near_front_center_indices
            case 5:
                area_indices = self.near_front_right_indices
            case 6:
                area_indices = self.far_left_indices
            case 7:
                area_indices = self.near_left_indices
            case 8:
                area_indices = self.near_right_indices
            case 9:
                area_indices = self.far_right_indices
            case 10:
                area_indices = self.near_rear_left_indices
            case 11:
                area_indices = self.near_rear_center_indices
            case 12:
                area_indices = self.near_rear_right_indices
            case 13:
                area_indices = self.far_rear_left_indices
            case 14:
                area_indices = self.far_rear_center_indices
            case 15:
                area_indices = self.far_rear_right_indices
            case 16:
                area_indices = self.car_area_indices
            case 17:
                area_indices = np.arange(self.points.shape[0] - 1)

        return area_indices
