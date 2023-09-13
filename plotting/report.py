import csv
from pathlib import Path
import numpy as np
import pandas as pd
import pyvista as pv
import reportlab.platypus as pp
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from .plot_helpers import areas, SENSOR_COLOR_MAP, output_folder

pv.set_plot_theme(pv.themes.DocumentTheme())
table_style = pp.TableStyle(
    [
        ("BACKGROUND", (0, 0), (0, -1), colors.gray),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (1, 0), (-1, -1), colors.mistyrose),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]
)


# callable function that creates report according to passed parameters
def create_report(
    sensors, slices, vehicle, grid, path, name, args, n1=3, n2=2, n6=2, n7=2, n8=2
):
    overall_path = output_folder(path, name)
    path_slices = overall_path / "slices"
    path_sensors = overall_path / "sensors"
    path_sensorset = overall_path / "sensorset"
    path_png_pictures = overall_path / "png_screenshots"

    Path.mkdir(path_slices, exist_ok=True)
    Path.mkdir(path_sensors, exist_ok=True)
    Path.mkdir(path_sensorset, exist_ok=True)
    Path.mkdir(path_png_pictures, exist_ok=True)

    # legend for all screenshots
    legend_entries = [
        [" Camera Sensor", "blue"],
        [" LIDAR Sensor", "r"],
        [" Radar Sensor", "37FD12"],
        [" This Sensor", "orange"],
    ]

    # create screenshots for each sensor and save them
    for current_sensor in sensors:
        p = pv.Plotter(off_screen=True)
        p.add_points(current_sensor.position, point_size=20, color="orange")
        for sensor in sensors:
            color, opacity = SENSOR_COLOR_MAP.get(sensor.__class__.__name__, ("b", 1))
            p.add_points(sensor.position, color=color, point_size=12)

        p.set_position(point=current_sensor.plot_position)
        p.camera.focal_point = current_sensor.position
        p.camera.up = [0, 0, 1]
        p.add_mesh(vehicle, color="565656")
        p.add_axes()
        p.add_legend(
            legend_entries, border=True, loc="upper right", face="r", size=(0.22, 0.22)
        )
        p.show_grid()
        filename = f"{current_sensor.name}-metrics".replace(" ", "-")
        p.screenshot(path_sensors / f"{filename}.jpg")
        p.screenshot(path_png_pictures / f"{filename}.png")
        p.close()

    # create two screenshots for the whole sensorset and save them
    for i in range(1, 3, 1):
        p = pv.Plotter(off_screen=True)
        for sensor in sensors:
            color, opacity = SENSOR_COLOR_MAP.get(sensor.__class__.__name__, ("b", 1))
            p.add_points(sensor.position, color=color, point_size=12)

        p.add_mesh(vehicle, color="565656")
        if i == 1:
            p.set_position(point=[8.5, 7, 7])
        if i == 2:
            p.set_position(point=[-6.5, -7, 7])
        p.camera.focal_point = [1.5, 0, 0]
        p.camera.up = [0, 0, 1]
        p.add_axes()
        p.add_legend(
            legend_entries[0:3],
            border=True,
            loc="lower right",
            face="r",
            size=(0.22, 0.22),
        )
        p.show_grid()
        filename = f"sensorset{i}".replace(" ", "-")
        p.screenshot(path_sensorset / f"{filename}.jpg")
        p.screenshot(path_png_pictures / f"{filename}.png")
        p.close()

    # create a screenshot for every slice and save it
    for current_slice in slices:
        legend_entries = [
            [f" {current_slice.axis} = {current_slice.dist}m", "black"],
            [f" spacing = {grid.spacing}m", "black"],
        ]
        p = pv.Plotter(off_screen=True)
        p.add_legend(
            legend_entries,
            border=True,
            loc="upper center",
            face=None,
            bcolor="w",
            size=(0.2, 0.15),
        )
        p.add_mesh(current_slice.mesh, **args)
        if current_slice.axis == "z":
            p.camera_position = "xy"
        elif current_slice.axis == "y":
            p.camera_position = "xz"
        elif current_slice.axis == "x":
            p.camera_position = "yz"
        p.show_grid()
        p.add_axes()
        filename = f"cross-section_{current_slice.axis}={current_slice.dist}m".replace(" ", "-")
        p.screenshot(
            path_slices / f"{filename}.jpg"
        )
        p.screenshot(
            path_png_pictures / f"{filename}.png"
        )
        p.close()

    # save the calculated data from grid as 2 csv files
    np.savetxt(path_sensorset / "metrics.csv", grid.metrics, fmt="%s")
    bs_vol_row1 = "blind_spot_volume", grid.blind_spot_volume, "m^3"
    with open(path_sensorset / "blindspotvolume.csv", "w", newline="") as bs_vol:
        writer = csv.writer(bs_vol, delimiter=" ")
        writer.writerow(bs_vol_row1)

    # save the calculated data from each sensor as 2 csv files
    for sensor in sensors:
        filename = f"{sensor.name}-vector.csv".replace(" ", "-")
        np.savetxt(path_sensors / filename, sensor.metrics, fmt="%s")
        sensor_row1 = "covered-volume", sensor.covered_volume, "m^3"
        sensor_row2 = "occluded-volume", sensor.occluded_volume, "m^3"
        sensor_row3 = "fraction-occluded", sensor.fraction_occluded, "%"
        filename = f"{sensor.name}-metrics.csv".replace(" ", "-")
        with open(path_sensors / filename, "w", newline="") as sensor_metrics:
            writer = csv.writer(sensor_metrics, delimiter=" ")
            writer.writerow(sensor_row1)
            writer.writerow(sensor_row2)
            writer.writerow(sensor_row3)

    # save the calculated data from each slice as a csv file
    for cur_slice in slices:
        slice_row1 = "x_max_front", cur_slice.x_max_front
        slice_row2 = "x_max_rear", cur_slice.x_max_rear
        slice_row3 = "y_max_left", cur_slice.y_max_left
        slice_row4 = "y_max_right", cur_slice.y_max_right
        slice_row5 = "blind_area", cur_slice.blind_area
        filename = f"cross-section_{cur_slice.axis}={cur_slice.dist}m.csv".replace(" ", "-")
        with open(path_slices / filename, "w", newline="",) as sensor_metrics:
            writer = csv.writer(sensor_metrics, delimiter=" ")
            writer.writerow(slice_row1)
            writer.writerow(slice_row2)
            writer.writerow(slice_row3)
            writer.writerow(slice_row4)
            writer.writerow(slice_row5)

    # create a csv file with all area names
    with open(path_sensorset / "areas.csv", mode="w", newline="") as area_file:
        writer = csv.writer(area_file)
        for area in areas:
            writer.writerow([area])

    # create pdf
    pdf_filename = overall_path / "Result.pdf"
    doc = pp.SimpleDocTemplate(str(pdf_filename), pagesize=letter)
    styles = getSampleStyleSheet()

    # list story contains all elements of the report pdf, they are now added subsequently
    # first append everything related to the total sensorset
    story = [
        pp.Paragraph(str("Total sensorset metrics"), styles["Title"]),
        pp.Image(path_sensorset / "sensorset1.jpg", width=385, height=287),
        pp.Image(path_sensorset / "sensorset2.jpg", width=385, height=287),
        pp.PageBreak(),
    ]

    explanation1 = (
        "This table contains the percentage of points in each area, that fulfill the condition of the "
        "metric. Every column has its own condition/metric :"
    )
    explanation2 = "Column 1: Points that are covered by the Sensorset"
    explanation3 = f"Column 2: Points that are covered by at least {n1} sensors"
    explanation4 = f"Column 3: Points that are covered by at least {n2} different sensor technologies"
    explanation5 = "Column 4: Points that are covered by a Camera"
    explanation6 = "Column 5: Points that are covered by a LIDAR"
    explanation7 = "Column 6: Points that are covered by a Radar"
    explanation8 = f"Column 7: Points that are covered by at least {n6} Cameras"
    explanation9 = f"Column 8: Points that are covered by at least {n7} LIDAR"
    explanation10 = f"Column 9: Points that are covered by at least {n8} Radar"
    explanation11 = (
        'Please be aware that the values for car_area are only correct if you choose grid as "advanced"!! '
        "Otherwise they must be disregarded."
    )
    explanations = [
        explanation1,
        explanation2,
        explanation3,
        explanation4,
        explanation5,
        explanation6,
        explanation7,
        explanation8,
        explanation9,
        explanation10,
        explanation11,
    ]
    paragraphs = [pp.Paragraph(explanation) for explanation in explanations]
    story.extend(paragraphs)
    story.append(pp.Spacer(1, 0.1 * inch))

    # create a table for the metrics-matrix of the sensorset from the csv files using pandas dataframes
    csv_metrics_path = path_sensorset / "metrics.csv"
    dataframe_matrix = pd.read_csv(csv_metrics_path, header=None, delimiter=" ")
    dataframe_areas = pd.read_csv(path_sensorset / "areas.csv", header=None)
    merged_metrics = pd.merge(
        dataframe_areas, dataframe_matrix, left_index=True, right_index=True
    )
    table_data6 = []
    for index, row in merged_metrics.iterrows():
        table_data6.append(row.tolist())
    vector_table = pp.Table(table_data6)
    vector_table.setStyle(table_style)
    story.append(vector_table)
    story.append(pp.Spacer(1, 0.1 * inch))

    # create a table for the blind spot volume of the sensorset from the csv files using pandas dataframes
    dataframe_bs_vol = pd.read_csv(
        path_sensorset / "blindspotvolume.csv", header=None, delimiter=" "
    )
    table_data2 = []
    for index, row in dataframe_bs_vol.iterrows():
        table_data2.append(row.tolist())
    bs_vol_table = pp.Table(table_data2)
    bs_vol_table.setStyle(table_style)
    story.append(bs_vol_table)

    story.append(pp.PageBreak())

    # create lists of csv files for each slice and each sensor in the corresponding directories
    csv_files_slices = [
        file for file in path_slices.iterdir() if file.suffix == ".csv"
    ]
    csv_files_sensors = [
        file for file in path_sensors.iterdir() if file.suffix == ".csv"
    ]

    # create a page for each of the slices
    for csv_file in csv_files_slices:
        # append page title
        csv_filename = csv_file.stem
        story.append(pp.Paragraph(csv_filename, styles["Title"]))
        # load and append image
        img_filename = csv_file.stem + ".jpg"
        img_path = path_slices / img_filename
        story.append(pp.Image(img_path, width=550, height=410))

        # create a table for the metrics of the slice from the csv files using pandas dataframes
        dataframe_slice = pd.read_csv(
            path_slices / csv_file, delimiter=" "
        )
        table_data3 = [dataframe_slice]
        for index, row in dataframe_slice.iterrows():
            table_data3.append(row.tolist())
        slice_table = pp.Table(table_data3)
        slice_table.setStyle(table_style)
        story.append(slice_table)

        story.append(pp.PageBreak())

    # create a page for each of the sensors
    for csv_file in csv_files_sensors:
        filename_sens_csv = csv_file.stem
        if "metrics" in csv_file.stem:
            # append page title
            story.append(pp.Paragraph(filename_sens_csv, styles["Title"]))
            # load and append image
            img_filename = filename_sens_csv + ".jpg"
            img_path = path_sensors / img_filename
            story.append(pp.Image(img_path, width=256, height=189))
            story.append(pp.Spacer(1, 0.1 * inch))

            # create a table for the metrics of the sensor from the csv files using pandas dataframes
            dataframe_sensor_metrics = pd.read_csv(path_sensors / csv_file, delimiter=" ")

            table_data4 = [dataframe_sensor_metrics]
            for index, row in dataframe_sensor_metrics.iterrows():
                table_data4.append(row.tolist())
            sensor_table = pp.Table(table_data4)
            sensor_table.setStyle(table_style)
            story.append(sensor_table)

        elif "vector" in csv_file.stem:
            # create a table for the metrics-vector of the sensor from the csv files using pandas dataframes
            dataframe_sensor = pd.read_csv(path_sensors / csv_file, header=None)
            merged_vector = pd.merge(
                dataframe_areas, dataframe_sensor, left_index=True, right_index=True
            )
            story.append(
                pp.Paragraph(
                    "Percentage of covered points in each area:", styles["Definition"]
                )
            )
            table_data6 = []
            for index, row in merged_vector.iterrows():
                table_data6.append(row.tolist())
            vector_table = pp.Table(table_data6)
            vector_table.setStyle(table_style)
            story.append(pp.Spacer(1, 0.1 * inch))
            story.append(vector_table)

            story.append(pp.PageBreak())

    doc.build(story)
