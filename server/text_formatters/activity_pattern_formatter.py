""" Formats species activity patterns """

import dataclasses
import math
import os
import sys

from .analysis import Analysis
from .results import Results

# pylint: disable=consider-using-f-string
@dataclasses.dataclass
class ActivityPatternFormatter:
    """ Formats species activity patterns
    """

    @staticmethod
    def print_activity_patterns(results: Results) -> str:
        """ For each species daily activity patterns are given for all species by one hour segments.
            The species is listed and in parentheses (the number of reords used in the activity
            calculation / the total number of records some of which might be sequentil). The first
            column, labeled Hour, shows the hour segments starting and ending at midnight. Activity
            pattern is given by the number of records collected from all locations analyzed for all
            years, and in frequency for all years and months, and for all years and each month
            (since activity can vary by month). The total number of records for all years that was
            used is also given. The number of records matches the number of pictures listed under
            NUMBER OF PICTURES AND FILTERED PICTURES PER YEAR above
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'ACTIVITY PATTERNS' + os.linesep
        result += ' Activity in one-hour segments - Species (Number of pictures in one hour ' \
                    'segments/Total number of pics)' + os.linesep

        for species in results.get_species():
            to_add = ''
            species_images = results.get_species_images(species['scientificName'])
            # Activity / All
            to_add += '                   All months         Jan              Feb              ' \
                        'Mar              Apr              May              Jun              ' \
                        'Jul              Aug              Sep              Oct              ' \
                        'Nov              Dec' + os.linesep
            to_add += '    Hour        Number Frequency Number Frequency Number Frequency Number ' \
                        'Frequency Number Frequency Number Frequency Number Frequency Number ' \
                        'Frequency Number Frequency Number Frequency Number Frequency Number ' \
                        'Frequency Number Frequency' + os.linesep

            totals = [0] * 13
            total_activities = [0] * 13

            # 12 months + all months
            for one_month in range(-1, 12):
                # -1 = all months
                if one_month == -1:
                    activity = Analysis.activity_for_image_list(species_images)
                else:
                    species_month_images = [one_image for one_image in species_images if \
                                                        one_image['image_dt'].month == one_month]
                    activity = Analysis.activity_for_image_list(species_month_images)
                total_activities[one_month + 1] = activity

            # 24 hrs
            for one_hour in range(0, 24):
                species_hour_images = results.filter_hours(species_images, one_hour, one_hour + 1)

                to_add += '{:02d}:00-{:02d}:00   '.format(one_hour, one_hour + 1)
                # 12 months
                for one_month in range(-1, 12):
                    activity = 0
                    # -1 = all months
                    if one_month == -1:
                        activity = Analysis.activity_for_image_list(species_hour_images)
                    else:
                        species_hour_month_images = results.filter_month(species_hour_images, \
                                                                                        one_month)
                        activity = Analysis.activity_for_image_list(species_hour_month_images)

                    if activity != 0:
                        to_add += '{:6d} {:10.3f}'.format(activity, \
                                            float(activity) / float(total_activities[one_month + 1]))
                    else:
                        to_add += '                 '
                    totals[one_month + 1] = totals[one_month + 1] + activity

                to_add += os.linesep

            to_add += 'Total         '

            for one_total in totals:
                to_add += '{:6d}    100.000'.format(one_total)

            to_add += os.linesep

            # Print the header
            result += '{:<28s} ({:6d}/{:6d})'.format(species['name'], totals[0], \
                                                                len(species_images)) + os.linesep

            result += to_add

            result += os.linesep

        return result

    @staticmethod
    def print_species_pairs_activity_similarity(results: Results) -> str:
        """ A table showing the similarity comparison of activity patterns using hourly frequency is
            given. The number in the table shows the square root of the sum of the squared
            differencs by hour for each species pair. Freqency is used because the number of records
            used to calcluate activity patterns generally differs for each species. If a pair of
            species has similar activity patterns then the value in the table will be low. If two
            species have very different activity patterns, one being diurnal, the other nocturnal
            for instance, the value in the table will be high
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES PAIRS ACTIVITY SIMILARITY (LOWER IS MORE SIMILAR)' + os.linesep

        result += '                            '

        for species in results.get_species():
            result += '{:<8s} '.format(species['name'][:8]) + os.linesep

        result += os.linesep

        for species in results.get_species():
            result += '{:<27s}'.format(species['name'])
            for other_species in results.get_species():
                species_image = results.get_species_images(species['scientificName'])
                other_species_image = results.get_species_images(other_species['scientificName'])
                total_activity = Analysis.activity_for_image_list(species_image)
                total_activity_other = Analysis.activity_for_image_list(other_species_image)

                activity_similarity = 0.0

                # 24 hrs
                for one_hour in range(0, 24):
                    species_image_hour = results.filter_hours(species_image, one_hour, one_hour + 1)
                    other_species_image_hour = results.filter_hours(other_species_image, \
                                                                            one_hour, one_hour + 1)
                    activity = Analysis.activity_for_image_list(species_image_hour)
                    activity_other = Analysis.activity_for_image_list(other_species_image_hour)
                    frequency = activity / total_activity
                    frequency_other = activity_other / total_activity_other
                    difference = frequency - frequency_other
                    # Frequency squared
                    activity_similarity = activity_similarity + (difference * difference)

                result += '{:6.3f}   '.format(activity_similarity)

            result += os.linesep

        result += os.linesep

        return result

    @staticmethod
    def print_specie_pair_most_similar(results: Results) -> str:
        """ he species pair that has the most similar activity pattern is compared. Only those
            species with 25 or more pictures are used.
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES PAIR MOST SIMILAR IN ACTIVITY (FREQUENCY)' + os.linesep
        result += '  Consider those species with 25 or more pictures' + os.linesep

        lowest = None
        lowest_other = None
        lowest_frequency = sys.float_info.max

        for species in results.get_species():
            for other_species in results.get_species():
                species_image = results.get_species_images(species['scientificName'])
                other_species_image = results.get_species_images(other_species['scientificName'])

                activity_similarity = 0.0

                if (len(species_image) >= 25 and len(other_species_image) >= 25 and \
                                                species['scientificName'] != other_species['scientificName']):
                    # 24 hrs
                    for one_hour in range(0, 24):
                        species_image_hour = results.filter_hours(species_image, \
                                                                            one_hour, one_hour + 1)
                        other_species_image_hour = results.filter_hours(other_species_image, \
                                                                            one_hour, one_hour + 1)
                        num_images = float(len(species_image_hour))
                        num_images_other = float(len(other_species_image_hour))
                        frequency = num_images / float(len(species_image))
                        frequency_other = num_images_other / float(len(other_species_image))
                        difference = frequency - frequency_other
                        # Frequency squared
                        activity_similarity = activity_similarity + (difference * difference)

                    activity_similarity = math.sqrt(activity_similarity)

                    if lowest_frequency >= activity_similarity:
                        lowest_frequency = activity_similarity
                        lowest = species
                        lowest_other = other_species

        if lowest is not None:
            result += 'Hour            {:<28s} {:<28s}'.format(lowest['name'], \
                                                            lowest_other['name']) + os.linesep

            species_images = results.get_species_images(lowest['scientificName'])
            other_species_images = results.get_species_images(lowest_other['scientificName'])
            total_images = len(species_images)
            total_images_other = len(other_species_images)
            activity_similarity = 0.0

            # 24 hrs
            for one_hour in range(0, 24):
                species_image_hour = results.filter_hours(species_image, one_hour, one_hour + 1)
                other_species_image_hour = results.filter_hours(other_species_image, \
                                                                        one_hour, one_hour + 1)
                num_images = float(len(species_image_hour))
                num_images_other = float(len(other_species_image_hour))
                frequency = num_images / total_images
                frequency_other = num_images_other / total_images_other
                difference = frequency - frequency_other
                # Frequency squared
                activity_similarity = activity_similarity + difference * difference

                result += '{:02d}:00-{:02d}:00     {:5.3f}                        {:5.3f}'.format(\
                                    one_hour, one_hour + 1, frequency, frequency_other) + os.linesep

        result += os.linesep

        return result

    @staticmethod
    def print_chi_square_analysis_paired_activity(results: Results) -> str:
        """ Using the Ch-squared statistic activity patterns of paired species are analyzed and
            results presented in species x species table. The null hypothesis H0: Species A and B
            have similar activity patterns at 95% is tested. If the pattern is significantly similar
            then a "+" is entered for A x B, otherwise the pattern is not significcantly similar and
            is indicated by a"0" in the table. Only those species that have 25 or more records are
            considered
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'CHI-SQUARE ANALYSIS OF PAIRED ACTIVITY PATTERNS' + os.linesep
        result += '  H0: Species A and B have similar activity patterns at 95%' + os.linesep
        result += '  Significant = X, Not significant = Blank' + os.linesep
        result += '  Consider only species with >= 25 pictures' + os.linesep

        result += '                            '
        for species in results.get_species():
            result += '{:<8s} '.format(species['name'][:8])

        result += os.linesep

        for species in results.get_species():
            species_images = results.get_species_images(species['scientificName'])
            if len(species_images) >= 25:
                result += '{:<28s}'.format(species['name'])
                for other_species in results.get_species():
                    other_species_images = results.get_species_images(other_species['scientificName'])

                    activity_similarity = 0.0

                    # 24 hrs
                    for one_hour in range(0, 24):
                        species_image_hour = results.filter_hours(species_images, \
                                                                            one_hour, one_hour + 1)
                        other_species_image_hour = results.filter_hours(other_species_images, \
                                                                            one_hour, one_hour + 1)
                        num_images = float(len(species_image_hour))
                        num_images_other = float(len(other_species_image_hour))
                        frequency = num_images / float(len(species_images))
                        frequency_other = num_images_other / float(len(other_species_images))
                        difference = frequency - frequency_other
                        # Frequency squared
                        activity_similarity = activity_similarity + difference * difference

                    chi_square = (1.0 - activity_similarity) / 1.0

                    if chi_square >= 0.95 and len(other_species_image_hour) >= 25:
                        result += '   X     '
                    else:
                        result += '         '

                result += os.linesep

        result += os.linesep

        return result

    @staticmethod
    def print_activity_patterns_season(results: Results) -> str:
        """ Using Northern hemisphere seasons of winter (Dec-Jan-Feb), spring (Mar-Apr-May), summer
            (Jun-Jul-Aug), and fall (Sep-Oct-Nov) activity patterns for each species are presented
            in a table. The table shows the number of records used in the actvity calculation and
            the frequency for each season. To compare the seasonal activity patterns requires
            knowning the number of independent pictures recorded in each season normalied by the
            number of camera trap days (Pictures/Effort) for the season, and the proportion of the
            number of records divided by the total number of records for the all four seasons
            (Visitation proportion). That is, Visitation proportion is computed by summing
            Picture/Effort for all seasons, then dividing each season by the sum. This gives the
            proportion of records (based on indepdenent pictures, not the number of pictures used to
            create activity). Note that more records likely result from greater effort, hence the
            number of records must be normalizedby effort.The total number  of records for each
            season is given
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'ACTIVITY PATTERNS BY SEASON' + os.linesep
        result += '  Activity in one-hour segments by season' + os.linesep

        seasons = [
                [ 11, 0, 1 ],# 1
                [ 2, 3, 4 ], # 2
                [ 5, 6, 7 ], # 3
                [ 8, 9, 10 ] # 4
        ]

        length_per_season = [0] * 4
        monthly_totals = [0] * 12

        for location in results.get_locations():
            location_images = results.get_location_images(location['idProperty'])

            first_date = location_images[0]['image_dt']
            last_date = location_images[len(location_images) - 1]['image_dt']
            first_month = first_date.month
            last_month = last_date.month
            first_day = first_date.day
            last_day = last_date.day
            result += '{:<28s}'.format(location['nameProperty'])

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

        for season_index, one_season in enumerate(seasons):
            for one_month in one_season:
                length_per_season[season_index] = length_per_season[season_index] + \
                                                                        monthly_totals[one_month]

        for species in results.get_species():
            species_images = results.get_species_images(species['scientificName'])

            result += species['name'] + os.linesep
            result += '                     Dec-Jan-Feb           Mar-Apr-May           ' \
                                'Jun-Jul-Aug           Sep-Oct-Nov' + os.linesep
            result += 'Camera trap days    '

            for length in length_per_season:
                result += '{:7d}               '.format(length)
            result += os.linesep

            result += 'Number of pictures  '
            images_per_season = [0] * 4
            for one_season in range(0, 4):
                species_season_images = results.filter_month(species_images, seasons[one_season])

                activity = Analysis.activity_for_image_list(species_season_images)
                result += '{:7d}               '.format(activity)
                images_per_season[one_season] = activity
            result += os.linesep

            result += 'Pictures/Effort        '
            total = 0.0
            ratios = [0.0] * 4
            for one_season in range(0, 4):
                current_ratio = 0.0
                if length_per_season[one_season] != 0:
                    current_ratio = float(images_per_season[one_season]) / \
                                                float(length_per_season[one_season])
                result += '{:5.4f}                '.format(current_ratio)
                ratios[one_season] = current_ratio
                total = total + current_ratio
            result += os.linesep

            result += 'Visitation proportion  '
            for one_season in range(0, 4):
                if total != 0:
                    result += '{:5.4f}                '.format(ratios[one_season] / float(total))
                else:
                    result += '{:5.4f}                '.format(0.0)
            result += os.linesep

            to_add = ''

            to_add += '           Hour        Number      Freq      Number      Freq      ' \
                            'Number      Freq      Number      Freq' + os.linesep

            hourly_totals = [0] * 4

            # 24 hrs
            for one_hour in range(0, 24):
                species_hour_images = results.filter_hours(species_images, one_hour, one_hour + 1)

                to_add += '       [{:02d}]:00-{:02d}:00    '.format(one_hour, one_hour + 1)

                # 4 seasons
                for one_season in range(0, 4):
                    species_season_images = results.filter_month(species_images, \
                                                                                seasons[one_season])
                    species_season_hour_images = results.filter_month(species_hour_images, \
                                                                                seasons[one_season])

                    num_pics = Analysis.activity_for_image_list(species_season_hour_images)
                    total_pics = Analysis.activity_for_image_list(species_season_images)
                    frequency = 0.0
                    if total_pics != 0:
                        frequency = float(num_pics) / float(total_pics)

                    hourly_totals[one_season] = hourly_totals[one_season] + num_pics

                    to_add += '{:5d}        {:5.3f}    '.format(num_pics, frequency)

                to_add += os.linesep

            to_add += '       Hourly pics  '
            for hourly_total in hourly_totals:
                to_add += '{:7d}               '.format(hourly_total)

            to_add += os.linesep

            result += to_add + os.linesep

        return result
