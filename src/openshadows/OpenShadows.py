import pyvista
from shapely.geometry import Polygon
from triangle import triangulate


class Environment_3D():
    def __init__(self):
        self.surfaces = []
#        self.pol_types = []
#        self.polygon_surface = []  # Reference to the surface object
#        self.sunny_list = []
#        self.sunny_surface = []  # Reference to the sunny surface object
#        self.shadow_list = []

    def add_surface(self, surface_3D):
        self.surfaces.append(surface_3D)

    def show(self, hide=[], opacity=1, window=False, sun_position=None):
        pyvista = Pyvista_Screen(window=window)
        for surface in self.surfaces:
            if surface.type == "Opening" and "Opening" not in hide:
                pyvista.add_polygon(surface.polygon,surface.component.parameter("name").value,surface.type, "blue", opacity*0.6)
            elif surface.type == "Virtual_surface" and "Virtual_surface" not in hide:
                pyvista.add_polygon(surface.polygon,surface.component.parameter("name").value,surface.type, "red", opacity*0.4)
            elif surface.type == "Interior_surface" and "Interior_surface" not in hide:
                pyvista.add_polygon(surface.polygon,surface.component.parameter("name").value,surface.type, "green", opacity)
            elif surface.type == "Exterior_surface" and "Exterior_surface" not in hide:
                pyvista.add_polygon(surface.polygon,surface.component.parameter("name").value,surface.type, "white", opacity)
            elif surface.type == "Underground_surface" and "Underground_surface" not in hide:
                pyvista.add_polygon(surface.polygon,surface.component.parameter("name").value,surface.type, "brown", opacity)
            elif surface.type == "Shadow_surface" and "Shadow_surface" not in hide:
                pyvista.add_polygon(surface.polygon,surface.component.parameter("name").value,surface.type, "cyan", opacity)
        
        if sun_position is not None:
            shadow_surfaces = []
            for surface in self.surfaces:
                if surface.shadow == True:
                    shadow_surfaces.append(surface.polygon)
            shadow_polygons = []
            for surface in self.surfaces:
                if surface.sunny == True:
                    shadow_polygons.append(surface.get_shadow_polygon3D(shadow_surfaces, sun_position))
            shadow_polygons = sum(shadow_polygons, [])
            
            for polygon in shadow_polygons:
                pyvista.add_polygon(polygon.get_advanced_polygon(), color="gray")

        pyvista.show()

    def get_sunny_fraction(self, component, sun_position):
        shadow_surfaces = []
        for surface in self.surfaces:
            if surface.shadow == True:
                shadow_surfaces.append(surface.polygon)
        for surface in self.surfaces:
            if surface.component == component:
                sunny_fraction_polygon = surface.get_sunny_shapely_polygon(shadow_surfaces, sun_position)
                if sunny_fraction_polygon == None:
                    return 0.0
                else:
                    return sunny_fraction_polygon.area/surface.polygon.area



class Pyvista_Screen():
    def __init__(self, window=False, default_color="white"):
        self.default_color = default_color
        self.window = window
        self.text_actor = None
        if window:
            pyvista.set_jupyter_backend("none")
            self.plot = pyvista.Plotter(notebook=False)
            self.plot.enable_mesh_picking(callback=self.click_callback,style="surface",color="red",show_message=False)
            self.plot.add_axes_at_origin(labels_off=True)
        else:
            pyvista.set_jupyter_backend("trame")
            self.plot = pyvista.Plotter(notebook=True)
            self.plot.add_axes_at_origin()
        #self.plot.show_grid()

    def click_callback(self, mesh): 
        if self.text_actor:
            self.plot.remove_actor(self.text_actor) 
        self.text_actor = self.plot.add_text(f"{mesh.field_data['surface'][0]} ({mesh.field_data['surface'][1]})")
    
    def add_polygon(self, polygon, surface_name="name", surface_type="type", color=None, opacity=1):
        if color == None:
            color = self.default_color
        if polygon != None:
            mesh = polygon.get_pyvista_mesh().triangulate()
            mesh.field_data["surface"] = [surface_name,surface_type]
            self.plot.add_mesh(mesh, show_edges=False, color=color, opacity=opacity)
            # Calcular centroide para la etiqueta
            #self.nombres_poligonos["hola"] = mesh
            #centroid = np.mean(np.array(mesh.points), axis=0)
            #self.plot.add_point_labels([centroid], ["Hola"], font_size=24, text_color='black')
            self.plot.add_lines(polygon.get_pyvista_polygon_border(), color="black", width=5, connected=True)
            if (polygon.has_holes()):
                for i in range(len(polygon.holes2D)):
                    self.plot.add_lines(polygon.get_pyvista_hole_border(i), color="black", width=5, connected=True)

    # def add_polygons(self, polygons_list, color=None, opacity=1):
    #     for polygon in polygons_list:
    #         if color == None:
    #             self.add_polygon(polygon, self.default_color, opacity=opacity)
    #         else:
    #             self.add_polygon(polygon, color, opacity=opacity)

    def show(self):
        if self.window:
            self.plot.show()
        else:
            self.plot.show(jupyter_backend="client")
        

