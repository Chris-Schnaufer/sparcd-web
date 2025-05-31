""" Contains analysis functions for formatting """

import dataclasses
import datetime
import math

import ephem

# The number of seconds in a day as a float to capture fractions of days
SECONDS_IN_DAY = 60.0 * 60.0 * 24.0

@dataclasses.dataclass
class Analysis:
    """ Performs analysis on image lists
    """

    @staticmethod
    def image_has_species(image: dict, species: str) -> bool:
        """ Determines if the image has the species listed
        Arguments:
            image: the image to check
            species: the species scientific name to look for
        Return:
            Return True if the image has at least one instance of the species
            and False otherwise
        """
        if image and 'species' in image:
            for one_species in image['species']:
                if one_species['scientificName'] == species:
                    return True

        return False

    @staticmethod
    def get_days_span(end_dt: datetime.datetime, start_dt: datetime.datetime) -> int:
        """ Returns the number of days between the two timestamps
        Arguments:
            end_dt: the ending timestamp
            start_dt: the starting timestamp
        Return:
            The number of days between the timestamps as an integer. Will return a 
            negative number of end_dt is earlier than start_dt
        """
        return max(math.ceil(abs((end_dt - start_dt).total_seconds()) / SECONDS_IN_DAY), 1)

    @staticmethod
    def activity_for_image_list(images: tuple) -> int:
        """ Returns the number of distinct actions from the result set. Images MUST first be
        filtered by location and species to achieve a total accumulation
        Arguments:
            images: the tuple of images to process
        Returrns:
            The number of distinct actions found
        Notes:
            Actions are calculated when the time between two images is greater 
            than one hour
        """
        activities = 0

        prev_dt = None

        # Loop through the results and look at all the images
        for one_image in images:
            # Make sure we have what we need
            if not 'image_dt' in one_image or not one_image['image_dt']:
                continue

            # Get our first timestamp
            if prev_dt is None:
                activities += 1
                prev_dt = one_image['image_dt']
                continue

            # Compare minute difference in time to the limit (1 hour)
            if abs((one_image['image_dt'] - prev_dt).total_seconds()) / 60.0 >= 60:
                activities += 1
                prev_dt = one_image['image_dt']
                continue

        return activities


    @staticmethod
    def period_for_image_list(images: tuple, interval_minutes: int) -> int:
        """ Returns the number of distinct periods from the result set. Images MUST first be
        filtered by location and species to achieve a total accumulation
        Arguments:
            images: the tuple of images to process
            interval_minutes: the number of minutes before a new event is considered
        Returns:
            The number of distinct periods found
        Notes:
            Periods are calculated when the time between two images is greater 
            than one hour
        """
        periods = 0

        prev_dt = None

        # Loop through the results and look at all the images
        for one_image in images:
            # Make sure we have what we need
            if not 'image_dt' in one_image or not one_image['image_dt']:
                continue

            # Get our first timestamp
            if prev_dt is None:
                periods += 1
                prev_dt = one_image['image_dt']
                continue

            # Compare minute difference in time to the limit (1 hour)
            if abs((one_image['image_dt'] - prev_dt).total_seconds()) / 60.0 >= interval_minutes:
                periods += 1
                prev_dt = one_image['image_dt']
                continue

        return periods

    @staticmethod
    def abundance_for_image_list(images: tuple, interval_minutes: int, species_filter: str=None) \
                                                                                            -> int:
        """ Get the abundance value for a list of images. Images MUST first be filtered by
            location and species to achieve a total accumulation
        Arguments:
            images: the tuple of images to process
            interval_minutes: the number of minutes before a new event is considered
            species_filter: optional name of a specific species to look for
        Returns:
            The number of distinct periods found
        Notes:
            Periods are calculated when the time between two images is greater 
            than one hour
        """
        abundance = 0
        if not images or len(images) <= 0:
            return abundance

        last_image_dt = images[0]['image_dt']
        max_animals_in_event = 0
        for one_image in images:
            difference_minutes = math.ceil((one_image['image_dt'] - last_image_dt).\
                                                                        total_seconds() / 60.0)

            # If the current image is further away than the event interval, add the current max
            # number of animals to the total
            if difference_minutes >= interval_minutes:
                abundance = abundance + max_animals_in_event
                max_animals_in_event = 0

            # The max number of animals is the max number of animals in this image or the max number
            # of animals in the last image
            for one_species in one_image['species']:
                if species_filter is None or one_species['scientificName'] == species_filter:
                    max_animals_in_event = max(max_animals_in_event, int(one_species['count']))

            last_image_dt = one_image['image_dt']

        abundance = abundance + max_animals_in_event

        return abundance

    @staticmethod
    def get_full_moons(first: datetime, last: datetime) -> tuple:
        """ Returns the full moon dates that fall between the first and last dates, inclusive
        Arguments:
            first: the starting datetime to get the full moon for
            last: the ending datetime to get the full moon for
        Return:
            The tuple of calculated full moon dates
        """
        full_moons = []

        date = ephem.Date(datetime.date(first.year, first.month, first.day))
        while True:
            date = ephem.next_full_moon(date)
            if date.datetime().date() <= last.date():
                full_moons.append(date.datetime())
            else:
                break

        return full_moons

    @staticmethod
    def get_new_moons(first: datetime, last: datetime) -> tuple:
        """ Returns the new moon dates that fall between the first and last dates, inclusive
        Arguments:
            first: the starting datetime to get the new moon for
            last: the ending datetime to get the new moon for
        Return:
            The tuple of calculated new moon dates
        """
        new_moons = []

        date = ephem.Date(datetime.date(first.year, first.month, first.day))
        while True:
            date = ephem.next_new_moon(date)
            if date.datetime().date() <= last.date():
                new_moons.append(date.datetime())
            else:
                break

        return new_moons
