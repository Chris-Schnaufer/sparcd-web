""" Formats statistics about locations """

import os
import sys

import Analysis

@dataclasses.dataclass
class LocationStatFormatter:
    """ Formats statistics about locations
    """

    @staticmethod
    def printPercentOfSpeciesInLoc(results: tuple, res_locations: tuple, res_species: tuple, \
                                   interval_minutes: int) -> str:
        """ A species-location table showing the total number of independent pictures, and percent of
            the total for each location for each species analyzed. The total number of independent pictures
            for all species is given for each location
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
            interval_minutes: the interval between images to be considered the same period (in minutes)
        Return:
            Returns the image analysis text
        """
        result = FOR' EACH LOCATION TOTAL NUMBER AND PERCENT OF EACH SPECIES' + os.linesep
        result += '  Use independent picture' + os.linesep

        for location in res_locations:
            result += '{:31s} '.format(location['name'])
        result += os.linesep
        result += 'Species'
        for location in res_locations:
            result += '                   Total Percent'
        result += os.linesep

        have_species_images = [one_image for one_image in results['sorted_images_dt'] if 'species' in one_image and one_image['species']]
        for species in res_species:
            result += '{:<26s}'.format(species['sci_name'])
            for location in res_locations:
                location_images = [one_image for one_image in have_species_images if one_image['loc'] == location['idProperty']]
                total_period = Analysis.periodForImageList(location_images, interval_minutes)
                location_species_images = [one_image for one_image in location_images \
                                                            if Analysis.image_has_species(one_image, species['sci_name'])]
                period = analysis.periodForImageList(location_species_images, interval_minutes)
                result += '{:5d} {:7.2f}                   '.format(period, (period / float(total_period)) * 100.0)
            result += os.linesep

        result += 'Total pictures            '

        for location in res_locations:
            location_images = [one_image for one_image in results['sorted_images_dt'] if one_image['loc'] == location['idProperty']]
            result += '{:5d}  100.00                   '.format(analysis.periodForImageList(location_images, interval_minutes))

        result += os.linesep + os.linesep

        return result

    @staticmethod
    def printSpeciesByMonthByLocByYear(results: tuple, res_locations: tuple, res_species: tuple, \
                                       interval_minutes: int) -> str:
        """ For each year, for each location, a species-month table shows the number of independent records
            for each species. For each location and species the total number of independent records for all
            months is given in the last column (Total). The total number of pictures (Total pictures), the
            total number of camera trap days (Total effort), and total number of independent pictures (TotL)
            normalized by the total number of camera trap days for each month (Total/(Total effort)) is given.
            This is followed by a summary for all years
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
            interval_minutes: the interval between images to be considered the same period (in minutes)
        Return:
            Returns the image analysis text
        """
        result = 'FOR EACH LOCATION AND MONTH TOTAL NUMBER EACH SPECIES' + os.linesep
        result += '  Use independent picture' + os.linesep

        for year in sorted(set([item['image_dt'].year for item in results['sorted_images_dt']])):
            result += str(year) + os.linesep

            for location in res_locations:
                year_location_images = [one_image for one_image in result['sorted_images_dt'] if \
                                                one_image['image_dt'].year == year and one_image['loc'] == location['idProperty']]
                if year_location_images:
                    result += '{:<28s}  Jan    Feb    Mar    Apr    May    Jun    Jul    Aug    Sep    Oct    Nov    Dec   Total'.\
                                                                                            format(location['name'])
                    # All species
                    for species in res_species:
                        total_pics = 0;
                        year_locations_species_images = [one_image for one_image in year_location_images if \
                                                            Analysis.image_has_species(image, species['sci_name'])]
                        if year_locations_species_images:
                            result += '{:<28s}'.format(species['name'])
                            # Months 0-12
                            for one_month in range(0, 12):
                                yls_month_images = [one_image for one_image in year_locations_species_images if \
                                                                            one_image['image_dt'].month == one_month]
                                period = Analysis.periodForImageList(yls_month_images, interval_minutes)
                                result += '{:5d}  '.format(period)
                                total_pics = total_pics + period

                            result += '{:5d}  '.format(total_pics) + os.linesep

                    result += 'Total pictures              '
                    total_pics = 0;
                    for one_month in range(0, 12):
                        year_location_month_images = [one_image for one_image in year_location_images if \
                                                                one_image['image_dt'].month == one_month]
                        period = Analysis.periodForImageList(year_location_month_images, interval_minutes)
                        result += '{:5d}  '.format(period)
                        total_pics = total_pics + period;

                    result += '{:5d}  '.format(total_pics) + os.linesep
                    result += 'Total effort                '
                    
                    total_effort = 0;
                    first_cal = year_location_images[0]['image_dt']
                    last_cal = year_location_images[len(year_location_images) - 1]['image_dt']
                    first_month = first_cal.month
                    last_month = last_cal.month
                    first_day = first_cal.day
                    last_day = last_cal.day
                    for one_month in range(0, 12):
                        effort = 0;
                        if first_month == last_month and first_month == one_month:
                            effort = last_day - first_day + 1
                        elif first_month == one_month:
                            effort = 31 - first_day + 1
                        elif last_month == one_month:
                            effort = last_day
                        elif first_month < one_month and last_month > one_month:
                            effort = 31;

                        result += '{:5d}  '.format(effort)
                        total_effort = total_effort + effort
                    result += '{:5d}  '.format(total_effort) + os.linesep

                    result += 'Total/Total effort          '
                    for one_month in range(0, 12):
                        year_location_month_images = [one_image for one_image in year_location_images if \
                                                                            one_image['image_dt'].month == one_month]
                        period = analysis.periodForImageList(year_location_month_images, interval_minutes)
                        effort = 0;
                        if first_month == last_month and first_month == one_month:
                            effort = last_day - first_day + 1
                        elif first_month == one_month:
                            effort = 31 - first_day + 1
                        elif last_month == one_month:
                            effort = last_day
                        elif first_month < one_month and last_month > one_month:
                            effort = 31
                        double ratio = 0
                        if effort != 0:
                            ratio = float(period) / float(effort)
                        result += '{:5.2f}  '.format(ratio)

                    total_ratio = 0.0
                    if total_effort != 0:
                        total_ratio = float(total_pics) / float(total_effort)
                    result += '{:5.2f}  '.format(total_ratio) + os.linesep + os.linesep

        return result

    @staticmethod
    def printSpeciesByMonthByLoc(results: tuple, res_locations: tuple, res_species: tuple, \
                                 interval_minutes: int) -> str:
        """ Returns all locations for all species for each month for all years
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
            interval_minutes: the interval between images to be considered the same period (in minutes)
        Return:
            Returns the image analysis text
        """
        result = 'ALL LOCATIONS ALL SPECIES FOR EACH MONTH FOR ALL YEARS' + os.linesep
        result += '  Use independent picture' + os.linesep

        all_years = sorted(set([item['image_dt'].year for item in results['sorted_images_dt']])):
        if all_years:
            results += 'Years ' + all_years[0] + ' to ' + all_years[len(all_years) - 1] + os.linesep

        for location in res_locations:
            location_images = [one_image for one_image in results['sorted_images_dt'] if one_image['loc'] == location['idProperty']]
            if location_images:
                result += '{:<28s}  Jan    Feb    Mar    Apr    May    Jun    Jul    Aug    Sep    Oct    Nov    Dec   Total'.\
                                                                                                format(location['name'])

                for species in res_species:
                    total_pics = 0;
                    location_species_images = [one_image for one_image in location_images if \
                                                             Analysis.image_has_species(one_image, species['sci_name'])]
                    if location_species_images:
                        result += '{:<28s}'.format(species['name'])
                        # Months 0-12
                        for one_month in range(0, 12):
                            location_species_month_images = [one_image for one_image in location_species_images if \
                                                                                        one_image['image_dt'].month == one_month]
                            period = Analysis.periodForImageList(location_species_month_images, interval_minutes)
                            result += '{:5d}  '.format(period)
                            total_pics = total_pics + period;
                        result += '{:5d}  '.format(total_pics) + os.linesep

                result += 'Total pictures              '
                total_pics = 0;
                for one_month in range(0, 12):
                    location_month_images = [one_image for one_image in location_images if one_image['image_dt'].month == one_month]
                    period = Analysis.periodForImageList(location_month_images, interval_minutes)
                    result += '{:5d}  '.format(period)
                    total_pics = total_pics + period;
                result += '{:5d}  '.format(total_pics) + os.linesep

                result += 'Total effort                '
                total_effort = 0;
                first_cal = locations_images[0]['image_dt']
                last_cal = locations_images[len(location_images) - 1]['image_dt']
                first_month = first_cal.month
                last_month = last_cal.month
                first_day = first_cal.day
                last_day = last_cal.day
                for one_month in range(0, 12):
                    effort = 0;
                    if first_month == last_month and first_month == one_month:
                        effort = last_day - first_day + 1
                    elif first_month == one_month:
                        effort = 31 - first_day + 1
                    elif last_month == one_month:
                        effort = last_day
                    elif first_month < one_month and last_month > one_month:
                        effort = 31;

                    result += '{:5d}  '.format(effort)
                    total_effort = total_effort + effort
                result += '{:5d}  '.format(total_effort) + os.linesep

                result += 'Total/Total effort          '
                for one_month in range(0, 12):
                    location_month_images = [one_image for one_image in location_images if \
                                                                one_image['image_dt'].month == one_month]
                    period = analysis.periodForImageList(location_month_images, interval_minutes)
                    effort = 0;
                    if first_month == last_month && first_month == one_month:
                        effort = last_day - first_day + 1
                    elif first_month == one_month:
                        effort = 31 - first_day + 1
                    elif last_month == one_month:
                        effort = last_day;
                    elif first_month < one_month and last_month > one_month:
                        effort = 31;

                    ratio = 0.0
                    if effort != 0:
                        ratio = float(period) / float(effort)
                    result += '{:5.2f}  '.format(ratio)

                total_ratio = 0.0
                if total_effort != 0:
                    total_ratio = float(total_pics) / float(total_effort)
                result += '{:5.2f}  '.format(total_ratio) + os.linesep + os.linesep

        return result

    @staticmethod
    def printDistanceBetweenLocations(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ 
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result += 'DISTANCE (km) BETWEEN LOCATIONS' + os.linesep

        maxDistance = 0.0
        maxLoc1 = None
        maxLoc2 = None
        minLoc1 = None
        minLoc2 = None
        minDistance = sys.float_info.max
        for location in res_locations:
            for other_loc in res_locations:
                if location['idProperty'] != other_loc['idPropertu']
                    distance = SanimalAnalysisUtils.distanceBetween(location.getLat(), location.getLng(), other.getLat(), other.getLng());
                    if distance >= maxDistance:
                        maxDistance = distance
                        maxLoc1 = location
                        maxLoc2 = other_loc
                    if distance <= minDistance:
                        minDistance = distance
                        minLoc1 = location
                        minLoc2 = other_loc

        if minLoc1 != None:
            result += 'Minimum distance = {:7.3f} Locations: {:28s} {:28s}'.format(minDistance, \
                                                            minLoc1['name'], minLoc2['name']) + os.linesep
            result += 'Maximum distance = {:7.3f} Locations: {:28s} {:28s}'.format(maxDistance, \
                                                            maxLoc1['name'], maxLoc2['name']) + os.linesep
            result += 'Average distance = {:7.3f}'.format((minDistance + maxDistance) / 2.0) + os.linesep + os.linesep

        result += 'Locations                       '
        for location in res_locations:
            result += '{:<28s}'.format(location['name'])
        result += os.linesep
        for location in res_locations:
            result += '{:<32s}'.format(location['name'])
            for other_loc in res_locations:
                distance = SanimalAnalysisUtils.distanceBetween(location.getLat(), location.getLng(), other.getLat(), other.getLng());
                result += '{:<28f}'.format(distance)
            result += os.linesep

        result += os.linesep
        return result

    @staticmethod
    def printLocSpeciesFrequencySimiliarity() -> str:
        """ The 10 most similar locations where similarity is based on the frequency of number of independent
            pictures of each species recorded. Paired locations are given. The last column shows 10 times the
            square root of the sum of the squared frequency differences. Lower scores represent more similar species
            frequency composition. Also given are the top 10 most different locations. Higher scores represent
            greater differences. This is followed by a table showing all the scores for each paired of locations
        Return:
            Returns the image analysis text
        """
        result = 'LOCATION SPECIES FREQUENCY SIMILARITY (LOWER IS MORE SIMILAR)' + os.linesep
        result += '   One picture of each species per camera per PERIOD' + os.linesep
        result += '   Square root of sums of squared difference in frequency' + os.linesep + os.linesep
        result += '  TOP 10 LOCATION PAIRS MOST SIMILAR IN SPECIES FREQUENCY' + os.linesep
        result += 'No idea what these numbers are' + os.linesep + os.linesep
        result += '  TOP 10 LOCATION PAIRS MOST DIFFERENT IN SPECIES FREQUENCY' + os.linesep
        result += 'No idea what these numbers are' + os.linesep + os.linesep
        #      ???

        return result

    @staticmethod
    def printLocSpeciesCompositionSimiliarity() -> str:
        """ Each location has a species composition. Pairs of locations have the no species in common,
            some species incommon, or all species in common. The  Jaccard Similarity Index (JSI) is a
            similarity index. Shown are the top 10 locations with the most similar list of spcies. Given
            are the names of the locations, their JSI index (JSI), and the number of species recorded at
            each location (N1 N2) and the number of species in common (N1&N2). Also given is a list of
            the top 10 most different locations that have fewer species in common. A table of JSI scores
            comparing all locations is also given. Locations with no specis in common have JSI = 0.0.
            If both locations share the same species JSI = 1.000
        Return:
            Returns the image analysis text
        """
        result = 'LOCATION-SPECIES COMPOSITION SIMILARITY (Jaccard Similarity Index)' + os.linesep
        result += '  Is species present at this location? yes=1, no=0' + os.linesep
        result += '  1.00 means locations are identical; 0.00 means locations have no species in common' + os.linesep
        result += '  Location, location, JSI, number of species at each location, and number of species in common' + os.linesep + os.linesep
        result += '  TOP 10 LOCATION PAIRS MOST SIMILAR IN SPECIES COMPOSITION' + os.linesep
        result += 'No idea what these numbers are' + os.linesep + os.linesep
        result += '  TOP 10 LOCATION PAIRS MOST DIFFERENT IN SPECIES COMPOSITION' + os.linesep
        result += 'No idea what these numbers are' + os.linesep + os.linesep
        #      ???

        return result

    @staticmethod
    def printSpeciesOverlapAtLoc(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ A species x species table. Each row has the species name followed by the number of locations
            in () where the species was recored, then the number and in () the percent of locations where
            it was recorded with the species in the column
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES OVERLAP AT LOCATIONS' + os.linesep
        result = '  Number of locations  ' + str(len(res_locations)) + os.linesep
        result = '                          Locations  Locations and percent of locations where both species were recorded' + os.linesep
        result = 'Species                    recorded '
        for species in res_species:
            result += '{:<12s}'.format(species['name'])
        result += os.linesep

        for species in res_species:
            species_images = [one_image for one_image in results['sorted_images_dt'] if \
                                            Analysis.image_has_species(one_image, species['sci_name'])]
            result += '{:<28s}'.format(species['name'])
            locations = Analysis.locationsForImageList(species_images);
            result += '{:3d}    '.format(len(locations))
            for other_species in res_species:
                other_species_images = [one_image for one_image in results['sorted_images_dt'] if \
                                            Analysis.image_has_species(one_image, other_species['sci_name'])]
                locations_other = Analysis.locationsForImageList(other_species_images)
                intersection_size = len(set(locations).intersection(locations_other))
                result += '{:2d} ({:6.1f}) '.format(intersection_size, (100.0 * float(intersectionSize) / float(len(locations))))
            result += os.linesep

        result += os.linesep

        return result

    @staticmethod
    def printAreaCoveredByTraps() -> str:
        """ The area contained in the convex polygon formed by the outer-most locations listed. Also
            given are the UTM locations of the locations. This is followed by the Area contained in
            the convex polygon given in kilometers^2 and miles^2
        Return:
            Returns the image analysis text
        """
        result = 'AREA COVERED BY CAMERA TRAPS' + os.linesep
        result += '  List of locations forming convex polygon' + os.linesep
        result += 'No idea what these numbers are' + os.linesep + os.linesep

        return result
