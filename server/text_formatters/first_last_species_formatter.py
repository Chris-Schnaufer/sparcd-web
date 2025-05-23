""" Formats first and last species information """

import dataclasses
import os

from .analysis import Analysis
from .results import Results

# pylint: disable=consider-using-f-string
@dataclasses.dataclass
class FirstLastSpeciesFormatter:
    """ Formats search results first and last species information
    """

    @staticmethod
    def print_days_in_camera_trap(results: Results) -> str:
        """ Formats the daty in the camera trap
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        first_dt = results.get_first_image()['image_dt']
        last_dt = results.get_last_image()['image_dt']

        return  "NUMBER OF DAYS IN CAMERA TRAP PROGRAM = " + \
                        Analysis.get_days_span(last_dt, first_dt) + \
                        os.linesep + \
                "First picture: Year = " + first_dt.year + " Month = " + first_dt.month + \
                        " Day = " + first_dt.day + os.linesep + \
                "Last picture: Year = " + last_dt.year + " Month = " + last_dt.month + \
                        " Day = " + last_dt.day + os.linesep + \
                os.linesep

    @staticmethod
    def print_first_pic_of_each_species(results: Results) -> str:
        """ For each species to be analyzed, the day of the study, and the year, month, day,
        hour, minute, and location where the species was first recorded
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'FIRST PICTURE OF EACH SPECIES' + os.linesep + \
                 'Species                      Days  Year Month Day Hour Minute Second Location' + \
                                                                                        os.linesep

        cur_location = None
        format_location = ''
        for one_species in results.get_species():
            # Some upfront preparation
            first_dt = one_species['first_image']['image_dt']

            # Look up the name of the location using the site ID
            if one_species['first_image']['loc'] != cur_location:
                cur_location = one_species['first_image']['loc']
                format_location = next([one_loc for one_loc in results.get_locations() if \
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
                                                    results.get_first_image()['image_dt']), \
                                first_dt.year, first_dt.month, first_dt.day, first_dt.hour, \
                                first_dt.min, first_dt.sec, \
                                format_location) + \
                             os.linesep

        return result + os.linesep

    @staticmethod
    def print_last_pic_of_each_species(results: Results) -> str:
        """ FFor each species to be analyzed, the day of the study, and the year, month, day, hour, 
        minute, and location where the species was last recorded
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'LAST PICTURE OF EACH SPECIES' + os.linesep + \
                 'Species                      Days  Year Month Day Hour Minute Second Location' + \
                                                                '                   Duration' + \
                 os.linesep

        cur_location = None
        format_location = ''
        for one_species in results.get_species():
            # Some upfront preparation
            first_dt = one_species['first_image']['image_dt']
            last_dt = one_species['last_image']['image_dt']

            # Look up the location name by site ID
            if one_species['last_image']['loc'] != cur_location:
                cur_location = one_species['last_image']['loc']
                format_location = next([one_loc for one_loc in results.get_locations() if \
                                        one_loc['idProperty'] == one_species['last_image']['loc']])
                if format_location:
                    format_location = cur_location['name']
                else:
                    format_location = 'Unknown'

            # Format the result
            result += '{:<28s} {:4d}  {:4d} {:4d} {:4d} {:3d} {:5d} {:6d}   {:<28s} {:4d}'.\
                             format(
                                one_species['name'], \
                                Analysis.get_days_span(last_dt, \
                                    results.get_first_image()['image_dt']), \
                                last_dt.year, last_dt.month, last_dt.day, last_dt.hour, \
                                last_dt.min, last_dt.sec, format_location, \
                                Analysis.get_days_span(first_dt, last_dt)) + \
                             os.linesep

        return result + os.linesep

    @staticmethod
    def print_species_accumulation_curve(results: tuple) -> str:
        """ The day of the study that a new species was recorded, the total number of new species
            records, and the name of the species that was (were) recorded
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES ACCUMULATION CURVE' + os.linesep + \
                 '  DAY    NUMBER    SPECIES' + os.linesep

        for index, one_species in enumerate(results.get_species()):
            result += '{:5d}     {:3d}      {:s}'.format( \
                    Analysis.get_days_span(one_species['first_image']['image_dt'], \
                                                        results.get_first_image()['image_dt']), \
                    index + 1, \
                    one_species['name']) + \
                os.linesep

        return result + os.linesep
