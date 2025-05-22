""" Formats species with location/utm/latlng coordinates """

import dataclasses
import os

from analysis import Analysis

# pylint: disable=consider-using-f-string
@dataclasses.dataclass
class SpeciesLocCoordFormatter:
    """ Formats species with location/utm/latlng coordinates
    """

    @staticmethod
    def print_species_by_loc_with_utm(results: tuple, res_species: tuple) \
                                                                                            -> str:
        """ For each species a list of locations where the species was recorded, and the UTM and
            elevation of the location.
        Arguments:
            results: the results to search through
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES BY LOCATION WITH UTM AND ELEVATION' + os.linesep
        for species in res_species:
            species_images = [one_image for one_image in results['sorted_images_dt'] if \
                                        Analysis.image_has_species(one_image, species['sci_name'])]
            result += species['name'] + os.linesep

            result += 'Location                        UTMe-w   UTMn-s    Elevation   Lat        ' \
                      'Long' + os.linesep
            for location in Analysis.locations_for_image_list(species_images):
                utm_coord = SanimalAnalysisUtils.Deg2UTM(float(location['latProperty']), \
                                                                    float(location['lngProperty']))

                # We format the easting then northing of the UTM coordiantes
                result += '{:<28s}  {:8d}  {:8d}  {:7.0f}      {:8.6f}  {:8.6f}'. \
                                format( \
                                    location['name'], \
                                    round(utm_coord[0]), round(utm_coord[1]), \
                                    location['elevationProperty'], \
                                    float(location['latProperty']), float(location['lngProperty']) \
                                ) + os.linesep

            result += os.linesep

        return result
