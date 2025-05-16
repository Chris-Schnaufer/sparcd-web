""" Contains analysis functions for formatting """

import math

import MoonCalculator

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
                if one_species['sci_name'] == species:
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
        return math.ceil((end_dt - start_dt).total_seconds() / SECONDS_IN_DAY)

    @staticmethod
    def activityForImageList(results: tuple) -> int:
        """ Returns the number of distinct actions from the result set. Images MUST first be
        filtered by location and species to achieve a total accumulation
        Arguments:
            results: the results to analyze
        Returrns:
            The number of distinct actions found
        Notes:
            Actions are calculated when the time between two images is greater 
            than one hour
        """
        activities = 0

        prev_dt = None

        # Loop through the results and look at all the images
        for one_image in results['sorted_images_dt']:
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
    def periodForImageList(results: tuple, interval_minutes: int) -> int:
        """ Returns the number of distinct periods from the result set. Images MUST first be
        filtered by location and species to achieve a total accumulation
        Arguments:
            results: the results to analyze
            interval_minutes: the interval between images to be considered the same period (in minutes)
        Returns:
            The number of distinct periods found
        Notes:
            Periods are calculated when the time between two images is greater 
            than one hour
        """
        periods = 0

        prev_dt = None

        # Loop through the results and look at all the images
        for one_image in results['sorted_images_dt']:
            # Make sure we have what we need
            if not 'image_dt' in one_image or not one_image['image_dt']:
                continue

            # Get our first timestamp
            if prev_dt is None:
                periods += 1
                prev_dt = one_image['image_dt']
                continue

            # Compare minute difference in time to the limit (1 hour)
            if abs((one_image['image_dt'] - prev_dt).total_seconds()) / 60.0 <= interval_minutes:
                periods += 1
                prev_dt = one_image['image_dt']
                continue

        return periods

    @staticmethod
    def abundanceForImageList(results: tuple,  species: tuple, interval_minutes: int) -> int:
        """ Get the abundance value for a list of images. Images MUST first be filtered by
            location and species to achieve a total accumulation
        Arguments:
            results: the results to analyze
            species: the list of species
            interval_minutes: the interval between images to be considered the same period (in minutes)
        Returns:
            The number of distinct periods found
        Notes:
            Periods are calculated when the time between two images is greater 
            than one hour
        """
        abundance = 0

        species_names = [one_species['sci_name'] for one_species in species]

        last_image_dt = results['sorted_images_dt'][0]['image_dt']
        maxAnimalsInEvent = 0
        for one_image in results['sorted_images_dt']:
            difference_minutes = math.ceil((one_image['image_dt'] - last_image_dt).total_seconds() / 60.0)

            # If the current image is further away than the event interval, add the current max
            # number of animals to the total
            if (differenceMinutes >= eventInterval)
                abundance = abundance + maxAnimalsInEvent
                maxAnimalsInEvent = 0

            # The max number of animals is the max number of animals in this image or the max number
            # of animals in the last image
            for one_species in one_image['species']:
                if speciesFilter is None || one_species['sci_name'] in species_names:
                    maxAnimalsInEvent = math.max(maxAnimalsInEvent, one_species['count']);

            last_image_dt = one_image['image_dt'];

        abundance = abundance + maxAnimalsInEvent;

        return abundance;

    @staticmethod
    def locationsForImageList(images: tuple) -> tuple:
        """ Returns a list of locations that the image list contains
        Arguments:
            images: the tuple of images to search
        Return:
            Returns the tuple consisting of the unique locations
        """

        return tuple(set([tem['loc'] for item in images]))

    @staticmethod
    def getFullMoons(first: datetime, last: datetime) -> tuple:
        """ Returns the full moon dates that fall between the first and last dates, inclusive
        Arguments:
            first: the starting datetime to get the full moon for
            last: the ending datetime to get the full moon for
        Return:
            The tuple of calculated full moon dates
        """
        full_moons = []

        cur_date = first
        while cur_date <= last:
            # Localize the timestamps based upon either the server, the browser, or a user choice
            # TODO: Localize date before getting Julian date
            julian_date = MoonCalculator.getJulian(cur_date)

            phases = MoonCalculator.getPhase(julian_date)
            full_moon = MoonCalculator.getLunation(julian_date, phases[MoonCalculator.MOONPHASE], 180)
            full_millis = MoonCalculator.toMillisFromJulian(full_moon)

            # TODO: convert next date to localized timestamp
            next_full_moon_date = datetime.datetime.fromtimestamp(full_millis / 1000.0)
            fullMoons.append(next_full_moon_date)
            cur_date = next_full_moon_date + datetime.timedelta(days=20)

        return full_moons

    @staticmethod
    def getNewMoons(first: datetime, last: datetime) -> tuple:
        """ Returns the new moon dates that fall between the first and last dates, inclusive
        Arguments:
            first: the starting datetime to get the new moon for
            last: the ending datetime to get the new moon for
        Return:
            The tuple of calculated new moon dates
        """
        new_moons = []

        cur_date = first
        while (first2.isBefore(last2))
            # Localize the timestamps based upon either the server, the browser, or a user choice
            # TODO: Localize date before getting Julian date
            julian_date = MoonCalculator.getJulian(cur_date);

            phases = MoonCalculator.getPhase(julian_date)
            new_moon = MoonCalculator.getLunation(julian_date, phases[MoonCalculator.MOONPHASE], 0)
            new_millis = MoonCalculator.toMillisFromJulian(new_moon)

            # TODO: convert next date to localized timestamp
            next_new_moon_date = datetime.datetime.fromtimestamp(new_millis / 1000.0)
            new_moons.append(nextNewMoonDate)
            cur_date = nextNewMoonDate + datetime.timedelta(days=20)

        return new_moons
