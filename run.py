import logging
import pickle
import time
import pyvista as pv

from args import args
from environment.grid import Grid
from environment.slice import Slice
from plotting.report import create_report
from plotting.plots import create_plots
from plotting.plot_helpers import metrics, setup_plot_args, output_folder
from sensors.sensor_helpers import load_sensorset
from utils.gui import GUI

# PROGRAM OPTIONS
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def run(args):
    """Main function for the program.

    Args:
        args: input arguments provided by YAML-config file or command line.
    """

    logging.info("Starting Programm")
    sensors = load_sensorset(args.sensor_setup)

    if args.gui_mode:
        gui_instance = GUI()
        gui_instance.run()
        args.update(gui_instance.get_inputs())
    logging.info("Inputs evaluated -> now loading vehicle")

    vehicle = pv.read(args.vehicle_path).triangulate()
    logging.info("Vehicle loaded -> creating grid")

    grid = Grid(
        dim_x=args.dim_x,
        dim_y=args.dim_y,
        dim_z=args.dim_z,
        spacing=args.spacing,
        advanced=args.advanced,
        car=vehicle,
        center=args.origin,
        dist=args.nearfield_dist,
    )
    logging.info("Grid created -> starting single sensor coverage calculation")

    ix = 1
    max_ix = len(sensors)
    for sensor in sensors:
        logging.info(f"Calculating Single Sensor {ix} of {max_ix}")
        sensor.calculate_coverage(grid, vehicle)
        ix += 1
    logging.info("Finished single sensor calculation -> calculating grid coverage")

    grid.combine_data(sensors)
    grid.set_metrics_no_condition()
    grid.set_metrics_condition(
        n1=args.conditions.N1,
        n2=args.conditions.N2,
        n6=args.conditions.N6,
        n7=args.conditions.N7,
        n8=args.conditions.N8,
    )
    logging.info("Grid coverage calculated -> preparing report and plots")

    slices = [
        Slice(grid, 1.5, normal="x"),
        Slice(grid, 0, normal="y"),
        Slice(grid, 0.01),
    ]
    slices.extend(
        [
            Slice(grid, i * args.slice.distance)
            for i in range(1, args.slice.number, 1)
        ]
    )

    plot_args = setup_plot_args(
        metrics["n_sensor_technologies"], car_value=grid.car_value
    )

    if args.create_report:
        logging.info("Creating report")
        create_report(
            sensors,
            slices,
            vehicle,
            grid,
            args.save_path,
            args.folder_name,
            plot_args,
            n1=args.conditions.N1,
            n2=args.conditions.N2,
            n6=args.conditions.N6,
            n7=args.conditions.N7,
            n8=args.conditions.N8,
        )

    if not args.no_plots:
        logging.info("creating plots")
        create_plots(
            grid,
            sensors,
            vehicle,
            args.save_path,
            args.folder_name,
            slices[0],
            slices[1],
            slices[2],
        )
        logging.info("Report created -> finished")

    if args.save_variables:
        save_path = output_folder(args.save_path, args.folder_name) / "save_data.pkl"
        with open(save_path, "wb") as f:
            pickle.dump({"grid": grid, "vehicle": vehicle, "sensors": sensors,
                         "args": args}, f)


if __name__ == "__main__":
    start_time = time.time()
    logging.info("Starting main")
    run(args)
    logging.info("Success")
    logging.info(f"Results saved: {output_folder(args.save_path, args.folder_name)}")
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"Elapsed time is {elapsed_time}")
