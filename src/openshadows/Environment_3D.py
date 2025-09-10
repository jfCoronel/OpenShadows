import pyvista

class Environment_3D():
    def __init__(self):
        self.pol_3D = []
        self.pol_sunny = []
        self.sunny_fraction = []

    def add_polygon_3D(self, polygon_3D):
        self.pol_3D.append(polygon_3D)
        self.sunny_fraction.append(1.0)

    def show(self, window=False):
        pyvista = Pyvista_Screen(window=window)
        for polygon_3D in self.pol_3D:
            if polygon_3D.visible:
                pyvista.add_polygon(polygon_3D)
        pyvista.show()
    
    def calculate_shadows(self, sun_position):
        self.pol_sunny = []
        self.sunny_fraction = []
        for polygon in self.pol_3D:
            if polygon.sunny == True:
                sunny_polygons = polygon.get_sunny_polygon3D(self, sun_position)
                if sunny_polygons != None:
                    sunny_area = 0
                    for sunny_polygon in sunny_polygons:
                        self.pol_sunny.append(sunny_polygon)
                        sunny_area += sunny_polygon.area
                    self.sunny_fraction.append(sunny_area/polygon.area)
                else:
                    self.sunny_fraction.append(0)  # No sunny area
            else:
                self.sunny_fraction.append(float('nan'))


class Pyvista_Screen():
    def __init__(self, window=False, default_color="white"):
        self.default_color = default_color
        self.window = window
        self.text_actor = None
        if window:
            pyvista.set_jupyter_backend("none")
            self.plot = pyvista.Plotter(notebook=False)
            self.plot.enable_mesh_picking(callback=self.click_callback,style="surface",color="pink",show_message=False)
            self.plot.add_axes_at_origin(labels_off=True)
        else:
            pyvista.set_jupyter_backend("trame")
            self.plot = pyvista.Plotter(notebook=True)
            self.plot.add_axes_at_origin()
        #self.plot.show_grid()

    def click_callback(self, mesh): 
        if self.text_actor:
            self.plot.remove_actor(self.text_actor) 
        name = mesh.field_data["name"]
        self.text_actor = self.plot.add_text(name)
        print("Clicked on: ", name)
        #print(mesh)
    
    def add_polygon(self, polygon_3D):
        mesh = polygon_3D.get_pyvista_mesh().triangulate()
        mesh.field_data["name"] = polygon_3D.name
        self.plot.add_mesh(mesh, show_edges=False, color=polygon_3D.color, opacity=polygon_3D.opacity)
        self.plot.add_lines(polygon_3D.get_pyvista_polygon_border(), color="black", width=5, connected=True)
        if (polygon_3D.has_holes()):
            for i in range(len(polygon_3D.holes2D)):
                self.plot.add_lines(polygon_3D.get_pyvista_hole_border(i), color="black", width=5, connected=True)

    def show(self):
        if self.window:
            self.plot.show()
        else:
            self.plot.show(jupyter_backend="client")
        

