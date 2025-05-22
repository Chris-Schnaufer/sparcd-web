""" Formats statistics about lunar activity """

import dataclasses
import datetime
import math
import os

from analysis import Analysis

# Number of days (in seconds) for a datetime to be considered to be within a moon phase
MOON_PHASE_DATE_DIFF_SEC = 5 * 24 * 60 * 60     # Five days in seconds


def in_moons(image_date: datetime.datetime, moons: tuple) -> tuple:
    """ Returns whether or not the image date falls within a full moon
    Arguments:
        image_date: the date to check
        moons: an iterator containing the datetime of the moons to check
    Return:
        Returns a tuple containing True/False for if the image date is within
        range of a full moon, the index of the moon that matched, and the moon
        datetime that matched. When not matched, the index and datetime positions
        contain None
    """
    for index, one_moon in enumerate(moons):
        if abs((one_moon - image_date).total_seconds()) < MOON_PHASE_DATE_DIFF_SEC:
            return True, index, one_moon

    return False, None, None


def create_lunar_activity_table(results: tuple, res_species: tuple)-> tuple:
    """ Returns a tuple containing tuples of species, total difference, and total images
    Arguments:
        results: the results to search through
        res_species: all distinct result species information
    Return:
        Returns the table of information
    """
    lunar_activities = []

    full_moons = Analysis.get_full_moons(results['sorted_images_dt'][0],
                                results['sorted_images_dt'][len(results['sorted_images_dt']) - 1])
    new_moons = Analysis.get_new_moons(results['sorted_images_dt'][0],
                                results['sorted_images_dt'][len(results['sorted_images_dt']) - 1])

    full_images = [one_image for one_image in results['sorted_images_dt'] if \
                                                                    in_moons(one_image, full_moons)]
    new_images = [one_image for one_image in results['sorted_images_dt'] if \
                                                                    in_moons(one_image, new_moons)]

    for species in res_species:
        num_images_total_tull = 0
        num_images_total_new = 0

        total_difference = 0.0

        full_species_images = [one_image for one_image in full_images if \
                                        Analysis.image_has_species(one_image, species['sci_name'])]

        new_species_images = [one_image for one_image in new_images if \
                                        Analysis.image_has_species(one_image, species['sci_name'])]

        # 24 hrs
        for one_hour in range(0, 24):
            full_species_hour_images = [one_image for one_image in full_species_images if \
                                    one_image['image_dt'].hour >= one_hour and \
                                    one_image['image_dt'].hour < one_hour + 1]
            new_species_hour_images = [one_image for one_image in new_species_images if \
                                    one_image['image_dt'].hour >= one_hour and
                                    one_image['image_dt'].hour < one_hour + 1]

            frequency_full = 0.0
            if len(full_species_images) > 0:
                frequency_full = float(len(full_species_hour_images)) / \
                                                                    float(len(full_species_images))
            num_images_total_tull = num_images_total_tull + len(full_species_hour_images)

            frequency_new = 0.0
            if len(new_species_images) > 0:
                frequency_new = float(len(new_species_hour_images)) / float(len(new_species_images))
            num_images_total_new = num_images_total_new + len(new_species_hour_images)

            difference = frequency_full - frequency_new
            total_difference = total_difference + difference * difference

        total_difference = math.sqrt(total_difference)

        lunar_activities.append((species, total_difference, num_images_total_tull + \
                                                                            num_images_total_new))

    return lunar_activities


# pylint: disable=consider-using-f-string
@dataclasses.dataclass
class LunarActivityFormatter:
    """ Formats statistics about lunar activity
    """

    @staticmethod
    def print_lunar_activity(results: tuple, res_species: tuple) -> str:
        """ For all species the activity pattern for 11 days centered around a Full moon and New
            moon is given. The table shows the hour of the day,the number of records,and the
            frequency of total records for both a New moon and a Full moon. The moon completes one
            orbit around earth each 29.55 days. The Difference is the square root of the sum of the
            squared differences in frequency. The greater the difference, the more a species is
            active during one phase of the moon compared to the other phase. Note that birds are
            likely more active during a Full moon than a New moon, and nocturnal rodents might
            show the opposite pattern
        Arguments:
            results: the results to search through
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        result = 'LUNAR ACTIVITY PATTERN' + os.linesep
        result += '  New and full moon +/- 5 days activity patterns' + os.linesep
        result += '  Difference (large is greater difference)' + os.linesep

        full_moons = Analysis.get_full_moons(results['sorted_images_dt'][0],
                                results['sorted_images_dt'][len(results['sorted_images_dt']) - 1])
        new_moons = Analysis.get_new_moons(results['sorted_images_dt'][0],
                                results['sorted_images_dt'][len(results['sorted_images_dt']) - 1])

        full_images = [one_image for one_image in results['sorted_images_dt'] if \
                                                                    in_moons(one_image, full_moons)]
        new_images = [one_image for one_image in results['sorted_images_dt'] if \
                                                                    in_moons(one_image, new_moons)]

        for species in res_species:
            result += species['name'] + os.linesep
            result += '                 Full moon activity    New moon activity' + os.linesep
            result += '    Hour        Number    Frequency   Number    Frequency' + os.linesep

            full_species_images = [one_image for one_image in full_images if \
                                        Analysis.image_has_species(one_image, species['sci_name'])]

            new_species_images = [one_image for one_image in new_images if \
                                        Analysis.image_has_species(one_image, species['sci_name'])]

            num_images_total_tull = 0
            num_images_total_new = 0

            total_difference = 0.0

            to_add = ''

            # 24 hrs
            for one_hour in range(0, 24):
                full_species_hour_images = [one_image for one_image in full_species_images if \
                                        one_image['image_dt'].hour >= one_hour and \
                                        one_image['image_dt'].hour < one_hour + 1]
                new_species_hour_images = [one_image for one_image in new_species_images if \
                                        one_image['image_dt'].hour >= one_hour and
                                        one_image['image_dt'].hour < one_hour + 1]

                frequency_full = 0.0
                if len(full_species_images) > 0:
                    frequency_full = float(len(full_species_hour_images)) / \
                                                                    float(len(full_species_images))
                num_images_total_tull = num_images_total_tull + len(full_species_hour_images)

                frequency_new = 0.0
                if len(new_species_images) > 0:
                    frequency_new = float(len(new_species_hour_images)) / \
                                                                    float(len(new_species_images))
                num_images_total_new = num_images_total_new + len(new_species_hour_images)

                difference = frequency_full - frequency_new
                total_difference = total_difference + difference * difference

                to_add += '{:02d}:00-{:02d}:00      {:5d}      {:5.3f}      {:5d}      {:5.3f}'.\
                                                format( \
                                                    one_hour, one_hour + 1, \
                                                    len(full_species_hour_images), frequency_full, \
                                                    len(new_species_hour_images), frequency_new) + \
                                                os.linesep

            total_difference = math.sqrt(total_difference)

            to_add += 'Total            {:5d}                 {:5d}'.format(\
                                        num_images_total_tull, num_images_total_new) + os.linesep
            to_add += 'Difference       {:5.2f}'.format(total_difference) + os.linesep
            to_add += os.linesep

            if total_difference != 0:
                result += to_add

        return result

    @staticmethod
    def print_lunar_activity_most_different(results: tuple, res_species: tuple) -> str:
        """ The species whose lunar activity pattern is most different is given
        Arguments:
            results: the results to search through
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """

        lunar_activities = create_lunar_activity_table(results, res_species)

        result = ''

        if lunar_activities:
            # Sort by descending difference
            sorted_lunar_activities = sorted(lunar_activities, key=lambda activity: activity[1])

            result += 'SPECIES LUNAR ACTIVITY MOST DIFFERENT: '
            result += sorted_lunar_activities[0][0]['name'] + os.linesep

            result += os.linesep + 'Species                   Difference Number of records' + \
                                                                                        os.linesep
            for one_activity in sorted_lunar_activities:
                # Format species name, total difference, and total images for each lunar activity
                result += '{:<28s} {:4.2f}      {:7d}'.format( \
                                one_activity[0]['name'], one_activity[1], one_activity[2]) + \
                          os.linesep

            result += os.linesep

        return result
