""" Formats statistics about locations """

import dataclasses
import os
import sys

from .analysis import Analysis
from .coordinate_utils import distance_between
from .results import Results

# pylint: disable=consider-using-f-string
@dataclasses.dataclass
class LocationStatFormatter:
    """ Formats statistics about locations
    """

    @staticmethod
    def print_percent_of_species_in_loc(results: Results) -> str:
        """ A species-location table showing the total number of independent pictures, and percent
            of the total for each location for each species analyzed. The total number of
            independent pictures for all species is given for each location
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'FOR EACH LOCATION TOTAL NUMBER AND PERCENT OF EACH SPECIES' + os.linesep
        result += '  Use independent picture' + os.linesep

        for location in results.get_locations():
            result += '{:>31s} '.format(location['nameProperty'])
        result += os.linesep
        result += 'Species'
        for location in results.get_locations():
            result += '                   Total Percent'
        result += os.linesep

        # We just want images that have a species and ignore ones that don't
        have_species_images = [one_image for one_image in results.get_images() if \
                                                    'species' in one_image and one_image['species']]

        # Loop through the species
        for species in results.get_species_by_name():
            result += '{:<26s}'.format(species['name'])
            for location in results.get_locations():
                have_location_images = results.filter_location(have_species_images, \
                                                                            location['idProperty'])
                total_period = Analysis.period_for_image_list(have_location_images, \
                                                                            results.get_interval())
                location_species_images = results.filter_species( \
                                            results.get_location_images(location['idProperty']), \
                                            species['scientificName'])
                period = Analysis.period_for_image_list(location_species_images, \
                                                                            results.get_interval())
                result += '{:5d} {:7.2f}                   '.format(period, \
                                                    (float(period) / float(total_period)) * 100.0)
            result += os.linesep

        result += 'Total pictures            '

        for location in results.get_locations():
            location_images = [one_image for one_image in results.get_images() if \
                                                        one_image['loc'] == location['idProperty']]
            result += '{:5d}  100.00                   '.format(\
                                Analysis.period_for_image_list(location_images, \
                                                                            results.get_interval()))

        result += os.linesep + os.linesep

        return result

    @staticmethod
    def print_species_by_month_by_loc_by_year(results: Results) -> str:
        """ For each year, for each location, a species-month table shows the number of independent
            records for each species. For each location and species the total number of independent
            records for all months is given in the last column (Total). The total number of pictures
            (Total pictures), the total number of camera trap days (Total effort), and total number
            of independent pictures (TotL) normalized by the total number of camera trap days for
            each month (Total/(Total effort)) is given. This is followed by a summary for all years
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'FOR EACH LOCATION AND MONTH TOTAL NUMBER EACH SPECIES' + os.linesep
        result += '  Use independent picture' + os.linesep

        for year in results.get_years():
            result += str(year) + os.linesep

            for location in results.get_locations():
                year_location_images = results.filter_location(results.get_year_images(year), \
                                                                location['idProperty'])
                if year_location_images:
                    result += '{:<28s}  Jan    Feb    Mar    Apr    May    Jun    Jul    Aug    ' \
                              'Sep    Oct    Nov    Dec   Total'.format(location['nameProperty']) +\
                            os.linesep
                    # All species
                    for species in results.get_species_by_name():
                        total_pics = 0
                        year_locations_species_images = results.filter_species(\
                                                                        year_location_images, \
                                                                        species['scientificName'])
                        if year_locations_species_images:
                            result += '{:<28s}'.format(species['name'])
                            # Months 0-12
                            for one_month in range(0, 12):
                                yls_month_images = results.filter_month(\
                                                                    year_locations_species_images, \
                                                                    one_month)
                                period = Analysis.period_for_image_list(yls_month_images, \
                                                                            results.get_interval())
                                result += '{:5d}  '.format(period)
                                total_pics = total_pics + period

                            result += '{:5d}  '.format(total_pics) + os.linesep

                    result += 'Total pictures              '
                    total_pics = 0
                    for one_month in range(0, 12):
                        year_location_month_images = results.filter_month(year_location_images, \
                                                                                        one_month)
                        period = Analysis.period_for_image_list(year_location_month_images, \
                                                                            results.get_interval())
                        result += '{:5d}  '.format(period)
                        total_pics = total_pics + period

                    result += '{:5d}  '.format(total_pics) + os.linesep
                    result += 'Total effort                '

                    total_effort = 0
                    first_cal = year_location_images[0]['image_dt']
                    last_cal = year_location_images[len(year_location_images) - 1]['image_dt']
                    first_month = first_cal.month
                    last_month = last_cal.month
                    first_day = first_cal.day
                    last_day = last_cal.day
                    for one_month in range(0, 12):
                        effort = 0
                        if first_month == last_month and first_month == one_month:
                            effort = last_day - first_day + 1
                        elif first_month == one_month:
                            effort = 31 - first_day + 1
                        elif last_month == one_month:
                            effort = last_day
                        elif first_month < one_month and last_month > one_month:
                            effort = 31

                        result += '{:5d}  '.format(effort)
                        total_effort += effort
                    result += '{:5d}  '.format(total_effort) + os.linesep

                    result += 'Total/Total effort          '
                    for one_month in range(0, 12):
                        year_location_month_images = results.filter_month(year_location_images, \
                                                                                        one_month)
                        period = Analysis.period_for_image_list(year_location_month_images, \
                                                                            results.get_interval())
                        effort = 0
                        if first_month == last_month and first_month == one_month:
                            effort = last_day - first_day + 1
                        elif first_month == one_month:
                            effort = 31 - first_day + 1
                        elif last_month == one_month:
                            effort = last_day
                        elif first_month < one_month and last_month > one_month:
                            effort = 31
                        ratio = 0
                        if effort != 0:
                            ratio = float(period) / float(effort)
                        result += '{:5.2f}  '.format(ratio)

                    total_ratio = 0.0
                    if total_effort != 0:
                        total_ratio = float(total_pics) / float(total_effort)
                    result += '{:5.2f}  '.format(total_ratio) + os.linesep + os.linesep

        return result

    @staticmethod
    def print_species_by_month_by_loc(results: Results) -> str:
        """ Returns all locations for all species for each month for all years
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'ALL LOCATIONS ALL SPECIES FOR EACH MONTH FOR ALL YEARS' + os.linesep
        result += '  Use independent picture' + os.linesep

        if results.get_years():
            result += 'Years ' + str(results.get_first_year()) + ' to ' + \
                                                        str(results.get_last_year()) + os.linesep

        for location in results.get_locations():
            location_images = results.get_location_images(location['idProperty'])
            if location_images:
                result += '{:<28s}  Jan    Feb    Mar    Apr    May    Jun    Jul    Aug    ' \
                          'Sep    Oct    Nov    Dec   Total'.format(location['nameProperty']) + \
                        os.linesep

                for species in results.get_species_by_name():
                    total_pics = 0
                    location_species_images = results.filter_species(location_images,\
                                                                        species['scientificName'])
                    if location_species_images:
                        result += '{:<28s}'.format(species['name'])
                        # Months 0-12
                        for one_month in range(0, 12):
                            location_species_month_images = results.filter_month( \
                                                                location_species_images, one_month)
                            period = Analysis.period_for_image_list(location_species_month_images, \
                                                                            results.get_interval())
                            result += '{:5d}  '.format(period)
                            total_pics += period
                        result += '{:5d}  '.format(total_pics) + os.linesep

                result += 'Total pictures              '
                total_pics = 0
                for one_month in range(0, 12):
                    location_month_images = results.filter_month(location_images, one_month)
                    period = Analysis.period_for_image_list(location_month_images, \
                                                                            results.get_interval())
                    result += '{:5d}  '.format(period)
                    total_pics += period
                result += '{:5d}  '.format(total_pics) + os.linesep

                result += 'Total effort                '
                total_effort = 0
                first_cal = location_images[0]['image_dt']
                last_cal = location_images[len(location_images) - 1]['image_dt']
                first_month = first_cal.month
                last_month = last_cal.month
                first_day = first_cal.day
                last_day = last_cal.day
                for one_month in range(0, 12):
                    effort = 0
                    if first_month == last_month and first_month == one_month:
                        effort = last_day - first_day + 1
                    elif first_month == one_month:
                        effort = 31 - first_day + 1
                    elif last_month == one_month:
                        effort = last_day
                    elif first_month < one_month and last_month > one_month:
                        effort = 31

                    result += '{:5d}  '.format(effort)
                    total_effort += effort
                result += '{:5d}  '.format(total_effort) + os.linesep

                result += 'Total/Total effort          '
                for one_month in range(0, 12):
                    location_month_images = results.filter_month(location_images, one_month)
                    period = Analysis.period_for_image_list(location_month_images, \
                                                                            results.get_interval())
                    effort = 0
                    if first_month == last_month and first_month == one_month:
                        effort = last_day - first_day + 1
                    elif first_month == one_month:
                        effort = 31 - first_day + 1
                    elif last_month == one_month:
                        effort = last_day
                    elif first_month < one_month and last_month > one_month:
                        effort = 31

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
    def print_distance_between_locations(results: Results) -> str:
        """ 
        Arguments:
            results: the query results
        Return:
            Returns the image analysis text
        """
        result = 'DISTANCE (km) BETWEEN LOCATIONS' + os.linesep

        max_distance = 0.0
        max_loc_1 = None
        max_loc_2 = None
        min_loc_1 = None
        min_loc_2 = None
        min_distance = sys.float_info.max
        for location in results.get_locations():
            for other_loc in results.get_locations():
                if location['idProperty'] != other_loc['idProperty']:
                    distance = distance_between(float(location['latProperty']),\
                                                float(location['lngProperty']), \
                                                float(other_loc['latProperty']), \
                                                float(other_loc['lngProperty']))
                    if distance >= max_distance:
                        max_distance = distance
                        max_loc_1 = location
                        max_loc_2 = other_loc
                    if distance <= min_distance:
                        min_distance = distance
                        min_loc_1 = location
                        min_loc_2 = other_loc

        if min_loc_1 is not None:
            result += 'Minimum distance = {:7.3f} Locations: {:28s} {:28s}'.format(min_distance, \
                                        min_loc_1['nameProperty'], min_loc_2['nameProperty']) + \
                                    os.linesep
            result += 'Maximum distance = {:7.3f} Locations: {:28s} {:28s}'.format(max_distance, \
                                        max_loc_1['nameProperty'], max_loc_2['nameProperty']) + \
                                    os.linesep
            result += 'Average distance = {:7.3f}'.format((min_distance + max_distance) / 2.0) + \
                                                                            os.linesep + os.linesep

        result += 'Locations                       '
        for location in results.get_locations():
            result += '{:<28s}'.format(location['nameProperty'])
        result += os.linesep
        for location in results.get_locations():
            result += '{:<32s}'.format(location['nameProperty'])
            for other_loc in results.get_locations():
                distance = distance_between(float(location['latProperty']), \
                                                float(location['lngProperty']), \
                                                float(other_loc['latProperty']), \
                                                float(other_loc['lngProperty']))
                result += '{:<28f}'.format(distance)
            result += os.linesep

        result += os.linesep
        return result

    @staticmethod
    def print_loc_species_frequency_similiarity() -> str:
        """ The 10 most similar locations where similarity is based on the frequency of number of
            independent pictures of each species recorded. Paired locations are given. The last
            column shows 10 times the square root of the sum of the squared frequency differences.
            Lower scores represent more similar species frequency composition. Also given are the
            top 10 most different locations. Higher scores represent greater differences. This is
            followed by a table showing all the scores for each paired of locations
        Return:
            Returns the image analysis text
        """
        result = 'LOCATION SPECIES FREQUENCY SIMILARITY (LOWER IS MORE SIMILAR)' + os.linesep
        result += '   One picture of each species per camera per PERIOD' + os.linesep
        result += '   Square root of sums of squared difference in frequency' +  \
                                                                        os.linesep + os.linesep
        result += '  TOP 10 LOCATION PAIRS MOST SIMILAR IN SPECIES FREQUENCY' + os.linesep
        result += 'No idea what these numbers are' + os.linesep + os.linesep
        result += '  TOP 10 LOCATION PAIRS MOST DIFFERENT IN SPECIES FREQUENCY' + os.linesep
        result += 'No idea what these numbers are' + os.linesep + os.linesep
        #      ???

        return result

    @staticmethod
    def print_loc_species_composition_similiarity() -> str:
        """ Each location has a species composition. Pairs of locations have the no species in
            common, some species incommon, or all species in common. The  Jaccard Similarity Index
            (JSI) is a similarity index. Shown are the top 10 locations with the most similar list
            of spcies. Given are the names of the locations, their JSI index (JSI), and the number
            of species recorded at each location (N1 N2) and the number of species in common
            (N1&N2). Also given is a list of the top 10 most different locations that have fewer
            species in common. A table of JSI scores comparing all locations is also given.
            Locations with no specis in common have JSI = 0.0. If both locations share the same
            species JSI = 1.000
        Return:
            Returns the image analysis text
        """
        result = 'LOCATION-SPECIES COMPOSITION SIMILARITY (Jaccard Similarity Index)' + os.linesep
        result += '  Is species present at this location? yes=1, no=0' + os.linesep
        result += '  1.00 means locations are identical 0.00 means locations have no species in ' \
                                                    'common' + os.linesep
        result += '  Location, location, JSI, number of species at each location, and number of ' \
                                                    'species in common' + os.linesep + os.linesep
        result += '  TOP 10 LOCATION PAIRS MOST SIMILAR IN SPECIES COMPOSITION' + os.linesep
        result += 'No idea what these numbers are' + os.linesep + os.linesep
        result += '  TOP 10 LOCATION PAIRS MOST DIFFERENT IN SPECIES COMPOSITION' + os.linesep
        result += 'No idea what these numbers are' + os.linesep + os.linesep
        #      ???

        return result

    @staticmethod
    def print_species_overlap_at_loc(results: Results) -> str:
        """ A species x species table. Each row has the species name followed by the number of
            locations in () where the species was recored, then the number and in () the percent
            of locations where it was recorded with the species in the column
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES OVERLAP AT LOCATIONS' + os.linesep
        result += '  Number of locations  ' + str(len(results.get_locations())) + os.linesep
        result += '                          Locations  Locations and percent of locations where ' \
                 'both species were recorded' + os.linesep
        result += 'Species                    recorded '
        for species in results.get_species_by_name():
            result += '{:<12s}'.format(species['name'])
        result += os.linesep

        for species in results.get_species_by_name():
            species_images = results.get_species_images(species['scientificName'])
            result += '{:<28s}'.format(species['name'])
            locations = results.locations_for_image_list(species_images)
            result += '{:3d}    '.format(len(locations))
            for other_species in results.get_species():
                other_species_images = results.get_species_images(other_species['scientificName'])
                locations_other = results.locations_for_image_list(other_species_images)
                intersection_size = len(set(locations).intersection(locations_other))
                result += '{:2d} ({:6.1f}) '.format(intersection_size, \
                                        100.0 * (float(intersection_size) / float(len(locations))))
            result += os.linesep

        result += os.linesep

        return result

    @staticmethod
    def print_area_covered_by_traps() -> str:
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
