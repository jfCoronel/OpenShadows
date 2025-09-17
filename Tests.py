import OpenShadows as osh
import math
import numpy as np

env = osh.Environment_3D()
env.add_polygon_3D(osh.Polygon_3D("sur",[0,0,0],0,0,[[0, 0], [5, 0], [5, 2], [0, 2]],holes2D=[[[1,0.5],[4,0.5],[4,1.5],[1,1.5]]]))
#env.add_polygon_3D(osh.Polygon_3D("sur",[0,0,0],0,0,[[0, 0], [5, 0], [5, 2], [0, 2]]))
env.add_polygon_3D(osh.Polygon_3D("este",[5,0,0],90,0,[[0, 0], [10, 0], [10, 2], [0, 2]]))
env.add_polygon_3D(osh.Polygon_3D("norte",[5,10,0],180,0,[[0, 0], [5, 0], [5, 2], [0, 2]]))
env.add_polygon_3D(osh.Polygon_3D("oeste",[0,10,0],-90,0,[[0, 0], [10, 0], [10, 2], [0, 2]]))
env.add_polygon_3D(osh.Polygon_3D("techo",[0,0,2],0,90,[[0, 0], [5, 0], [5, 10], [0, 10]]))
env.add_polygon_3D(osh.Polygon_3D("suelo",[0,10,0],0,-90,[[0, 0], [0, 10], [5, 10], [5, 0]]))
env.add_polygon_3D(osh.Polygon_3D("Sombra",[-5,-5,0],0,0,[[0, 0], [15, 0], [15, 5], [0, 5]],color="blue"))
#env.add_polygon_3D(osh.Polygon_3D("Sombra2",[10,-5,0],180,0,[[0, 0], [15, 0], [15, 5], [0, 5]],color="blue"))
#env.add_polygon_3D(osh.Polygon_3D("terreno",[-30,-30,-0.0],0,90,[[0, 0], [60, 0], [60, 60], [0, 60]],holes2D=[[[30,30],[35,30],[35,40],[30,40]]]))#env.add_polygon_3D(osh.Polygon_3D("terreno",[-30,-30,-0.0],0,90,[[0, 0], [60, 0], [60, 60], [0, 60]],shading=False))

sun_azimuth = math.radians(10)
sun_altitude = math.radians(40)
sun_position = np.array([math.sin(sun_azimuth) * math.cos(sun_altitude), -math.cos(sun_azimuth) * math.cos(sun_altitude), math.sin(sun_altitude)])
env.calculate_shadows(sun_position)
env.show("sunny+shadows")
