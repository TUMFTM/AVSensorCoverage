import pyvista as pv

# this file contains 3d-vehicle-models in pyvista compatible formats, that are working correctly with the framework
# you can also provide other formats than obj, for supported formats please check the pyvista.read documentation
# please make sure yourself that the 3d-model fulfills the requirements to be used correctly in the framework.
# failure to do so may result in inability to run the program with your desired vehicle
evoque_path = (
    "/Users/hahns/Uni/BA/sensorauslegung_tool/CAD/Evoque_korrekte_strukturen.obj"
)
evoque = pv.read(evoque_path).triangulate()
ipace_path = "/Users/hahns/Uni/BA/sensorauslegung_tool/CAD/ipace.obj"
ipace = pv.read(ipace_path).triangulate()
t7_path = "/Users/hahns/Uni/BA/sensorauslegung_tool/CAD/t7_reduced.obj"
t7 = pv.read(t7_path).triangulate()
