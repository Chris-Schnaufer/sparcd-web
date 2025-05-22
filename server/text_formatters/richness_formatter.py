""" Formats species richness calculations """

import dataclasses
import os

from analysis import Analysis

# pylint: disable=consider-using-f-string
@dataclasses.dataclass
class RichnessFormatter:
    """ Formats species richness calculations
    """

    @staticmethod
    def print_location_species_richness(results: tuple, res_locations: tuple, res_species: tuple, \
                                     interval_minutes: int) -> str:
        """ A table of locations vs. species showing the number of pictures of each species recorded
            at the location. The last column shows the number of species recorded at the location
            (Rich), and the last row shows total number of loations a species was recorded at
            (Richness)
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
            interval_minutes: the interval between images to be considered the same period
                            (in minutes)
        Return:
            Returns the image analysis text
        """
        result = 'LOCATIONS BY SPECIES AND LOCATION AND SPECIES RICHNESS' + os.linesep
        result += '  One record of each species per location per PERIOD' + os.linesep
        result += 'Location                          '

        for species in res_species:
            result += '{:<6s} '.format(species['name'][:6])
        result += 'Rich' + os.linesep

        for location in res_locations:
            result += '{:<28s}       '.format(location['name'])

            location_images = [one_image for one_image in results['sorted_images_dt'] if \
                                                        results['loc'] == location['idProperty']]

            horizontal_richness = 0
            for species in res_species:
                location_species_images = [one_image for one_image in location_images if \
                                        Analysis.image_has_species(one_image, species['sci_name'])]

                period = Analysis.period_for_image_list(location_species_images, interval_minutes)
                horizontal_richness = horizontal_richness + (0 if period == 0 else 1)
                result += '{:5d}  '.format(period)

            result += '{:5d}  '.format(horizontal_richness) + os.linesep

        result += 'Richness                           '

        for species in res_species:
            richness = 0
            species_images = [one_image for one_image in results['sorted_images_dt'] if \
                                        Analysis.image_has_species(one_image, species['sci_name'])]

            for location in res_locations:
                species_location_images = [one_image for one_image in species_images if \
                                                        results['loc'] == location['idProperty']]
                richness = richness + (0 if len(species_location_images) == 0 else 1)

            result += '{:5d}  '.format(richness)

        result += os.linesep + os.linesep

        return result
