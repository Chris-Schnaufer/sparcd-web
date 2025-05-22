""" Formats first and last species information """

import dataclasses
import os

from analysis import Analysis

# pylint: disable=consider-using-f-string
@dataclasses.dataclass
class FirstLastSpeciesFormatter:
    """ Formats search results first and last species information
    """

    @staticmethod
    def print_days_in_camera_trap(results: tuple) -> str:
        """ Formats the daty in the camera trap
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        first_dt = results[0]['image_dt']
        last_dt = results[len(results)-1]['image_dt']

        return  "NUMBER OF DAYS IN CAMERA TRAP PROGRAM = " + \
                        Analysis.get_days_span(last_dt, first_dt) + \
                        os.linesep + \
                "First picture: Year = " + first_dt.year + " Month = " + first_dt.month + \
                        " Day = " + first_dt.day + os.linesep + \
                "Last picture: Year = " + last_dt.year + " Month = " + last_dt.month + \
                        " Day = " + last_dt.day + os.linesep + \
                os.linesep

    @staticmethod
    def print_first_pic_of_each_species(results: tuple, res_locations: tuple, res_species: tuple) \
                                                                                            -> str:
        """ For each species to be analyzed, the day of the study, and the year, month, day,
        hour, minute, and location where the species was first recorded
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result = 'FIRST PICTURE OF EACH SPECIES' + os.linesep + \
                 'Species                      Days  Year Month Day Hour Minute Second Location' + \
                                                                                        os.linesep

        cur_location = None
        format_location = ''
        for one_species in res_species:
            # Some upfront preparation
            first_dt = one_species['first_image']['image_dt']
            if one_species['first_image']['loc'] != cur_location:
                cur_location = one_species['first_image']['loc']
                format_location = next([one_loc for one_loc in res_locations if \
                                        one_loc['idProperty'] == one_species['first_image']['loc']])
                if format_location:
                    format_location = cur_location['name']
                else:
                    format_location = 'Unknown'

            # Format the result
            result += '{:<28s} {:4d}  {:4d} {:4d} {:4d} {:3d} {:5d} {:6d}   {:<28s}'.\
                             format(
                                one_species['name'], \
                                Analysis.get_days_span(first_dt, \
                                                    results['sorted_images_dt'][0]['image_dt']), \
                                first_dt.year, first_dt.month, first_dt.day, first_dt.hour, \
                                first_dt.min, first_dt.sec, \
                                format_location) + \
                             os.linesep

        return result + os.linesep

    @staticmethod
    def print_last_pic_of_each_species(results: tuple, res_locations: tuple, res_species: tuple) \
                                                                                            -> str:
        """ FFor each species to be analyzed, the day of the study, and the year, month, day, hour, 
        minute, and location where the species was last recorded
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result = 'LAST PICTURE OF EACH SPECIES' + os.linesep + \
                 'Species                      Days  Year Month Day Hour Minute Second Location' + \
                                                                '                   Duration' + \
                 os.linesep

        cur_location = None
        format_location = ''
        for one_species in res_species:
            # Some upfront preparation
            first_dt = one_species['first_image']['image_dt']
            last_dt = one_species['last_image']['image_dt']
            if one_species['last_image']['loc'] != cur_location:
                cur_location = one_species['last_image']['loc']
                format_location = next([one_loc for one_loc in res_locations if \
                                        one_loc['idProperty'] == one_species['last_image']['loc']])
                if format_location:
                    format_location = cur_location['name']
                else:
                    format_location = 'Unknown'

            # Format the result
            result += '{:<28s} {:4d}  {:4d} {:4d} {:4d} {:3d} {:5d} {:6d}   {:<28s} {:4d}'.\
                             format(
                                one_species['name'], \
                                Analysis.get_days_span(first_dt, \
                                    results['sorted_images_dt'][0]['image_dt']), \
                                first_dt.year, first_dt.month, first_dt.day, first_dt.hour, \
                                first_dt.min, first_dt.sec, format_location, \
                                Analysis.get_days_span(last_dt, first_dt)) + \
                             os.linesep

        return result + os.linesep

    @staticmethod
    def print_species_accumulation_curve(results: tuple, res_species: tuple) -> str:
        """ The day of the study that a new species was recorded, the total number of new species
            records, and the name of the species that was (were) recorded
        Arguments:
            results: the results to search through
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        first_res_image = results['sorted_images_dt'][0]

        species_first_image = []
        for one_species in res_species:
            species_images = [one_image for one_image in results['sorted_images_dt'] if \
                                Analysis.image_has_species(one_image, one_species['sci_name'])]
            if species_images:
                species_first_image.append(one_species, species_images[0])

        species_first_image = sorted(species_first_image, lambda item: item[1]['image_dt'])

        result = 'SPECIES ACCUMULATION CURVE' + os.linesep + \
                 '  DAY    NUMBER    SPECIES' + os.linesep

        index = 1
        for one_set in species_first_image:
            result += '{:5d}     {:3d}      {:s}'.format( \
                    Analysis.get_days_span(one_set[1]['image_dt'], first_res_image['image_dt']), \
                    index, \
                    one_set[0]['name']) + \
                os.linesep
            index += 1

        return result + os.linesep
