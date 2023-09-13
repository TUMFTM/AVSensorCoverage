import numpy as np

from . import grid_helpers as helpers


# this class creates a cross-section of the grid
class Slice:
    def __init__(self, grid, dist, normal="z", cells=True):
        origin = None
        if normal == "x":
            origin = (dist, 0, 0)
        elif normal == "y":
            origin = (0, dist, 0)
        elif normal == "z":
            origin = (0, 0, dist)
        self.grid = grid
        self.mesh = grid.mesh.slice(normal, origin=origin)
        self.dist = dist
        self.axis = normal
        self.cell_area = grid.spacing**2
        self.blind_area = None
        self.x_max_rear = None
        self.x_max_front = None
        self.y_max_right = None
        self.y_max_left = None
        self.x_dist = None
        self.y_dist = None
        self.blind_cells = None

        # if-clause to set the points used for calculation as the vertices or the cell centers of the grid
        if not cells:
            self.points = self.mesh.points
        else:
            self.points = self.mesh.cell_centers().points

        # call function to set the metrics
        self.__set_metrics()

    # private function that sets the metrics of the slice
    def __set_metrics(self):
        # compute blind area on cross-section
        self.blind_cells = np.nonzero(self.mesh.cell_data["sensorset"][:, 0] == 0)[0]
        self.blind_area = round(self.cell_area * self.blind_cells.size, 2)

        # compute the distances to the first covered cell in direction of global coordinate axis. to do this,
        # an area of the 4x length/width of the car is examined. the results are stored in x_dist and y_dist.
        if self.axis != "x":
            # area to examine
            indices_x = helpers.get_bounding_box_indices(
                self.points,
                (
                    self.grid.car.bounds[0] * 4,
                    self.grid.car.bounds[1] * 4,
                    self.grid.car.bounds[2],
                    self.grid.car.bounds[3],
                    self.grid.car.bounds[4],
                    self.grid.car.bounds[5],
                ),
            )[0]
            if self.axis == "z":
                # if axis is z then sort points first by y coordinate and then by x coordinate(sorting by x
                # coordinate is default, so no operation is required)
                indices_x_sorted = np.column_stack(
                    np.split(
                        indices_x,
                        np.unique(self.points[indices_x][:, 1], return_index=True)[1][
                            1:
                        ],
                    )
                ).T
            elif self.axis == "y":
                # if axis is y then sort points first by z coordinate and then by x coordinate(sorting by x
                # coordinate is default, so no operation is required)
                indices_x_sorted = np.column_stack(
                    np.split(
                        indices_x,
                        np.unique(self.points[indices_x][:, 2], return_index=True)[1][
                            1:
                        ],
                    )
                ).T

            # get the sorted data and call function to find the distances, then determine max values rear and front
            data_x = self.mesh.cell_data["sensorset"][:, 0][indices_x_sorted]
            self.x_dist = self.__get_distances(data_x)
            self.x_max_rear = np.amax(self.x_dist[:, 0])
            self.x_max_front = np.amax(self.x_dist[:, 1])

        if self.axis != "y":
            # area to examine
            indices_y = helpers.get_bounding_box_indices(
                self.points,
                (
                    self.grid.car.bounds[0],
                    self.grid.car.bounds[1],
                    self.grid.car.bounds[2] * 4,
                    self.grid.car.bounds[3] * 4,
                    self.grid.car.bounds[4],
                    self.grid.car.bounds[5],
                ),
            )[0]
            sorted_points = self.points[indices_y]

            if self.axis == "z":
                # if axis is z then sort points first by x coordinate and then by y coordinate
                indices_y = indices_y[
                    np.lexsort((sorted_points[:, 1], sorted_points[:, 0]))
                ]
                sorted_points = sorted_points[
                    np.lexsort((sorted_points[:, 1], sorted_points[:, 0]))
                ]
                indices_y_sorted = np.column_stack(
                    np.split(
                        indices_y,
                        np.unique(sorted_points[:, 0], return_index=True)[1][1:],
                    )
                ).T
            if self.axis == "x":
                # if axis is x then sort points first by z coordinate and then by y coordinate
                indices_y = indices_y[
                    np.lexsort((sorted_points[:, 1], sorted_points[:, 2]))
                ]
                sorted_points = sorted_points[
                    np.lexsort((sorted_points[:, 1], sorted_points[:, 2]))
                ]
                indices_y_sorted = np.column_stack(
                    np.split(
                        indices_y,
                        np.unique(sorted_points[:, 2], return_index=True)[1][1:],
                    )
                ).T

            # get the sorted data and call function to find the distances, then determine max values left and right
            data_y = self.mesh.cell_data["sensorset"][:, 0][indices_y_sorted]
            self.y_dist = self.__get_distances(data_y)
            self.y_max_right = np.amax(self.y_dist[:, 0])
            self.y_max_left = np.amax(self.y_dist[:, 1])

    # private function which contains an algorithm to find sequences of values 0 next to car values. the number of
    # zeros then can be directly used to determine the distance to the first covered cell
    def __get_distances(self, data):
        # create matrix as a result to save the distances
        result = np.zeros((data.shape[0], 2))
        count_rear_bool = True
        count_front_bool = False
        count_rear = 0
        count_front = 0

        # traverse through every row of the data
        for i in range(data.shape[0]):
            # traverse through every element of the row
            for value in data[i, :]:
                # start with the rear/left values
                if count_rear_bool:
                    # count consecutive zeros, if a car value appears, stop and start front/right count
                    match value:
                        case 0:
                            count_rear += 1
                        case 1:
                            count_rear = 0
                        case self.grid.car_value:
                            count_rear_bool = False
                            count_front_bool = True
                # front/right values
                if count_front_bool:
                    # we are now coming from inside the car, count consecutive zeros until we hit the first one
                    match value:
                        case 0:
                            count_front += 1
                        case 1:
                            count_front_bool = False
            # save the result for the current row and start again for the next row
            result[i, 0] = round(count_rear * np.sqrt(self.cell_area), 2)
            result[i, 1] = round(count_front * np.sqrt(self.cell_area), 2)
            count_rear = 0
            count_front = 0
            count_rear_bool = True
            count_front_bool = False

        return result
