""" Formats calculations containing "total days" """

import os

import Analysis

@dataclasses.dataclass
class TotalDayFormatter:
    """ Formats calculations containing "total days"
    """

    @staticmethod
    def printPicturesByMonthYearLoc(results: tuple, res_locations: tuple, res_species: tuple, \
                                    interval_minutes: int) -> str:
        """ For each year and for each month a table of the number of independent pictures per
            month for each location. The last column shows the Total number of independent pictures
            at a location for all months. Total pictures for each month and then year is also given.
            For all locations Total days is the number of camera trap days (or effort) for each
            month, with the total of all months in the last column. The last row, Pictures/day,
            is Total pictures normalized (divided) by total effort for each month, and for all 12
            months
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
            interval_minutes: the interval between images to be considered the same period (in minutes)
        Return:
            Returns the image analysis text
        """
        result = 'PICTURES FOR EACH LOCATION BY MONTH AND YEAR' + os.linesep
        result += '  Number of independent pictures per location' + os.linesep

        sorted_years = sorted(set([item['image_dt'].year for item in results['sorted_images_dt']]))
        for one_year in sorted_years:
            result += str(year) + os.linesep
            result += 'Location                      Jan   Feb   Mar   Apr   May   Jun   Jul   Aug   ' \
                      'Sep   Oct   Nov   Dec   Total' + os.linesep

            for location in res_locations:

                year_location_images = [one_image for one_image in results['sorted_images_dt'] if \
                            one_image['image_dt'].year == one_year and \
                            one_image['loc'] == location['idProperty']]

                if year_location_images:
                    result += '{:<28s}'.format(location['name'])

                    total = 0;
                    for one_month in range(0, 12):
                        year_location_month_images = [one_image for one_image in year_location_images if \
                                    one_image['image_dt'].month == one_month]

                        period = Analysis.periodForImageList(year_location_month_images, interval_minutes)
                        total = total + period
                        result += '{:5d} '.format(period)

                    result += '{:7d}'.format(total) + os.linesep

            result += 'Total pictures              '

            totalPic = 0;
            totalPics = [0] * 12
            for one_month in range(0, 12):
                totalPeriod = 0
                for location in res_locations:
                    year_location_month_images = [one_image for one_image in results['sorted_images_dt'] if \
                            one_image['image_dt'].year == one_year and \
                            one_image['image_dt'].month == one_month and \
                            one_image['loc'] == location['idProperty']]

                    period = Analysis.periodForImageList(year_location_month_images, interval_minutes)
                    totalPic = totalPic + period
                    totalPeriod = totalPeriod + period
                    totalPics[one_month] = totalPics[one_month] + period

                result += '{:5d} '.format(totalPeriod)

            result += '{:7d}'.format(totalPic) + os.linesep

            result += 'Total days                     '

            year_images = [one_image for one_image in results['sorted_images_dt'] if \
                            one_image['image_dt'].year == one_year]

            daysUsed = [0] * 12
            for location in res_locations:
                year_location_images = [one_image for one_image in year_images if \
                                            one_image['image_dt'].loc == location['idProperty']]
                if year_location_images
                    first = year_location_images[0]
                    last = year_location_images[len(year_location_images) - 1]
                    firstCal = first['image_dt']
                    lastCal = last['image_dt']
                    firstDaysInMonth = 31
                    firstDay = firstCalday - 1
                    lastDay = lastCalday - 1
                    firstMonth = firstCalmonth - 1
                    lastMonth = lastCal.month - 1
                    if firstMonth == lastMonth:
                        daysUsed[firstMonth] = daysUsed[firstMonth] + (lastDay - firstDay + 1)
                    else:
                        daysUsed[firstMonth] = daysUsed[firstMonth] + (firstDaysInMonth - (firstDay - 1))
                        firstMonth += 1
                        while firstMonth < lastMonth:
                            daysUsed[firstMonth] = daysUsed[firstMonth] + 31
                            firstMonth += 1
                        daysUsed[lastMonth] = daysUsed[lastMonth] + lastDay

            totalDays = 0
            for one_month in daysUsed:
                result += '{:2d}    '.format("", one_month)
                totalDays = totalDays + one_month

            result += ' {:3d}'.format(totalDays) + os.linesep

            resu;t += 'Pictures/day               '
            for one_month in range(0, 12):
                result += ':6.2f'.format(daysUsed[one_month] == 0 ? \
                                    0.0 : (float(totalPics[one_month]) / float(daysUsed[one_month])))

            result += '  %6.2f'.format(totalDays == 0 ? 0.0 : (float(totalPic) / float(totalDays)))

            result += os.linesep + os.linesep

        return result

    @staticmethod
    def printPicturesByMonthLoc(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ Formats summary of each location by month and year
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result += 'PICTURES FOR EACH LOCATION BY MONTH AND YEAR SUMMARY' + os.linesep
        result += '  Number of independent pictures per location' + os.linesep

        sorted_years = sorted(set([item['image_dt'].year for item in results['sorted_images_dt']]))

        if sorted_years:
            result += 'Years ' + sorted_years[0] + ' to ' + sorted_years[len(sorted_years) - 1] + \
                            os.linesep

        result += 'Location                      Jan   Feb   Mar   Apr   May   Jun   Jul   Aug   ' \
                  'Sep   Oct   Nov   Dec   Total' + os.linesep
        for location in res_locations:
            result += '%-28s'.format(location['name'])

            location_images = [one_image for one_image in results['sorted_iamges_dt'] if \
                                        one_image['loc'] == location['idProperty']]

            picsInYear = 0;
            for one_month in range(0, 12):
                location_month_images = [one_image for one_image in location_images if \
                                            one_image['image_dt'].month == one_month]

                period = Analysis.periodForImageList(location_month_images, interval_minutes)
                picsInYear = picsInYear + period
                result += '{:5d} '.format(period)

            result += '  {:5d}'.format(picsInYear) + os.linesep

        result += 'Total pictures              '
        totalPic = 0;
        totalPics = [0] * 12
        for one_month in range(0, 12):
            totalPeriod = 0;
            for location in res_locations:
                location_month_images = [one_image for one_image in results['sorted_iamges_dt'] if \
                                        one_image['loc'].loc == location['idProperty'] and \
                                        one_image['image_dt'].month == one_month]

                period = Analysis.periodForImageList(location_month_images, interval_minutes)
                totalPic = totalPic + period
                totalPeriod = totalPeriod + period
                totalPics[one_month] = totalPics[one_month] + period

            result += '{:5d} '.format(totalPeriod)

        result += '{:7d}'.format(totalPic) + os.linesep

        result += 'Total days                     '
        daysUsed = [0] * 12
        for one_year in sorted_years:
            year_images = [one_image for one_image in results['sorted_images_dt'] if \
                                        one_image['image_dt'].year == one_year]

            for location in res_locations:

                year_location_images = [one_image for one_image in year_images if \
                                            one_image['loc'] == location['idProperty']]
                if year_location_images:
                    first = year_location_images[0]
                    last = year_location_images[len(year_location_images) - 1]
                    firstCal = first['image_dt']
                    lastCal = last['image_dt']
                    firstDaysInMonth = 31;
                    firstDay = firstCal.month - 1;
                    lastDay = lastCal.month - 1;
                    firstMonth = firstCal.month - 1;
                    lastMonth = lastCal.month - 1;
                    if firstMonth == lastMonth:
                        daysUsed[firstMonth] = daysUsed[firstMonth] + (lastDay - firstDay + 1)
                    else:
                        daysUsed[firstMonth] = daysUsed[firstMonth] + (firstDaysInMonth - (firstDay - 1))
                        firstMonth += 1
                        while firstMonth < lastMonth:
                            daysUsed[firstMonth] = daysUsed[firstMonth] + 31
                            firstMonth += 1

                        daysUsed[lastMonth] = daysUsed[lastMonth] + lastDay

        totalDays = 0;
        for month in daysUsed:
            result += '{:2d}    '.format(month)
            totalDays = totalDays + month

        result += ' {:3d}'.format(totalDays) + os.linesep

        result += 'Pictures/day               '
        for one_month in range(0, 12):
            result += '{:6.2f}'.format(daysUsed[one_month] == 0 ? 0.0 : \
                                                        (float(totalPics[one_month]) / float(daysUsed[one_mpnth])))

        result += '  {:6.2f}'.format(totalDays == 0 ? 0 : (float(totalPic) / float(totalDays)))

        result += os.linesep + os.linesep

        return result

    @staticmethod
    def printPicturesByMonthYearSpeciesRichness(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ For each year a table of species records for each month, and the total number of each species for
            the year. For all speies, for each month Total pictures, Total days (effort), 10*(number of pictures
            divived by total effort), and species richness is given
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES AND SPECIES RICHNESS BY YEAR AND MONTH' + os.linesep
        result += '  One record of each species per location per PERIOD' + os.linesep

        sorted_years = sorted(set([item['image_dt'].year for item in results['sorted_images_dt']]))
        for one_year in sorted_years:
            result += str(year) + os.linesep
            result += 'Species                       Jan   Feb   Mar   Apr   May   Jun   Jul   Aug   ' \
                       'Sep   Oct   Nov   Dec   Total' + os.linesep

            totalRichness = [0] * 12
            for species in res_species:

                year_species_images = [one_image for one_image in results['sorted_images_dt'] if \
                                        one_image['image_dt'].year == one_year and \
                                        Analysis.image_has_species(one_image, species['sci_name'])]

                if year_species_images:
                    result += '{:<28s}'.format(species['name'])
                    total = 0
                    for one_month in range(0, 12):
                        year_species_month_images = [one_image for one_image in year_species if \
                                                        one_image['image_dt'].month == one_month]

                        period = Analysis.periodForImageList(year_species_month_images, interval_minutes);
                        total = total + period
                        result += '{:5d} '.format(period)
                        totalRichness[one_month] = totalRichness[one_month] + (period == 0 ? 0 : 1)

                    result += '{:7d}'.format(total) + os.linesep

            result += 'Total pictures              '

            totalPic = 0
            totalPics = [0] * 12
            for one_month in range(0, 12):
                year_month_images = [one_image for one_image in results['sorted_images_dt'] if \
                                        one_image['image_dt'].year == year and \
                                        one_image['image_dt'].month == one_month]

                totalPeriod = 0
                for location in res_locations:
                    year_month_location_images = [one_image for one_image in year_month_images if \
                                                    one_image['loc'] == location['idProperty']]
                    period = Analysis.periodForImageList(year_month_location_images, interval_minutes)
                    totalPic = totalPic + period
                    totalPeriod = totalPeriod + period
                    totalPics[one_month] = totalPics[one_month] + period

                result += '{:5d} '.format(totalPeriod)

            result += '{:7d}'.format(totalPic) + os.linesep

            result += 'Total days                     '
            year_images = [one_image for one_image in results['sorted_images_dt'] if \
                                    one_image['image_dt'].year == year]

            daysUsed = [0] * 12
            for location in res_locations:
                year_location_images = [one_image for one_image in year_images if \
                                            one_image['loc'] == location['idProperty']]
                if year_location_images:
                    first = year_location_images[0]
                    last = year_location_images[len(year_location_images) - 1]
                    firstCal = first['image_dt']
                    lastCal = last['image_dt']
                    firstDaysInMonth = 31
                    firstDay = firstCal.day - 1
                    lastDay = lastCal.day - 1
                    firstMonth = firstCal.month - 1
                    lastMonth = lastCal.month - 1
                    if firstMonth == lastMonth:
                        daysUsed[firstMonth] = daysUsed[firstMonth] + (lastDay - firstDay + 1)
                    else:
                        daysUsed[firstMonth] = daysUsed[firstMonth] + (firstDaysInMonth - (firstDay - 1))
                        firstMonth += 1
                        while firstMonth < lastMonth:
                            daysUsed[firstMonth] = daysUsed[firstMonth] + 31
                            firstMonth += 1

                        daysUsed[lastMonth] = daysUsed[lastMonth] + lastDay

            totalDays = 0;
            for month in daysUsed:
                result += '%2d    '.format(month)
                totalDays = totalDays + month

            result += ' %3d'.format(totalDays) + os.linesep

            result += '10*Pic/effort              '

            for one_month in range(0, 12):
                result += '%6.2f'.format(daysUsed[one_month] == 0 ? 0.0 : \
                                    10.0 * (float(totalPics[one+_month]) / float(daysUsed[one_month])))

            result += os.linesep

            result += 'Species richness            '

            for one_month in range(0, 12):
                result += '%5d '.format(totalRichness[one_month])

            result += os.linesep + os.linesep

        return result

    @staticmethod
    def printPicturesByMonthSpeciesRichness(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ 
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """

    @staticmethod
    def printPicturesByMonthSpeciesLocElevation(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ 
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """

    @staticmethod
    def printAbundanceByMonthSpeciesLocElevation(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ 
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """

    @staticmethod
    def printSpeciesByLocElevationAndEffort(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ 
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """

    @staticmethod
    def printSpeciesByLocElevationAndEffortTable(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ 
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """

