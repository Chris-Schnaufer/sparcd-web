""" Formats statistics about lunar activity """

import dataclasses
import datetime
import math
import os

from .analysis import Analysis
from .results import Results

# Number of days (in seconds) for a datetime to be considered to be within a moon phase
MOON_PHASE_DATE_DIFF_SEC = 5 * 24 * 60 * 60     # Five days in seconds


def in_moons(image_date: datetime.datetime, moons: tuple) -> bool:
    """ Returns whether or not the image date falls within a full moon
    Arguments:
        image_date: the date to check
        moons: an iterator containing the datetime of the moons to check
    Return:
        Returns True/False for if the image date is within range of the moons
        contain None
    """
    for one_moon in moons:
        if abs((one_moon - image_date).total_seconds()) < MOON_PHASE_DATE_DIFF_SEC:
            return True

    return False

def in_moons_debug(image_date: datetime.datetime, moons: tuple) -> bool:
    """ Returns whether or not the image date falls within a full moon
    Arguments:
        image_date: the date to check
        moons: an iterator containing the datetime of the moons to check
    Return:
        Returns True/False for if the image date is within range of the moons
        contain None
    """
    for one_moon in moons:
        if abs((one_moon - image_date).total_seconds()) < MOON_PHASE_DATE_DIFF_SEC:
            return True

    return False


def create_lunar_activity_table(results: Results)-> tuple:
    """ Returns a tuple containing tuples of species, total difference, and total images
    Arguments:
        results: the results to search through
        res_species: all distinct result species information
    Return:
        Returns the table of information
    """
    lunar_activities = []

    full_moons = Analysis.get_full_moons(results.get_first_image()['image_dt'], \
                                                            results.get_last_image()['image_dt'])
    new_moons = Analysis.get_new_moons(results.get_first_image()['image_dt'], \
                                                            results.get_last_image()['image_dt'])

    full_images = [one_image for one_image in results.get_images() if \
                                                        in_moons(one_image['image_dt'], full_moons)]
    new_images = [one_image for one_image in results.get_images() if \
                                                        in_moons(one_image['image_dt'], new_moons)]

    for species in results.get_species_by_name():
        num_images_total_full = 0
        num_images_total_new = 0

        total_difference = 0.0

        full_species_images = results.filter_species(full_images, species['scientificName'])
        new_species_images = results.filter_species(new_images, species['scientificName'])

        # 24 hrs
        for one_hour in range(0, 24):
            full_species_hour_images = results.filter_hours(full_species_images, \
                                                                            one_hour, one_hour + 1)
            new_species_hour_images = results.filter_hours(new_species_images, \
                                                                            one_hour, one_hour + 1)

            frequency_full = 0.0
            if len(full_species_images) > 0:
                frequency_full = float(len(full_species_hour_images)) / \
                                                                    float(len(full_species_images))
            num_images_total_full += len(full_species_hour_images)

            frequency_new = 0.0
            if len(new_species_images) > 0:
                frequency_new = float(len(new_species_hour_images)) / float(len(new_species_images))
            num_images_total_new += len(new_species_hour_images)

            difference = frequency_full - frequency_new
            total_difference = total_difference + (difference * difference)

        total_difference = math.sqrt(total_difference)

        lunar_activities.append((species, total_difference, num_images_total_full + \
                                                                            num_images_total_new))

    return lunar_activities


# pylint: disable=consider-using-f-string
@dataclasses.dataclass
class LunarActivityFormatter:
    """ Formats statistics about lunar activity
    """

    @staticmethod
    def print_lunar_activity(results: Results) -> str:
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
        Return:
            Returns the image analysis text
        """
        result = 'LUNAR ACTIVITY PATTERN' + os.linesep
        result += '  New and full moon +/- 5 days activity patterns' + os.linesep
        result += '  Difference (large is greater difference)' + os.linesep

        full_moons = Analysis.get_full_moons(results.get_first_image()['image_dt'], \
                                                            results.get_last_image()['image_dt'])
        new_moons = Analysis.get_new_moons(results.get_first_image()['image_dt'], \
                                                            results.get_last_image()['image_dt'])

        full_images = [one_image for one_image in results.get_images() if \
                                                        in_moons(one_image['image_dt'], full_moons)]
        new_images = [one_image for one_image in results.get_images() if \
                                                        in_moons(one_image['image_dt'], new_moons)]

        for species in results.get_species_by_name():
            result += species['name'] + os.linesep
            result += '                 Full moon activity    New moon activity' + os.linesep
            result += '    Hour        Number    Frequency   Number    Frequency' + os.linesep

            full_species_images = results.filter_species(full_images, species['scientificName'])
            new_species_images = results.filter_species(new_images, species['scientificName'])

            num_images_total_full = 0
            num_images_total_new = 0

            total_difference = 0.0

            to_add = ''

            # 24 hrs
            for one_hour in range(0, 24):
                full_species_hour_images = results.filter_hours(full_species_images, \
                                                                            one_hour, one_hour + 1)
                new_species_hour_images = results.filter_hours(new_species_images, \
                                                                            one_hour, one_hour + 1)

                frequency_full = 0.0
                if len(full_species_images) > 0:
                    frequency_full = float(len(full_species_hour_images)) / \
                                                                    float(len(full_species_images))
                num_images_total_full += len(full_species_hour_images)

                frequency_new = 0.0
                if len(new_species_images) > 0:
                    frequency_new = float(len(new_species_hour_images)) / \
                                                                    float(len(new_species_images))
                num_images_total_new += len(new_species_hour_images)

                difference = frequency_full - frequency_new
                total_difference += difference * difference

                to_add += '{:02d}:00-{:02d}:00      {:5d}      {:5.3f}      {:5d}      {:5.3f}'.\
                                                format( \
                                                    one_hour, one_hour + 1, \
                                                    len(full_species_hour_images), frequency_full, \
                                                    len(new_species_hour_images), frequency_new) + \
                                                os.linesep

            total_difference = math.sqrt(total_difference)

            to_add += 'Total            {:5d}                 {:5d}'.format(\
                                        num_images_total_full, num_images_total_new) + os.linesep
            to_add += 'Difference       {:5.2f}'.format(total_difference) + os.linesep
            to_add += os.linesep

            if total_difference != 0:
                result += to_add

        return result

    @staticmethod
    def print_lunar_activity_most_different(results: Results) -> str:
        """ The species whose lunar activity pattern is most different is given
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """

        lunar_activities = create_lunar_activity_table(results)

        result = ''

        if lunar_activities:
            # Sort by descending difference
            sorted_lunar_activities = sorted(lunar_activities, key=lambda activity: activity[1], reverse=True)

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
