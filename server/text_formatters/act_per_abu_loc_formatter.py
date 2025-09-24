""" Formats species activities, abundance, and period at locations information """

import dataclasses
import os

from analysis import Analysis
from results import Results

# pylint: disable=consider-using-f-string
@dataclasses.dataclass
class ActPerAbuLocFormatter:
    """ Formats species activities, abundance, and period at locations information
    """

    @staticmethod
    def print_number_of_pictures_by_year(results: Results) -> str:
        """ For each year the total number of pictures of all species (All), the number of pictures
            that are used to calculate the activity pattern (Activity), the number of independent
            pictures (Period), and the total number of individuals in all the independent pitures
            (Abundance). This is followed by the total (Total) for all years
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'NUMBER OF PICTURES AND FILTERED PICTURES PER YEAR' + os.linesep + \
                 '        Year       All Activity   Period Abundance' + os.linesep

        image_total = 0
        activity_total = 0
        period_total = 0
        abundance_total = 0
        for year in results.get_years():
            year_image_total = 0
            year_activity_total = 0
            year_period_total = 0
            year_abundance_total = 0

            year_images = results.get_year_images(year)
            for one_species in results.get_species():
                year_species_images = results.filter_species(year_images, \
                                                                    one_species['scientificName'])
                year_image_total = year_image_total + len(year_species_images)
                year_activity_total += \
                        Analysis.activity_for_image_list(year_species_images)
                year_period_total += \
                        Analysis.period_for_image_list(year_species_images, results.get_interval())
                year_abundance_total += \
                        Analysis.abundance_for_image_list(year_species_images, \
                                            results.get_interval(), one_species['scientificName'])
            image_total += year_image_total
            activity_total += year_activity_total
            period_total += year_period_total
            abundance_total += year_abundance_total
            result += '        {:4d}   {:7d}  {:7d}  {:7d}  {:7d}'.format(year, year_image_total, \
                                            year_activity_total, year_period_total, \
                                            year_abundance_total) + \
                       os.linesep

        result += '        Total  {:7d}  {:7d}  {:7d}  {:7d}'.format(image_total, activity_total, \
                                            period_total, abundance_total) + os.linesep + os.linesep

        return result

    @staticmethod
    def print_number_of_pictures_by_species_by_year(results: Results) -> str:
        """ For each species to be analyzed and for each year, the total number of pictures (All),
            the number of pictures that are used to calculate the activity pattern (Activity), the
            number of independent pictures (Period), the total number of individuals in all the
            independent pitures (Abundance), and the number of locations where the species was
            recorded (Sites). This is followed by the total (Total) for all years
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'NUMBER OF PICTURES BY SPECIES BY YEAR' + os.linesep

        for one_species in results.get_species_by_name():
            result += '  ' + one_species['name'] + os.linesep
            result += '        Year       All Activity   Period Abundance Locations' + os.linesep

            species_image_total = 0
            species_activity_total = 0
            species_period_total = 0
            species_abundance_total = 0
            species_location_total = 0
            species_images = results.get_species_images(one_species['scientificName'])

            for one_year in results.get_years():
                species_year_images = results.filter_year(species_images, one_year)
                species_activity = Analysis.activity_for_image_list(species_year_images)
                species_period = Analysis.period_for_image_list(species_year_images, \
                                                                            results.get_interval())
                species_abundance = Analysis.abundance_for_image_list(species_year_images, \
                                            results.get_interval(), one_species['scientificName'])
                species_location = len(results.locations_for_image_list(species_year_images))
                species_image_total += len(species_year_images)
                species_activity_total += species_activity
                species_period_total += species_period
                species_abundance_total += species_abundance
                species_location_total += species_location
                result += '        {:4d}   {:7d}  {:7d}  {:7d}  {:7d}  {:7d}'.format(one_year, \
                                            len(species_year_images), species_activity, \
                                            species_period, species_abundance, species_location) + \
                          os.linesep

            result += '        Total  {:7d}  {:7d}  {:7d}  {:7d}  {:7d}'.format(\
                                            species_image_total, species_activity_total, \
                                            species_period_total, species_abundance_total, \
                                            species_location_total) + \
                      os.linesep + os.linesep

        return result

    @staticmethod
    def print_number_of_pictures_by_percent_total(results: Results) -> str:
        """ A list of the number of independent pictures of each species ranked by total from most
            to least, and the percent of the total number of all independent pictures. The total
            number of indepdenent pictures is given
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES RANKED BY NUMBER OF INDEPENDENT PICTURES AND PERCENT OF TOTAL' + \
                                                                                    os.linesep
        result += '     Species                   Total  Percent' + os.linesep

        period_total = 0
        for one_year in results.get_years():
            year_period_total = 0
            year_images = results.get_year_images(one_year)

            for one_species in results.get_species():
                year_species_images = results.filter_species(year_images, \
                                                                    one_species['scientificName'])
                year_period_total += \
                            Analysis.period_for_image_list(year_species_images, \
                                                                            results.get_interval())
            period_total = period_total + year_period_total

        for one_species in results.get_species_by_name():
            species_period_total = 0
            species_images = results.get_species_images(one_species['scientificName'])

            for one_year in results.get_years():
                species_year_images = results.filter_year(species_images, one_year)
                species_period_total += \
                                Analysis.period_for_image_list(species_year_images, \
                                                                            results.get_interval())
            result += '  {:<28s} {:5d}  {:7.2f}'.format(one_species['name'], species_period_total, \
                                    (float(species_period_total) / float(period_total)) * 100.0) + \
                      os.linesep

        result += '  Total pictures               {:5d}   100.00'.format(period_total) + \
                        os.linesep + os.linesep

        return result

    @staticmethod
    def print_species_abundance(results: Results) -> str:
        """ For each species (SPECIES) a list of the number of independent pictures (NUMBER PICS),
            proportion of the total number of all independent pictures (PROPORTION), the average
            number of individuals in each picture (AVG NUM INDIVS), and the proportion of the total
            number of individuals for that species divided by the total number of all individuals
            (PROPORTION). The total number of all independent pictures (Total) is given in the last
            line
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES ABUNDANCE' + os.linesep
        result += '  One record of each species per location per PERIOD' + os.linesep
        result += 'SPECIES                      NUMBER PICS      RELATIVE ABUNDANCE     ' \
                  'AVG NUM INDIVS     ABUNDANCE OF INDIVS' + os.linesep

        period_over_all_species = 0
        num_animals_photographed = 0

        for one_species in results.get_species_by_name():
            species_images = results.get_species_images(one_species['scientificName'])

            for one_year in results.get_years():
                species_year_images = results.filter_year(species_images, one_year)
                period_over_all_species += \
                        Analysis.period_for_image_list(species_year_images, results.get_interval())
                num_animals_photographed += \
                        Analysis.abundance_for_image_list(species_year_images, \
                                            results.get_interval(), one_species['scientificName'])

        for one_species in results.get_species():
            species_images = results.get_species_images(one_species['scientificName'])
            abundance_total = 0
            period_total = 0
            for one_year in results.get_years():
                species_year_images = results.filter_year(species_images, one_year)
                abundance_total += \
                            Analysis.abundance_for_image_list(species_year_images, \
                                            results.get_interval(), one_species['scientificName'])
                period_total += \
                            Analysis.period_for_image_list(species_year_images, \
                                                                            results.get_interval())

            result += '{:<28s} {:7d}               {:7.2f}             {:7.2f}             ' \
                      '{:7.2f}'.format(one_species['name'], period_total, \
                                100.0 * float(period_total) / float(period_over_all_species), \
                                float(abundance_total)/float(period_total) if period_total else 0,\
                                100.0 * float(abundance_total) / float(num_animals_photographed)) \
                      + os.linesep


        result += 'Total                        {:7d}                100.00'.format( \
                                                                        period_over_all_species)
        result += os.linesep + os.linesep

        return result

    @staticmethod
    def print_species_abundance_year_site(results: tuple) -> str:
        """ Species average abundance by year and site
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES AVERAGE ABUNDANCE BY YEAR AND SITE' + os.linesep
        result += 'One record of each species per location per PERIOD' + os.linesep
        result += '               Use maximum number of individuals per PERIOD' + os.linesep

        for one_year in results.get_years():
            year_images = results.get_year_images(one_year)
            result += str(one_year) + os.linesep
            result += 'Species                     '

            for one_location in results.get_locations():
                result += '{:<5s} '.format(one_location['nameProperty'][:5])
            result += os.linesep

            for one_species in results.get_species_by_name():
                year_species_images = results.filter_species(year_images, \
                                                                    one_species['scientificName'])
                result += '{:<28s}'.format(one_species['name'])

                for one_location in results.get_locations():
                    year_species_loc_images = results.filter_location(year_species_images, \
                                                                        one_location['idProperty'])
                    abundance = Analysis.abundance_for_image_list(year_species_loc_images, \
                                            results.get_interval(), one_species['scientificName'])

                    loc_species_images = results.filter_species(\
                                            results.filter_location(results.get_images(), \
                                                                    one_location['idProperty']), \
                                            one_species['scientificName'])
                    period = Analysis.period_for_image_list(loc_species_images, \
                                                                            results.get_interval())

                    result += '{:5.2f} '.format(0.0 if period == 0 else \
                                                                float(abundance) / float(period))

                result += os.linesep

            result += os.linesep

        return result

    @staticmethod
    def print_species_abundance_site(results: tuple) -> str:
        """ Species average abundance by site for all years
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES AVERAGE ABUNDANCE BY SITE ALL YEARS' + os.linesep

        if results.get_years():
            result += 'Years ' + str(results.get_first_year()) + ' to ' + \
                                                str(results.get_last_year()) + os.linesep

        result += 'Species                     '
        for location in results.get_locations():
            result += '{:<5s} '.format(location['nameProperty'][:5])
        result += os.linesep

        for one_species in results.get_species_by_name():
            species_images = results.get_species_images(one_species['scientificName'])
            result += '{:<28s}'.format(one_species['name'])

            for one_location in results.get_locations():
                species_loc_images = results.filter_location(species_images, \
                                                                        one_location['idProperty'])
                abundance = Analysis.abundance_for_image_list(species_loc_images, \
                                            results.get_interval(), one_species['scientificName'])

                loc_species_images = \
                            results.filter_species( \
                                        results.get_location_images(one_location['idProperty']), \
                                        one_species['scientificName'])
                period = Analysis.period_for_image_list(loc_species_images, results.get_interval())

                result += '{:5.2f} '.format(0.0 if period == 0 else float(abundance)/float(period))

            result += os.linesep

        result += os.linesep

        return result
