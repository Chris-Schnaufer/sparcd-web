""" Contains the results of a query """

from text_formatters.analysis import Analysis

# The default interval value
DEFAULT_INTERVAL_MIN=0

class Results:
    """ Contains the results of a query """
    # All the known locations
    _all_locations = None
    # All the known species
    _all_species = None
    # Sorted images
    _images = None
    # Image interval
    interval_minutes = DEFAULT_INTERVAL_MIN
    # Sorted unique location ID
    _locations = None
    # Original results
    _results = None
    # Sorted unique species by nane
    _species = None
    # Images sorted by year
    _year_images = None
    # Sorted unique year
    _years = None

    def __init__(self, results: tuple, all_species: tuple, all_locations: tuple, \
                                                    interval_minutes: int=DEFAULT_INTERVAL_MIN):
        """ Initializer
        Arguments:
            results: the search results
            all_locations: all the known locations
            all_species: all the known species
            interval_minutes: the number of minutes between images to discard
        """
        self._all_locations = all_locations
        self._all_species = all_species

        # Check that we have results
        if results is None:
            return

        # Make sure results are iterable
        try:
            _ = results[0]
        except TypeError:
            return

        try:
            all_images, all_locations, all_years, all_species = self._initialize(results, \
                                                                        all_locations, all_species)
        except KeyError as ex:
            print('Invalid results specified', flush=True)
            print(ex, flush=True)
            return

        # Sort images by year
        year_images = [] * len(self._years)
        for one_image in all_images:
            cur_index = all_years.index(one_image['image_dt'].year)
            year_images[cur_index].append(one_image)

        # We are initialized, set our results
        self._results = results
        self._images = all_images
        self._locations = all_locations
        self._species = all_species
        self._year_images = year_images
        self._years = all_years
        self._interval_minutes = interval_minutes

    def _initialize(self, results: tuple, all_locations: tuple, all_species: tuple) -> tuple:
        """ Returns the image, locations, years, and species of the search results
        Arguments:
            results: the search results
            all_locations: all the known locations
            all_species: all the known species
        Returns:
            Returns a tupe containing the images (sorted by date and time), unique locations
            (sorted by nane), unique years (sorted by year), and unique species (sorted by name)
            of the search results
        """
        all_images = []
        for one_result in results:
            if one_result['images']:
                # Add the images, with location, to the list of all images
                all_images.extend([{'loc':one_result['loc']} | one_image for one_image in \
                                                                            one_result['images']])
        sorted_images = sorted(all_images, key=lambda cur_img: cur_img['image_dt'])

        # Get all the locations and check for an unknown
        sorted_locations = sorted(set(map(lambda cur_img: cur_img['loc'], all_images)))
        have_unknown = False
        mapped_values = []
        for test_value in sorted_locations: # TODO: Handle only active locations
            found_items = [one_location for one_location in all_locations if \
                                                    one_location['idProperty'] == test_value]
            if found_items and len(found_items) > 0:
                mapped_values.append(found_items[0])
            else:
                have_unknown = True

        sorted_locations = mapped_values
        if have_unknown:
            sorted_locations.append({'name':'Unknown', 'idPropert':'unknown', 'latProperty':0.0,
                                     'lngProperty':0.0, 'elevation':0.0})

        # Get all the species and check for unknown
        all_species = {}
        for one_image in self._images:
            for one_species in one_image['species']:
                if not one_species['sci_name'] in all_species:
                    all_species[one_species['name']] = {'first_image':one_image,
                                                        'last_image':one_image,
                                                        'sci_name':one_species['sci_name']
                                                       }
                else:
                    # Update the last image for the species if it's later than the current
                    # last image
                    if one_image['image_dt'] > \
                                        all_species[one_species['name']]['last_image']['image_dt']:
                        all_species[one_species['name']]['last_image'] = one_image['image_dt']

        sorted_species = sorted(map(lambda cur_species: cur_species['name'], \
                                [{'name':key} | item for key, item in all_species.items()]))
        have_unknown = False
        mapped_values = []
        for test_value in sorted_species:
            for one_species in all_species:
                found_items = [one_species for one_species in all_species if \
                                                            one_species['sci_name'] == test_value]
                if found_items and len(found_items) > 0:
                    mapped_values.append(found_items[0])
                else:
                    have_unknown = True

        sorted_species = mapped_values
        if have_unknown:
            sorted_species.append({'name': 'Unknown', 'scientificName': 'unknown', \
                                  'speciesIconURL': 'https://i.imgur.com/4qz5mI0.png', \
                                  'keyBinding': None
                                  })

        # Get all the years sorted
        sorted_years = sorted(set(map(lambda item: item['image_dt'].year, sorted_images)))

        return (sorted_images, sorted_locations, sorted_years, sorted_species)

    def get_interval(self) -> int:
        """ Returns the image interval in seconds """
        return self._interval_minutes

    def get_images(self) -> tuple:
        """ Returns the date sorted list of images
        Return:
            The tuple of images sorted by date
        """
        if self._images:
            return self._images

        raise RuntimeError('Call made to Results.get_images after bad initialization')

    def get_locations(self) -> tuple:
        """ Returns the unique locations sorted by ID
        Return:
            Returns the tuple of location IDs
        """
        if self._locations:
            return self._locations

        raise RuntimeError('Call made to Results.get_locations after bad initialization')

    def get_species(self) -> tuple:
        """ Returns the unique species sorted by name
        Return:
            Returns the tuple of species
        """
        if self._species:
            return self._species

        raise RuntimeError('Call made to Results.get_species after bad initialization')

    def get_years(self) -> tuple:
        """ Returns the unique sorted years
        Return:
            Returns the tuple of years
        """
        if self._years:
            return self._years

        raise RuntimeError('Call made to Results.get_years after bad initialization')

    def get_all_locations(self) -> tuple:
        """ Returns the list of all the locations """
        if self._all_locations:
            return self._all_locations

        raise RuntimeError('Call made to Results.get_all_locations after bad initialization')

    def get_all_species(self) -> tuple:
        """ Returns the list of all the species """
        if self._all_species:
            return self._all_species

        raise RuntimeError('Call made to Results.get_all_species after bad initialization')

    def get_year_images(self, year: int) -> tuple:
        """ Returns the list of images for a specific year
        Arguments:
            The year to return
        Returns:
            Returns the tuple of images for the specified year. An empty tuple is returned if the
            year doesn't have any images associated with it
        """
        if self._years is None or self._year_images is None:
            raise RuntimeError('Call made to Results.get_year_images after bad initialization')

        result = ()
        try:
            cur_index = self._years.index(year)
            if cur_index < len(self._year_images):
                result = self._year_images[cur_index]
        except ValueError:
            pass

        return result

    def filter_month(self, images: tuple, month: int) -> tuple:
        """ Filters the images by image month
        Arguments:
            images: the tuple of images to search through
            month: the month to filter on (months start at zero - 0)
        Return:
            A tuple containing the images for that month
        """
        return [one_image for one_image in images if one_image['image_dt'].month == month]

    def filter_location(self, images: tuple, location_id: str) -> tuple:
        """ Filters the image by the location ID
        Arguments:
            images: the tuple of images to search through
            location_id: the location ID to filter on
        Return:
            A tuple containing the images for that location
        """
        return [one_image for one_image in images if one_image['loc'] == location_id]

    def filter_species(self, images: tuple, species_sci_name: str) -> tuple:
        """ Filters the image by the species scientific name
        Arguments:
            images: the tuple of images to search through
            species_sci_name: the scientific species name to sort on
        Return:
            A tuple containing the images for that species
        """
        return [one_image for one_image in images if \
                                            Analysis.image_has_species(one_image, species_sci_name)]
