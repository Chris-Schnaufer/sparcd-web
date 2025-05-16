""" Formats species with location/utm/latlng coordinates """

import os

import Analysis

@dataclasses.dataclass
class SpeciesLocCoordFormatter:
    """ Formats species with location/utm/latlng coordinates
    """

    @staticmethod
    def printSpeciesByLocWithUTM(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ For each species a list of locations where the species was recorded, and the UTM and
            elevation of the location.
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES BY LOCATION WITH UTM AND ELEVATION' + os.linesep
        for species in res_species:
            species_images = [one_image for one_image in results['sorted_images_dt'] if \
                                            Analysis.image_has_species(one_image, species['sci_name'])]
            result += species['name'] + os.linesep

            result += 'Location                        UTMe-w   UTMn-s    Elevation   Lat        Long' + os.linesep
            for location in cur_locations:
                utm_coord = SanimalAnalysisUtils.Deg2UTM(float(location['latProperty']), float(location['lngProperty']));

                # We format the easting then northing of the UTM coordiantes
                result += '{:<28s}  {:8d}  {:8d}  {:7.0f}      {:8.6f}  {:8.6f}'. \
                                format( \
                                        location['name'], \
                                        math.round(utm_coord[0]), math.round(utm_coord[1]), \
                                        location['elevationProperty'], \
                                        float(location['latProperty']), float(location['lngProperty']) \
                                      ) + os.linesep

            result += os.linesep

        return result
