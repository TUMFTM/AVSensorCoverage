from .lidar import Lidar


# this class is a child class of lidar and has no own implementation, since lidars and radars are modelled equally
# in the current state of the program. An extra class is needed to differentiate between the sensor types for the
# computation of the combined data and the sensorset metrics
class Radar(Lidar):
    def __init__(self, position, fov_h, fov_v, detection_range, min_range, name):
        super().__init__(position, fov_h, fov_v, detection_range, min_range, name)
