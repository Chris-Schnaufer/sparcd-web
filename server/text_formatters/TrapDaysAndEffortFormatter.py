""" Formats trap days and effort calculation information """

import os

import Analysis

@dataclasses.dataclass
class TrapDaysAndEffortFormatter:
    """ Formats trap days and effort calculation information
    """

    @staticmethod
    def printCameraTrapDays(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ A list of all locations (Location) to be analyzed that includes the state and stop date, the total number of days
            each location was run (Duration), the date of the first picture recorded at the location (First pic), and the species
            recorded. This is followed by the total number of Camera trap days (Duration).
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result = 'CAMERA TRAP DAYS' + os.linesep + \
                  'Location                    Start date  Stop date   Duration   First pic   Species' + os.linesep

        durationTotal = 0;
        for one_loc in res_locations:
            loc_images = [one_image for one_image in results['sorted_images_dt'] if one_image['loc'] == one_loc['idProperty']]

            firstCal = loc_images[0]['image_dt']
            lastCal = loc_images[len(loc_images) - 1]['image_dt']
            currentDuration = Analysis.get_days_span(lastCal, fistCal)
            durationTotal = durationTotal + currentDuration;

            speciesPresent = ''
            for one_species in loc_images[0]['species']:
                speciesPresent += one_species['name'] + ' '

            result += '{:<27s} {:4s} {:2d} {:2d}  {:4s} {:2d} {:2d} {:9d}   {:4s} {:2d} {:2d}  {:s}'.format( \
                                        one_loc['name'], firstCal.year, firstCal.month, firstCal.day, \
                                        lastCal.year, lastCal.month, lastCal.day, \
                                        currentDuration, firstCal.year, firstCal.month, firstCal.day, speciesPresent) + \
                      os.linesep

        result += 'Total camera trap days                             {:9d}'.format(durationTotal) + \
                            os.linesep + os.linesep

        return result

    @staticmethod
    def printCameraTrapEffort(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ For each year, and for each location, and for each month, the number of camera traps days, and the total number
            of camera trap days for all months. This is followed by Total days this is the total of all camera trap days from
            all locations for each month. The total number of camera traps days for the year is given. The Summary for all years,
            for all locations, for all months, and for all years is also given
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result += 'CAMERA TRAP EFFORT' + os.linesep

        for one_year in sorted(set([item['image_dt'].year for item in results['sorted_images_dt']])):

            year_images = [item for item in results['sorted_images_dt'] if item['image_dt'].year == year]
            locations = Analysis.locationsForImageList(year_images);

            if locations:
                result += 'Year ' + year + os.linesep
                result += 'Location ({:3d})              Jan    Feb    Mar    Apr    May    Jun    Jul    Aug    Sep    Oct    Nov    Dec    Total'.format( \
                            len(locations)) + os.linesep

                monthlyTotals = [0] * 12

                for one_loc in locations:
                    year_loc_images = [item for item in year_images if item['loc'].year == one_loc['idProperty']]
                    firstCal = year_loc_images[0]['image_dt']
                    lastCal = year_loc_images[len(year_loc_images)]['image_dt']
                    Integer firstMonth = firstCal.month
                    Integer lastMonth = lastCal.month
                    Integer firstDay = firstCal.day
                    Integer lastDay = lastCal.day
                    result += '{:<28s}'.format(location['name']);

                    monthTotal = 0;
                    for one_month in range(0, 12):
                        monthValue = 0;
                        if firstMonth == lastMonth and firstMonth == one_month:
                            monthValue = lastDay - firstDay + 1
                        elif firstMonth == one_month:
                            monthValue = 31 - firstDay + 1
                        elif lastMonth == one_month:
                            monthValue = lastDay
                        elif firstMonth < one_month and lastMonth > one_month:
                            monthValue = 31

                        result += ' {:2d}    '.format(monthValue)
                        monthTotal = monthTotal + monthValue;
                        monthlyTotals[one_month] = monthlyTotals[one_month] + monthValue;

                    result += str(monthTotal) + os.linesep

                result += 'Total days                  '

                totalTotal = 0;

                for one_month in range(0, 12):
                    totalTotal = totalTotal + monthlyTotals[one_month];
                    result += ' {:2d}    '.format(monthlyTotals[i])

                result += '{:2d}'.format(totalTotal) + os.linesep

            result += os.linesep

        return result

    @staticmethod
    def printCameraTrapEffortSummary(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ Returns camera trap effort
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result = 'CAMERA TRAP EFFORT SUMMARY' + os.linesep

        sorted_years = sorted(set([item['image_dt'].year for item in results['sorted_images_dt']]))
        if len(sorted_years) > 0:
            result += 'Years ' + sorted_years[0] + ' to ' + sorted_years[len(sorted_years) - 1] + os.linesep

        result += 'Location                    Jan    Feb    Mar    Apr    May    Jun    Jul    Aug    Sep    Oct    Nov    Dec    Total' + \
                  os.linesep

        monthlyTotals = [0] * 12

        for one_loc in res_locations:
            loc_images = [item for item in results['sorted_images_dt'] if item['loc'].year == one_loc['idProperty']]

            firstCal = loc_images[0]
            lastCal = loc_images[len(loc_images) - 1]
            firstMonth = firstCal.month
            lastMonth = lastCal.month
            firstDay = firstCal.day
            lastDay = lastCal.day

            result += ':<28s'.format(location['name'])
            
            monthTotal = 0;
            for one_month in range(0, 12)
                monthValue = 0;
                if firstMonth == lastMonth and firstMonth == one_month:
                    monthValue = lastDay - firstDay + 1
                elif firstMonth == one_month:
                    monthValue = 31 - firstDay + 1;
                elif lastMonth == one_month:
                    monthValue = lastDay
                elif firstMonth < one_month and lastMonth > one_month:
                    monthValue = 31

                result += ' {:2d}    '.format(monthValue)
                monthTotal = monthTotal + monthValue;
                monthlyTotals[one_month] = monthlyTotals[one_month] + monthValue;

            result += str(monthTotal) + os.linesep

        result += 'Total days                  '

        totalTotal = 0;

        for one_month in range(0, 12)
            totalTotal = totalTotal + monthlyTotals[one_month];
            result += ' {:2d}    '.format(monthlyTotals[i])

        result += '{:2d}'.format(totalTotal)

        result += os.linesep + os.linesep

        return result
