""" Formats occurrence of species in locations """

import os
import sys

import Analysis

@dataclasses.dataclass
class OccuranceFormatter:
    """ Formats occurrence of species in locations
    """

    @staticmethod
    def printCHISqAnalysisOfPairedSpecieFreq(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ A table of location x location showing the results of a chi-square test of species frequencies
            at each pair of locations. The null hypothesis H0: Species frequencies are independent of
            location is tested. If two locations have similar species frequencies then the H0 is rejected
            and an "R" is shown in the table. Otherwise a "-" shows the locations have independent species
            frequencies
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result = ''

        result += 'CHI-SQUARE ANALYSIS OF PAIRED SITES SPECIES FREQUENCIES' + os.linesep
        result += '  H0: Species frequencies are independent of site' + os.linesep
        result += '  Reject null hypothesis = R, Accept null hypothesis = -' + os.linesep
        result += 'Sites                      ' + os.linesep
        result += 'No idea what these numbers are' + os.linesep + os.linesep

        return result

    @staticmethod
    def printCoOccuranceMatrix(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ 
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result += 'SPECIES CO-OCCURRENCE MATRIX' + os.linesep
        result += '  The number of locations each species pair co-occurs' + os.linesep
        result += '                            '

        for species in res_species:
            result += '{:3s} '.format(species['name'][:3])
        result += os.linesep

        for species in res_species:
            result += '{:<28s}'.format(species['name'])
            species_images = [one_image for one_image in results['sorted_images_dt'] if \
                                                Analysis.image_has_species(one_image, species['sci_name'])]

            for other_species in res_species:
                other_species_images = [one_image for one_image in results['sorted_images_dt'] if \
                                                Analysis.image_has_species(one_image, other_species['sci_name'])]

                numLocations = 0;

                for location in res_locations:
                    species_location_images = [one_image for one_image in species_images if \
                                                    one_image['loc'] == location['idProperty']]
                    other_species_location_images = [one_image for one_image in other_species_images if \
                                                    one_image['loc'] == location['idProperty']]

                    if species_location_images and other_species_location_images:
                        numLocations = numLocations + 1;

                result += '%3d '.format(numLocations)

            result += os.linesep

        result += os.linesep

        return result

    @staticmethod
    def printAbsensePresenceMatrix(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ Table of species presence or absence at locations
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result = 'ABSENCE-PRESENCE MATRIX' + os.linesep
        result += '  Species vs locations matrix (locations in alphabetical order)' + os.linesep
        result += '          Species ('
        result += '{:3d}'.format(len(res_species))
        result += ')               Locations ('
        result += '{:3d}'.format(len(res_locations))
        result += os.linesep
        result += '                            '

        alphabetical = sorted(res_locations, key=lambda loc: loc['idProperrty'])

        for loc_num in range(1, len(alphabetical) + 1):
            result += '{:2d} '.format(loc_num)
        result += os.linesep

        for species in res_species:
            result += '{:<28s}'.format(species['name'])

            species_images = [one_image for one_image in results['sorted_images_dt'] if \
                                                Analysis.image_has_species(one_image, species['sci_name'])]

            for location in res_location:
                species_location_images = [one_image for one_image in species_images if \
                                                    one_image['loc'] == location['idProperty']]
                result += '%2d '.format((len(species_location_images) == 0 ? 0 : 1))

            result += os.linesep

        result += os.linesep

        return result

    @staticmethod
    def printMaxMinSpeciesElevation(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ Prints the species min amd max elevation table
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES MIN AND MAX ELEVATION' + os.linesep
        result += '  Species vs locations matrix (location sorted from low to high elevation)' + os.linesep
        result += '          Species ('
        result += '{:3d}'.format(len(res_species))
        result += ')               Locations ('
        result += '{:3d}'.format(len(res_locations))
        result += os.linesep
        result += '                            '

        elevation_locs = sorted(res_locations, key=lambda loc: float(loc['elevationProperty']))

        for location in range(1, len(elevation_locs) + 1):
            result += '{:2d} '.format(location)

        result += os.linesep

        for species in res_species:
            result += '{:<28s}'.format(species['name'])

            species_images = [one_image for one_image in results['sorted_images_dt'] if \
                                                Analysis.image_has_species(one_image, species['sci_name'])]

            for location in res_location:
                species_location_images = [one_image for one_image in species_images if \
                                                    one_image['loc'] == location['idProperty']]
                result += '{:2d} '.format((len(species_location_images) == 0 ? 0 : 1))

            result += os.linesep

        result += os.linesep

        result += '  List of elevations and locations' + os.linesep

        for loc_index, location in enumerate(res_location):
            result += ' {:2d} {:5.0f} '.format(loc_index + 1, location['elevationProperty']) + \
                                location['name'] + os.linesep
        result += os.linesep

        result += '  Minimum and maximum elevation for each species' + os.linesep
        result += '   SPECIES                     Min   Max' + os.linesep
        for species in res_species:
            minElevation = sys.float_info.max
            maxElevation = 0.0

            species_images = [one_image for one_image in results['sorted_images_dt'] if \
                                                Analysis.image_has_species(one_image, species['sci_name'])]

            for location in res_location:
                species_location_images = [one_image for one_image in species_images if \
                                                    one_image['loc'] == location['idProperty']]

                if species_location_images:
                    elevation = float(location['elevationProperty'])
                    if elevation > maxElevation:
                        maxElevation = elevation
                    if elevation < minElevation:
                        minElevation = elevation

            result += '{:<28s} {:5.0f} {:5.0f}'.format(species['name'], minElevation, maxElevation) + os.linesep

        result += os.linesep

        return result

    @staticmethod
    def printNativeOccupancy(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ The list of species analyzed, and for each species the Fraction of locations Occupied
            calculated by computing the number of locations occupied by the species divided by the total
            number of location shown in (). For each species the Number of locations Occupied is also
            given. The Fraction of locations Occupied is referred to as Naive occupancy or Naive proportion
            of locations occupied.The list is presnted from the greatest porportion of locations occupied
            to least locations occupied
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result = 'NAIVE OCCUPANCY' + os.linesep
        result += '  Species naive location occupancy proportion' + os.linesep
        result += '  To create occupancy matrix run program OccupancyMatrix' + os.linesep
        result += '                               Fraction of locations   Number of locations' + os.linesep
        result += 'Species                              Occupied             Occupied (' + \
                            '{:3d}'.format(len(res_locations)) + os.linesep

        totalLocations = len(res_locations)

        pairs_to_print = []

        for species in res_species:
            species_images = [one_image for one_image in results['sorted_images_dt'] if \
                                                Analysis.image_has_species(one_image, species['sci_name'])]

            locationsWithSpecies = 0
            for location in res_location:
                species_location_images = [one_image for one_image in species_images if \
                                                    one_image['loc'] == location['idProperty']]
                if species_location_images:
                    locationsWithSpecies = locationsWithSpecies + 1;

            # Add a tuple of the fraction, and the formatted string to print out
            pairs_to_print.append((float(locationsWithSpecies) / float(totalLocations),
                                   '{:<28s}           {:5.3f}                  {:3d}'.format( \
                                        species['name'], float(locationsWithSpecies) / float(totalLocations),
                                        locationsWithSpecies) + os.linesep
                                  ))

        sorted_pairs_to_print = sorted(pairs_to_print, key=lambda pair: pair[0])

        for to_print in sorted_pairs_to_print:
            resut += toPrint[1]

        result += os.linesep

        return result
