""" Formats header information """

import os

@dataclasses.dataclass
class HeaderFormatter:
    """ Formats search results headers
    """

    @staticmethod
    def printLocations(results: tuple, res_locations: dict) -> str:
        """ Formats the locations header information
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
        Return:
            Returns the location header text
        """
        loc_names = [res_locations[one_key]['nameProperty'] for one_key in res_locations.keys() \
                                                    if one_key != "unknown" else "Unkown"]

        return "LOCATIONS " + str(len(res_locations.keys())) + os.linesep + \
            ", ".join(loc_names) + os.linesep + os.linesep

    @staticmethod
    def printSpecies(results: tuple, res_species: dict) -> str:
        """ Formats the species header information
        Arguments:
            results: the results to search through
            res_species: all distinct result species
        Return:
            Returns the species header text
        """
        species_names = [res_species[one_key]['name'] for one_key in res_species.keys() \
                                                    if one_key != "unknown" else "Unknown"]

        return "SPECIES " + str(len(res_species.keys())) + os.linesep + \
            ", ".join(species_names) + os.linesep + os.linesep

    @staticmethod
    def printImageAnalysisHeader(results: tuple, res_locations: dict, res_species: dict) -> str:
        """ Formats the image analysis header information
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species
        Return:
            Returns the image analysis text
        """
        total_images = 0
        for one_result in results:
            total_images += len(one_result[1])

        sorted_images = []

        return "FOR ALL SPECIES AT ALL LOCATIONS " + os.linesep + \
            "Number of pictures processed = " + str(total_images) + os.linesep + \
            "Number of pictures used in activity calculation = " + \
                                activityForImageList() + os.linesep + \
            "Number of independent pictures used in analysis = " + \
                                periodForImageList() + os.linesep + \
            "Number of sequential pictures of same species at same location within a PERIOD = " + \
                                 + os.linesep + \
            os.linesep
