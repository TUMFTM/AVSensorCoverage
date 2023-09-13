from pathlib import Path


metrics = dict(
    total_coverage=0,
    n_sensors=1,
    n_sensor_technologies=2,
    camera=3,
    lidar=4,
    radar=5,
    n_cameras=6,
    n_lidars=7,
    n_radars=8,
)

areas = dict(
    far_front_left=0,
    far_front_center=1,
    far_front_right=2,
    near_front_left=3,
    near_front_center=4,
    near_front_right=5,
    far_left=6,
    near_left=7,
    near_right=8,
    far_right=9,
    near_rear_left=10,
    near_rear_center=11,
    near_rear_right=12,
    far_rear_left=13,
    far_rear_center=14,
    far_rear_right=15,
    car_area=16,
    total=17,
)

DEFAULT_PLOT_ARGS = {
    "cmap": "plasma_r",
    "copy_mesh": True,
    "scalar_bar_args": {
        "fmt": "%.0f",
        "n_labels": None,
        "below_label": "Not covered",
        "above_label": "Vehicle",
        "title": "",
        "width": 0.6,
        "position_x": 0.2,
    },
    "clim": [1, None],
    "below_color": "FFFBC8",
    "above_color": "black",
}

SENSOR_COLOR_MAP = {
    "Camera": ("blue", 0.3),
    "Lidar": ("red", 0.4),
    "Radar": ("37FD12", 0.5),
}


def setup_plot_args(component_value, car_value):
    args = DEFAULT_PLOT_ARGS.copy()
    args["component"] = component_value
    args["scalar_bar_args"]["n_labels"] = car_value - 1
    args["clim"][1] = car_value - 1
    return args


def output_folder(path, name):
    # create directories for screenshots data and report if they don't exist
    overall_path = Path(path) / name
    Path.mkdir(overall_path, parents=True, exist_ok=True)
    return overall_path
