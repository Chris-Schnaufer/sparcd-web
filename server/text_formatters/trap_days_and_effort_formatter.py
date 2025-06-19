""" Formats trap days and effort calculation information """

import dataclasses
import os

from .analysis import Analysis
from .results import Results

# pylint: disable=consider-using-f-string
@dataclasses.dataclass
class TrapDaysAndEffortFormatter:
    """ Formats trap days and effort calculation information
    """

    @staticmethod
    def print_camera_trap_days(results: Results) -> str:
        """ A list of all locations (Location) to be analyzed that includes the state and stop date,
            the total number of days each location was run (Duration), the date of the first picture
            recorded at the location (First pic), and the species recorded. This is followed by the
            total number of Camera trap days (Duration).
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'CAMERA TRAP DAYS' + os.linesep + \
                  'Location                    Start date  Stop date   Duration   First pic   ' \
                  'Species' + os.linesep

        duration_total = 0
        for one_loc in results.get_locations():
            loc_images = results.get_location_images(one_loc['idProperty'])

            first_cal = loc_images[0]['image_dt']
            last_cal = loc_images[len(loc_images) - 1]['image_dt']
            current_duration = Analysis.get_days_span(last_cal, first_cal)
            duration_total = duration_total + current_duration

            species_present = ''
            for one_species in loc_images[0]['species']:
                species_present += one_species['name'] + ' '

            result += '{:<27s} {:4d} {:2d} {:2d}  {:4d} {:2d} {:2d} {:9d}   {:4d} {:2d} {:2d}  ' \
                      '{:s}'.format( \
                                    one_loc['nameProperty'], first_cal.year, first_cal.month, \
                                    first_cal.day, last_cal.year, last_cal.month, last_cal.day, \
                                    current_duration, first_cal.year, first_cal.month, \
                                    first_cal.day, species_present) + \
                      os.linesep

        result += 'Total camera trap days                             {:9d}'.format(\
                                                                            duration_total) + \
                                                                            os.linesep + os.linesep

        return result

    @staticmethod
    def print_camera_trap_effort(results: Results) -> str:
        """ For each year, and for each location, and for each month, the number of camera traps
            days, and the total number of camera trap days for all months. This is followed by Total
            days this is the total of all camera trap days from all locations for each month. The
            total number of camera traps days for the year is given. The Summary for all years, for
            all locations, for all months, and for all years is also given
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result = 'CAMERA TRAP EFFORT' + os.linesep

        for one_year in results.get_years():

            year_images = results.get_year_images(one_year)
            locations = results.locations_for_image_list(year_images)
            locations = [results.get_image_location(one_loc) for one_loc in locations]

            if locations:
                result += 'Year ' + str(one_year) + os.linesep
                result += 'Location ({:3d})              Jan    Feb    Mar    Apr    May    ' \
                          'Jun    Jul    Aug    Sep    Oct    Nov    Dec    Total'.format( \
                                                                        len(locations)) + os.linesep

                monthly_totals = [0] * 12

                for one_loc in locations:
                    year_loc_images = results.filter_location(year_images, one_loc['idProperty'])
                    first_cal = year_loc_images[0]['image_dt']
                    last_cal = year_loc_images[len(year_loc_images) - 1]['image_dt']
                    first_month = first_cal.month
                    last_month = last_cal.month
                    first_day = first_cal.day
                    last_day = last_cal.day
                    result += '{:<28s}'.format(one_loc['nameProperty'])

                    month_total = 0
                    for one_month in range(0, 12):
                        month_value = 0
                        if first_month == last_month and first_month == one_month:
                            month_value = last_day - first_day + 1
                        elif first_month == one_month:
                            month_value = 31 - first_day + 1
                        elif last_month == one_month:
                            month_value = last_day
                        elif first_month < one_month and last_month > one_month:
                            month_value = 31

                        result += ' {:2d}    '.format(month_value)
                        month_total += month_value
                        monthly_totals[one_month] += month_value

                    result += str(month_total) + os.linesep

                result += 'Total days                  '

                for one_month in range(0, 12):
                    result += ' {:2d}    '.format(monthly_totals[one_month])

                result += '{:2d}'.format(sum(monthly_totals)) + os.linesep

            result += os.linesep

        return result

    @staticmethod
    def print_camera_trap_effort_summary(results: tuple) -> str:
        """ Returns camera trap effort
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'CAMERA TRAP EFFORT SUMMARY' + os.linesep

        if results.get_years():
            result += 'Years ' + str(results.get_first_year()) + ' to ' + \
                                                        str(results.get_last_year()) + os.linesep

        result += 'Location                    Jan    Feb    Mar    Apr    May    Jun    Jul    ' \
                  'Aug    Sep    Oct    Nov    Dec    Total' + os.linesep

        monthly_totals = [0] * 12

        for one_loc in results.get_locations():
            loc_images = results.get_location_images(one_loc['idProperty'])

            first_cal = loc_images[0]['image_dt']
            last_cal = loc_images[len(loc_images) - 1]['image_dt']
            first_month = first_cal.month
            last_month = last_cal.month
            first_day = first_cal.day
            last_day = last_cal.day

            result += '{:<28s}'.format(one_loc['nameProperty'])

            month_total = 0
            for one_month in range(0, 12):
                month_value = 0
                if first_month == last_month and first_month == one_month:
                    month_value = last_day - first_day + 1
                elif first_month == one_month:
                    month_value = 31 - first_day + 1
                elif last_month == one_month:
                    month_value = last_day
                elif first_month < one_month and last_month > one_month:
                    month_value = 31

                result += ' {:2d}    '.format(month_value)
                month_total = month_total + month_value
                monthly_totals[one_month] = monthly_totals[one_month] + month_value

            result += str(month_total) + os.linesep

        result += 'Total days                  '

        total_total = 0

        for one_month in range(0, 12):
            total_total = total_total + monthly_totals[one_month]
            result += ' {:2d}    '.format(monthly_totals[one_month])

        result += '{:2d}'.format(total_total)

        result += os.linesep + os.linesep

        return result
