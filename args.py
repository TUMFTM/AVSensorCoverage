import argparse
from pathlib import Path

import yaml
from easydict import EasyDict as edict
from datetime import datetime


def cur_file_path():
    return Path(__file__).absolute().parent


def get_default_folder_name():
    return datetime.now().strftime("simulation_%d_%m_%Y_%H-%M-%S")


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='Autonomous Vehicle Sensor Setup Coverage Analysis')

# Arguments for sensors and vehicle
parser.add_argument("--sensors",  type=lambda p: Path(p).absolute(), default=cur_file_path() / "sensorsets" / "test_setup.yaml", dest="sensor_setup", help="Path to the yaml file defining the sensors.")
parser.add_argument("--vehicle",  type=lambda p: Path(p).absolute(), default=cur_file_path() / "vehicle" / "simple_box.obj", dest="vehicle_path", help="Path to the 3D vehicle model.")

# Arguments for Directories
parser.add_argument("--path", default=cur_file_path() / "simulation_results", type=lambda p: Path(p).absolute(), dest="save_path", help="Parent path for simulation results folder.")
parser.add_argument("--name", default=get_default_folder_name(), dest="folder_name", help="Name of the folder. If not given, current datetime is used.")

# Argument for YAML configuration file
parser.add_argument("--config", type=lambda p: Path(p).absolute(), default=cur_file_path() / "config.yaml", help="Path to the yaml configuration file for environment setup.")

# Program Arguments
parser.add_argument("--no_plots", action="store_true", help="Deactivate creation of plots. Default is plots are created.")
parser.add_argument("--gui_mode", action='store_true', help="Activate GUI mode for entering settings.",)
parser.add_argument("--create_report", action="store_true", help="Create a pdf report with results.",)
parser.add_argument("--save_variables", action="store_true", help="Save variables as pickle.")

# --------------------------------------------------
program_args = parser.parse_args()

# Add parameters from YAML to args dict
with open(program_args.config, "r") as yamlfile:
    cfg = yaml.safe_load(yamlfile)

merged = {**vars(program_args), **cfg}

args = edict(merged)
