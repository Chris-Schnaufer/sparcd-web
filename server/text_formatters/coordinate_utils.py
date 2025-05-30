""" Handles coordinate system conversions and measurements """

from osgeo import ogr
from osgeo import osr

LAT_LONG_WGS84_EPSG = 4326
SOUTHERN_AZ_UTM_EPSG = 26912
SOUTHERN_AZ_UTM_ZONE = '12N'

def distance_between(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """ Measures the distance between two points
    Arguments:
        lat1: the latitude of the first point
        lon1: the longitude of the first point
        lat2: the latitude of the second point
        lon2: the longitude of the second point
    Return:
        Returns the distance in meters between the two points
    """
    point1 = ogr.Geometry(ogr.wkbPoint)
    point1.AddPoint(lat1, lon1)
    point2 = ogr.Geometry(ogr.wkbPoint)
    point2.AddPoint(lat2, lon2)

    return point1.Distance(point2)

def deg2utm(lat: float, lon: float) -> tuple:
    """ Converts a point in lat-lon degrees to UTM
    Arguments:
        lat: the latitude of the point
        lon: the longitude of the point
    Return:
        Returns the converted point in an X,Y tuple
    """
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(lat, lon)

    # Lat-Lon spatial reference
    latlon_ref = osr.SpatialReference()
    latlon_ref.ImportFromEPSG(LAT_LONG_WGS84_EPSG)

    # UTM spatial reference
    utm_ref = osr.SpatialReference()
    utm_ref.ImportFromEPSG(SOUTHERN_AZ_UTM_EPSG)

    # Transform from Lat-Lon to UTM
    transform = osr.CoordinateTransformation(latlon_ref, utm_ref)

    point.Transform(transform)

    return (point.GetX(), point.GetY())
