""" Formats first and last species information """

import datetime
import math
import os

@dataclasses.dataclass
class FirstLastSpeciesFormatter:
    """ Formats search results first and last species information
    """

    @staticmethod
    def printDaysInCameraTrap(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ Formats the daty in the camera trap
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        first_dt = results[0]['image_dt'];
        last_dt = results[len(results)-1]['image_dt'];

        return  "NUMBER OF DAYS IN CAMERA TRAP PROGRAM = " + \
                        get_days_span(last_dt, first_dt) + \
                        os.linesep + \
                "First picture: Year = " + first_dt.year + " Month = " + first_dt.month + \
                        " Day = " + first_dt.day + os.linesep + \
                "Last picture: Year = " + last_dt.year + " Month = " + last_dt.month + \
                        " Day = " + lastday + os.linesep + \
                os.linesep

    @staticmethod
    def printFirstPicOfEachSpecies(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ For each species to be analyzed, the day of the study, and the year, month, day, hour, minute, 
        and location where the species was first recorded
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result = 'FIRST PICTURE OF EACH SPECIES' + os.linesep + \
                 'Species                      Days  Year Month Day Hour Minute Second Location' + os.linesep

        cur_location = None
        format_location = ''
        for one_species in res_species:
            # Some upfront preparation
            first_dt = one_species['first_image']['image_dt']
            if one_species['first_image']['loc'] != cur_location:
                cur_location = one_species['first_image']['loc']
                format_location = next([one_loc for one_loc in res_locations if \
                                        one_loc['idProperty'] = one_species['first_image']['loc']] else None)
                if format_location:
                    format_location = cur_location['name']
                else:
                    format_location = 'Unknown'

            # Format the result
            result += '{:<28s} {:4d}  {:4d} {:4d} {:4d} {:3d} {:5d} {:6d}   {:<28s}'.\
                             format(
                                one_species['name'], \
                                get_days_span(first_dt, results['sorted_images_dt'][0]['image_dt']), \
                                first_dt.year, first_dt.month, first_dt.day, first_dt.hour, first_dt.min, first_dt.sec, \
                                format_location) + \
                             os.linesep

        return result + os.linesep

    @staticmethod
    def printLastPicOfEachSpecies(results: tuple, res_locations: tuple, res_species: tuple) -> str:
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
                                        one_loc['idProperty'] = one_species['last_image']['loc']] else None)
                if format_location:
                    format_location = cur_location['name']
                else:
                    format_location = 'Unknown'

            # Format the result
            result += '{:<28s} {:4d}  {:4d} {:4d} {:4d} {:3d} {:5d} {:6d}   {:<28s} {:4d}'.\
                             format(
                                one_species['name'], \
                                get_days_span(first_dt, results['sorted_images_dt'][0]['image_dt']), \
                                first_dt.year, first_dt.month, first_dt.day, first_dt.hour, first_dt.min, first_dt.sec, \
                                format_location, get_days_span(last_dt, first_dt)) + \
                             os.linesep

        return result + os.linesep

    @staticmethod
    def printSpeciesAccumulationCurve(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ The day of the study that a new species was recorded, the total number of new species records,
        and the name of the species that was (were) recorded
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        first_res_image = results['sorted_images_dt'][0]

        result = 'SPECIES ACCUMULATION CURVE' + os.linesep + \
                 '  DAY    NUMBER    SPECIES' + os.linesep

        int index = 1;
        for one_species in res_species:
            result += '{:5d}     {:3d}      {:s}'.
                        format( \
                            get_days_span(one_species['first_image']['image_dt'], first_res_image['image_dt']), \
                            index, \
                            one_species['name']) + \
                        os.linesep

            toReturn.append(String.format("%5d     %3d      %s\n", SanimalAnalysisUtils.daysBetween(analysis.getImagesSortedByDate().get(0).getDateTaken(), entry.getValue().getDateTaken()) + 1, ++number, entry.getKey().getName()));

        return result + os.linesep
