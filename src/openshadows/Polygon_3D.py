import math
import numpy as np
from shapely.geometry import Polygon
import pyvista
from triangle import triangulate

class Polygon_3D():
    def __init__(self, origin, azimuth, altitude, polygon2D, holes2D=[], color="white", opacity=1.0):
        self.origin = np.array(origin)
        self.azimuth = azimuth
        self.altitude = altitude
        self.polygon2D = polygon2D
        self.azimuth_rad = math.radians(self.azimuth)
        self.altitude_rad = math.radians(self.altitude)
        self.normal_vector = np.array((math.cos(self.altitude_rad)*math.sin(self.azimuth_rad),
                                       -math.cos(self.altitude_rad) *
                                       math.cos(self.azimuth_rad),
                                       math.sin(self.altitude_rad)))
        self.x_axis = np.array((math.cos(self.azimuth_rad),
                                math.sin(self.azimuth_rad),
                                0))
        self.y_axis = np.cross(self.normal_vector, self.x_axis)
        self.polygon3D = self._convert_2D_to_3D_(self.polygon2D)
        self.holes2D = holes2D
        self.holes3D = []
        for hole in self.holes2D:
            self.holes3D.append(self._convert_2D_to_3D_(hole))
        self.shapely_polygon = Polygon(self.polygon2D, self.holes2D)
        self.area = self.shapely_polygon.area
        self.equation_d = np.sum(self.normal_vector*self.origin)
        self.color = color
        self.opacity = opacity

    def has_holes(self):
        if (len(self.holes2D) > 0):
            return True
        else:
            return False

    def is_coplanar(self, polygon_3D):
        if np.allclose(self.normal_vector, polygon_3D.normal_vector):  # same normal verctor
            if np.isclose(np.sum(self.normal_vector*polygon_3D.origin), self.equation_d):  # in the plane
                return True
            else:
                return False
        else:
            return False

    def get_advanced_polygon(self):
        advanced_origin = self.origin + self.normal_vector*1e-4
        advanced = Polygon_3D(advanced_origin, self.azimuth,
                              self.altitude, self.polygon2D, self.holes2D)
        return advanced

    def _convert_2D_to_3D_(self, pol_2D):
        pol_3D = []
        for vertex in pol_2D:
            v_loc = (self.origin[0] + vertex[0] * math.cos(self.azimuth_rad)
                     - vertex[1] * math.sin(self.altitude_rad) *
                     math.sin(self.azimuth_rad),
                     self.origin[1] + vertex[0] * math.sin(self.azimuth_rad)
                     + vertex[1] * math.sin(self.altitude_rad) *
                     math.cos(self.azimuth_rad),
                     self.origin[2] + vertex[1] * math.cos(self.altitude_rad))
            pol_3D.append(v_loc)
        return pol_3D

    def is_facing_sun(self, sun_position):
        escalar_p = np.sum(self.normal_vector*sun_position)
        if escalar_p >= 1e-10:
            return True
        else:
            return False

    def get_pyvista_mesh(self):
        if self.has_holes():
            (points, faces) = self._triangulate_()
            return pyvista.PolyData(points, faces=faces)
        else:
            faces = [len(self.polygon3D), *range(0, len(self.polygon3D))]
            return pyvista.PolyData(np.array(self.polygon3D), faces)

    def _triangulate_(self):
        def edge_idxs(nv):
            i = np.append(np.arange(nv), 0)
            return np.stack([i[:-1], i[1:]], axis=1)

        nv = 0
        verts, edges = [], []
        for loop in (self.polygon2D, *self.holes2D):
            verts.append(loop)
            edges.append(nv + edge_idxs(len(loop)))
            nv += len(loop)

        verts, edges = np.concatenate(verts), np.concatenate(edges)
        # Triangulate needs to know a single interior point for each hole
        holes = np.array([np.mean(h, axis=0) for h in self.holes2D])
        # Because triangulate is a wrapper around a C library the syntax is a little weird, 'p' here means planar straight line graph
        d = triangulate(dict(vertices=verts, segments=edges, holes=holes), opts='p')

        # Convert back to pyvista
        v, f = d['vertices'], d['triangles']
        nv, nf = len(v), len(f)
        points = np.concatenate([v, np.zeros((nv, 1))], axis=1)
        # Creo que lo tengo que hacer en 2D y luego pasarlo a 3D
        faces = np.concatenate([np.full((nf, 1), 3), f], axis=1).reshape(-1)
        return (self._convert_2D_to_3D_(points), faces)

    def get_pyvista_polygon_border(self):
        return np.vstack([np.array(self.polygon3D), self.polygon3D[0]])

    def get_pyvista_hole_border(self, i):
        return np.vstack([np.array(self.holes3D[i]), self.holes3D[i][0]])

    def get_sunny_shapely_polygon(self, shadow_polygons_list, sun_position):
        if not self.is_facing_sun(sun_position):
            return None
        else:
            # Calculate projected shadows
            shadows_2D = []
            for shadow_polygon in shadow_polygons_list:
                if shadow_polygon.is_facing_sun(sun_position):
                    shadows_2D.append(self._calculate_shapely_2D_projected_(
                        shadow_polygon, sun_position))
            # Calculate sunny polygon
            sunny_polygon = self.shapely_polygon
            for shadow_polygon in shadows_2D:
                if shadow_polygon != None:
                    sunny_polygon = sunny_polygon.difference(shadow_polygon)
            if sunny_polygon.is_empty:
                sunny_polygon = None
            return sunny_polygon

    def get_sunny_polygon3D(self, shadow_polygons_list, sun_position):
        return self._shapely_multipolygon_to_polygons_3D_(self.get_sunny_shapely_polygon(shadow_polygons_list, sun_position))

    def get_shadow_shapely_polygon(self, shadow_polygons_list, sun_position):
        sunny_polygon = self.get_sunny_shapely_polygon(
            shadow_polygons_list, sun_position)
        if sunny_polygon == None:
            return self.shapely_polygon
        else:
            shadow_polygon = self.shapely_polygon.difference(sunny_polygon)
            if shadow_polygon.is_empty:
                return None
            else:
                return shadow_polygon

    def get_shadow_polygon3D(self, shadow_polygons_list, sun_position):
        return self._shapely_multipolygon_to_polygons_3D_(self.get_shadow_shapely_polygon(shadow_polygons_list, sun_position))

    def _calculate_shapely_2D_projected_(self, polygon_to_project, sun_position):
        projected_polygon = []
        n_points = 0
        k_total = 0
        for point in polygon_to_project.polygon3D:
            k = (np.sum(self.normal_vector * point)-self.equation_d) / \
                (np.sum(self.normal_vector * sun_position))
            projected_point_3D = point - k * sun_position
            vector = projected_point_3D - self.origin
            projected_point_2D = np.array(
                [np.sum(self.x_axis*vector), np.sum(self.y_axis*vector)])
            projected_polygon.append(projected_point_2D)
            if (k > -1e-6):  # Por delante o en el plano
                n_points += 1
            if (k > 0.1):  # 10 cm
                k_total += k
        # TODO: que ocurre cuando tengo planos cortantes ...
        if n_points > 2 and k_total > 0.1:
            return Polygon(projected_polygon)
        else:
            return None

    # Para dibujarlos en 3D
    def _shapely_multipolygon_to_polygons_3D_(self, shapely_polygon):
        polygon_list = []
        if shapely_polygon != None:
            if shapely_polygon.geom_type == 'MultiPolygon':
                polygons = list(shapely_polygon.geoms)
                for pol in polygons:
                    polygon_list.append(self._shapely_to_polygon_3D_(pol))
            elif shapely_polygon.geom_type == 'Polygon':
                polygon_list.append(
                    self._shapely_to_polygon_3D_(shapely_polygon))
        return polygon_list

    def _shapely_to_polygon_3D_(self, shapely_pol):
        exterior_pol = np.asarray(shapely_pol.exterior.coords)
        holes = [(np.asarray(ring.coords)) for ring in shapely_pol.interiors]
        return Polygon_3D(self.origin, self.azimuth, self.altitude, exterior_pol, holes)
