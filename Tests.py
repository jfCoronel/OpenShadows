import openshadows as osh

env = osh.Environment_3D()
p_1 = osh.Polygon_3D([0,0,0],0,0,[[0, 0], [1, 0], [1, 1], [0, 1]])  
env.add_polygon_3D(p_1)
p_2 = osh.Polygon_3D([0,0,0],90,0,[[0, 0], [1, 0], [1, 1], [0, 1]],color="red")  
env.add_polygon_3D(p_2)
p_3 = osh.Polygon_3D([0,0,0],-90,0,[[0, 0], [1, 0], [1, 1], [0, 1]],color="blue")  
env.add_polygon_3D(p_3)
p_4 = osh.Polygon_3D([0,0,0],180,0,[[0, 0], [1, 0], [1, 1], [0, 1]],color="green",opacity=0.5)  
env.add_polygon_3D(p_4)

env.show(window=True)