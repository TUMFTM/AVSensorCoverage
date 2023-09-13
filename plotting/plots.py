import pyvista as pv

from .plot_helpers import SENSOR_COLOR_MAP, metrics, setup_plot_args, output_folder

pv.set_plot_theme(pv.themes.DocumentTheme())

class SetVisibilityCallback:
    """Helper callback to keep a reference to the actor being modified."""

    def __init__(self, actor):
        self.actor = actor

    def __call__(self, state):
        self.actor.SetVisibility(state)


def create_plots(grid, sensors, vehicle, path, name, slice_x, slice_y, slice_z):
    args1 = setup_plot_args(metrics["n_sensors"], grid.car_value)
    args2 = setup_plot_args(metrics["n_sensor_technologies"], grid.car_value)
    args6 = setup_plot_args(metrics["n_cameras"], grid.car_value)
    args7 = setup_plot_args(metrics["n_lidars"], grid.car_value)
    args8 = setup_plot_args(metrics["n_radars"], grid.car_value)

    # create directories for screenshots data and report if they don't exist
    overall_path = output_folder(path, name)

    legend_entries1 = [
        [" Camera Sensor", "blue"],
        [" LIDAR Sensor", "r"],
        [" Radar Sensor", "37FD12"],
    ]

    p1 = pv.Plotter()
    p1.add_text(
        "Visualization of all sensors",
        position="upper_edge",
        font="arial",
        font_size=12,
    )
    p1.add_mesh(vehicle, color="565656")
    p1.add_legend(
        legend_entries1, border=True, loc="upper right", face="r", size=(0.22, 0.22)
    )

    startpos = 12
    size = 25
    for sensor in sensors:
        color, opacity = SENSOR_COLOR_MAP.get(sensor.__class__.__name__, ("b", 1))
        actor = p1.add_mesh(sensor.mesh, color=color, opacity=opacity, lighting=False)
        callback = SetVisibilityCallback(actor)
        p1.add_checkbox_button_widget(
            callback,
            value=True,
            position=(5.0, startpos),
            size=size,
            border_size=1,
            color_on=color,
            color_off='grey',
            background_color='grey',
        )
        p1.add_points(sensor.position)
        startpos = startpos + size + (size // 10)
    p1.add_text("Toggle boxes to turn sensor mesh on/off", position="lower_left", font_size=9)
    p1.add_axes()
    p1.show_grid()
    p1.save_graphic(overall_path / "plot1.pdf")
    p1.show()

    legend_entries2 = [[" Center of blind cell", "red"]]

    p2 = pv.Plotter()
    p2.add_text(
        "Blind spots of the sensorset",
        position="upper_edge",
        font="arial",
        font_size=12,
    )
    p2.add_legend(legend_entries2, border=True, loc="upper right", face="r", bcolor="w")
    p2.add_mesh(vehicle, color="565656")
    p2.add_points(grid.blind_spots, color="r", point_size=8)
    p2.add_axes()
    p2.show_grid()
    p2.save_graphic(overall_path / "plot2.pdf")
    p2.show()

    legend_entries3 = [
        [f" x = {slice_x.dist}m", "black"],
        [f" spacing = {grid.spacing}m", "black"],
    ]

    p3 = pv.Plotter()
    p3.add_text(
        "Number of sensors covering each cell",
        position="upper_edge",
        font="arial",
        font_size=12,
    )
    p3.add_legend(
        legend_entries3,
        border=True,
        loc="upper center",
        face=None,
        bcolor="w",
        size=(0.2, 0.15),
    )
    p3.add_mesh(slice_x.mesh, **args1)
    p3.camera_position = "yz"
    p3.add_axes()
    p3.show_grid()
    p3.save_graphic(overall_path / "plot3.pdf")
    p3.show()

    legend_entries4 = [
        [f" y = {slice_y.dist}m", "black"],
        [f" spacing = {grid.spacing}m", "black"],
    ]

    p4 = pv.Plotter()
    p4.add_text(
        "Number of sensors covering each cell",
        position="upper_edge",
        font="arial",
        font_size=12,
    )
    p4.add_legend(
        legend_entries4,
        border=True,
        loc="upper center",
        face=None,
        bcolor="w",
        size=(0.2, 0.15),
    )
    p4.add_mesh(slice_y.mesh, **args1)
    p4.camera_position = "xz"
    p4.add_axes()
    p4.show_grid()
    p4.save_graphic(overall_path / "plot4.pdf")
    p4.show()

    legend_entries5 = [
        [f" z = {slice_z.dist}m", "black"],
        [f" spacing = {grid.spacing}m", "black"],
    ]
    p5 = pv.Plotter(shape="2/3", window_size=[1280, 720])

    p5.subplot(3)
    p5.add_text(
        "Number of sensors covering each cell",
        position="upper_edge",
        font="arial",
        font_size=10,
    )
    p5.add_legend(
        legend_entries5,
        border=True,
        loc="upper center",
        face=None,
        bcolor="w",
        size=(0.2, 0.15),
    )
    p5.add_mesh(slice_z.mesh, **args1)
    p5.add_axes()
    p5.show_grid()
    p5.camera_position = "xy"
    p5.subplot(4)
    p5.add_text(
        "Number of different sensor technologies covering each cell",
        position="upper_edge",
        font="arial",
        font_size=10,
    )
    p5.add_legend(
        legend_entries5,
        border=True,
        loc="upper center",
        face=None,
        bcolor="w",
        size=(0.2, 0.15),
    )
    p5.add_mesh(slice_z.mesh, **args2)
    p5.add_axes()
    p5.show_grid()
    p5.camera_position = "xy"
    p5.subplot(0)
    p5.add_text(
        "Number of cameras covering each cell",
        position="upper_edge",
        font="arial",
        font_size=10,
    )
    p5.add_legend(
        legend_entries5,
        border=True,
        loc="lower right",
        face=None,
        bcolor="w",
        size=(0.2, 0.15),
    )
    p5.add_mesh(slice_z.mesh, **args6)
    p5.add_axes()
    p5.show_grid()
    p5.camera_position = "xy"
    p5.subplot(1)
    p5.add_text(
        "Number of LIDAR covering each cell",
        position="upper_edge",
        font="arial",
        font_size=10,
    )
    p5.add_legend(
        legend_entries5,
        border=True,
        loc="lower right",
        face=None,
        bcolor="w",
        size=(0.20, 0.15),
    )
    p5.add_mesh(slice_z.mesh, **args7)
    p5.add_axes()
    p5.show_grid()
    p5.camera_position = "xy"
    p5.subplot(2)
    p5.add_text(
        "Number of radars covering each cell",
        position="upper_edge",
        font="arial",
        font_size=10,
    )
    p5.add_legend(
        legend_entries5,
        border=True,
        loc="lower right",
        face=None,
        bcolor="w",
        size=(0.20, 0.15),
    )
    p5.add_mesh(slice_z.mesh, **args8)
    p5.add_axes()
    p5.show_grid()
    p5.camera_position = "xy"
    p5.save_graphic(overall_path / "plot5.pdf")
    p5.show()
