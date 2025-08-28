import pyvista

class Environment_3D():
    def __init__(self):
        self.pol_3D = []

    def add_polygon_3D(self, polygon_3D):
        self.pol_3D.append(polygon_3D)

    def show(self, window=False):
        pyvista = Pyvista_Screen(window=window)
        for polygon_3D in self.pol_3D:
            pyvista.add_polygon(polygon_3D)   
        pyvista.show()

        # if sun_position is not None:
        #     shadow_surfaces = []
        #     for surface in self.pol_3D:
        #         if surface.shadow == True:
        #             shadow_surfaces.append(surface.polygon)
        #     shadow_polygons = []
        #     for surface in self.pol_3D:
        #         if surface.sunny == True:
        #             shadow_polygons.append(surface.get_shadow_polygon3D(shadow_surfaces, sun_position))
        #     shadow_polygons = sum(shadow_polygons, [])
            
        #     for polygon in shadow_polygons:
        #         pyvista.add_polygon(polygon.get_advanced_polygon(), color="gray")

    def get_sunny_fraction(self, component, sun_position):
        shadow_surfaces = []
        for surface in self.pol_3D:
            if surface.shadow == True:
                shadow_surfaces.append(surface.polygon)
        for surface in self.pol_3D:
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
        self.text_actor = self.plot.add_text(f"Polygon 3D")
    
    def add_polygon(self, polygon_3D):
        mesh = polygon_3D.get_pyvista_mesh().triangulate()
        #mesh.field_data["surface"] = [...] Permitiria guardar información adicional
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
        

