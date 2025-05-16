""" Formats species activities, abundance, and period at locations information """

import datetime
import math
import os

import Analysis

@dataclasses.dataclass
class ActPerAbuLocFormatter:
    """ Formats species activities, abundance, and period at locations information
    """

    @staticmethod
    def printNumberOfPicturesByYear(results: tuple, res_locations: tuple, res_species: tuple, \
                                    interval_minutes: int) -> str:
        """ For each year the total number of pictures of all species (All), the number of pictures that are
            used to calculate the activity pattern (Activity), the number of independent pictures (Period),
            and the total number of individuals in all the independent pitures (Abundance). This
            is followed by the total (Total) for all years
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
            interval_minutes: the interval between images to be considered the same period (in minutes)
        Return:
            Returns the image analysis text
        """
        result = 'NUMBER OF PICTURES AND FILTERED PICTURES PER YEAR' + os.linesep + \
                 '        Year       All Activity   Period Abundance' + os.linesep

        image_total = 0
        activity_total = 0
        period_total = 0
        abundance_total = 0
        for year in sorted(set([item['image_dt'].year for item in results['sorted_images_dt']])):
            year_image_total = 0
            year_activity_total = 0
            year_period_total = 0
            year_abundance_total = 0

            year_images = [item for item in results['sorted_images_dt'] if item['image_dt'].year == year]
            for species in res_species:
                year_species = [item for item in year_images if Analysis.image_has_species(item, species['sci_name'])]
                year_image_total = year_image_total + len(year_species)
                year_activity_total = year_activity_total + Analysis.activityForImageList(year_species);
                year_period_total = year_period_total + Analysis.periodForImageList(year_species, interval_minutes);
                year_abundance_total = year_abundance_total + Analysis.abundanceForImageList(year_species, species, interval_minutes);
            image_total = image_total + year_image_total;
            activity_total = activity_total + year_activity_total;
            period_total = period_total + year_period_total;
            abundance_total = abundance_total + year_abundance_total;
            result += '        {:4d}   {:7d}  {:7d}  {:7d}  {:7d}'.format(year, year_image_total, \
                                            year_activity_total, year_period_total, year_abundance_total) +
                       os.linesep

        result += '        Total  {:7d}  {:7d}  {:7d}  {:7d}'.format(image_total, activity_total, period_total, \
                                            abundance_total) +
                  os.linesep + os.linesep

        return result

    @staticmethod
    def printNumberOfPicturesBySpeciesByYear(results: tuple, res_locations: tuple, res_species: tuple, \
                                             interval_minutes: int) -> str:
        """ For each species to be analyzed and for each year, the total number of pictures (All), the number of
            pictures that are used to calculate the activity pattern (Activity), the number of independent pictures
            (Period), the total number of individuals in all the independent pitures (Abundance), and the number of
            locations where the species was recorded (Sites). This is followed by the total (Total) for all years
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
            interval_minutes: the interval between images to be considered the same period (in minutes)
        Return:
            Returns the image analysis text
        """
        result = 'NUMBER OF PICTURES BY SPECIES BY YEAR' + os.linesep

        sorted_image_years = sorted(set([item['image_dt'].year for item in results['sorted_images_dt']]))
        for one_species in res_species:
            result += '  ' + one_species['name'] + os.linesep
            result += '        Year       All Activity   Period Abundance Locations' + os.linesep

            int species_image_total = 0;
            int species_activity_total = 0;
            int species_period_total = 0;
            int species_abundance_total = 0;
            int species_locationTotal = 0;
            image_species = [item for item in result['sorted_images_dt'] if Analysis.image_has_species(item, species['sci_name'])]
            for one_year in sorted_image_years:
                with_species_year = [one_image for one_image in image_species if one_image['image_dt'].year == one_year]
                species_image = with_species_year.size();
                species_activity = Analysis.activityForImageList(withSpeciesYear);
                species_period = Analysis.periodForImageList(withSpeciesYear, interval_minutes);
                species_abundance = Analysis.abundanceForImageList(withSpeciesYear, species, interval_minutes);
                species_location = Analysis.locationsForImageList(withSpeciesYear).size();
                species_image_total = species_image_total + species_image;
                species_activity_total = species_activity_total + species_activity;
                species_period_total = species_period_total + species_period;
                species_abundance_total = species_abundance_total + species_abundance;
                species_locationTotal = species_locationTotal + species_location;
                result += '        {:4d}   {:7d}  {:7d}  {:7d}  {:7d}  {:7d}'.format(year, species_image, \
                                                    species_activity, species_period, species_abundance, species_location) + \
                          os.linesep

            result = '        Total  {:7d}  {:7d}  {:7d}  {:7d}  {:7d}'.format(species_image_total, species_activity_total, \
                                                    species_period_total, species_abundance_total, species_locationTotal) + \
                      os.linesep + os.linesep

        return result

    @staticmethod
    def printNumberOfPicturesByPercentTotal(results: tuple, res_locations: tuple, res_species: tuple, \
                                            interval_minutes: int) -> str:
        """ A list of the number of independent pictures of each species ranked by total from most to least, and the
            percent of the total number of all independent pictures. The total number of indepdenent pictures is given
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
            interval_minutes: the interval between images to be considered the same period (in minutes)
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES RANKED BY NUMBER OF INDEPENDENT PICTURES AND PERCENT OF TOTAL' + os.linesep
        result += '     Species                   Total  Percent' + os.linesep

        sorted_image_years = sorted(set([item['image_dt'].year for item in results['sorted_images_dt']]))
        period_total = 0;
        for one_year in sorted_image_years:
            year_period_total = 0;
            year_images = [item for item in results['sorted_images_dt'] if item['image_dt'].year == year]
            for one_species in res_species:
                year_species_images = [one_image in year_images if Analysis.image_has_species(one_image, one_species['sci_name'])]
                year_period_total = year_period_total + Analysis.periodForImageList(year_species_images, interval_minutes)
            period_total = period_total + year_period_total

        for one_species in res_species:
            species_period_total = 0
            species_images = [one_image in results['sorted_images_dt'] if Analysis.image_has_species(one_image, one_species['sci_name'])]
            for one_year in sorted_image_years:
                species_year_images = [item for item in species_images if item['image_dt'].year == year]
                species_period_total = species_period_total + Analysis.periodForImageList(species_year_images, interval_mimutes);
            result += '  {:<28s} {:5d}  {:7.2f}'.format(one_species['name'], species_period_total, \
                                                    ((species_period_total * 1.0) / period_total) * 100.0) + \
                      os.linesep

        result += '  Total pictures               {:5d}   100.00'.format(period_total) + \
                        os.linesep + os.linesep

        return result
        
    @staticmethod
    def printspecies_abundance(results: tuple, res_locations: tuple, res_species: tuple, \
                              interval_minutes: int) -> str:
        """ For each species (SPECIES) a list of the number of independent pictures (NUMBER PICS),
            proportion of the total number of all independent pictures (PROPORTION), the average number of individuals
            in each picture (AVG NUM INDIVS), and the proportion of the total number of individuals for that species
            divided by the total number of all individuals (PROPORTION). The total number of all independent pictures
            (Total) is given in the last line
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
            interval_minutes: the interval between images to be considered the same period (in minutes)
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES ABUNDANCE' + os.linesep
        result += '  One record of each species per location per PERIOD' + os.linesep
        result += 'SPECIES                      NUMBER PICS      RELATIVE ABUNDANCE     AVG NUM INDIVS     ABUNDANCE OF INDIVS' + \
                                os.linesep

        period_over_all_species = 0;
        num_animals_photographed = 0;
        sorted_image_years = sorted(set([item['image_dt'].year for item in results['sorted_images_dt']]))

        for species in res_species:
            species_images = [one_image in results['sorted_images_dt'] if Analysis.image_has_species(one_image, one_species['sci_name'])]
            for one_year in sorted_image_years:
                species_year_images = [item for item in species_images if item['image_dt'].year == year]

        for species in res_species:
            species_images = [one_image in results['sorted_images_dt'] if Analysis.image_has_species(one_image, one_species['sci_name'])]
            abundance_total = 0;
            period_total = 0;
            for one_year in sorted_image_years:
                species_year_images = [item for item in species_images if item['image_dt'].year == year]
                abundance_total = abundance_total + Analysis.abundanceForImageList(species_year_images, res_species)
                period_total = period_total + Analysis.periodForImageList(species_year_images, interval_minutes)

            result += '{:<28s} {:7d}               {:7.2f}             {:7.2f}             {:7.2f}'.format( \
                                    one_species['name'], period_total, 100.0 * float(period_total) / float(period_over_all_species), \
                                    float(abundance_total) / float(period_total), float(abundance_total) / float(num_animals_photographed) * 100.0) \
                      + os.linesep

            period_over_all_species = period_over_all_species + abundance_total
            num_animals_photographed = num_animals_photographed + 

        result += 'Total                        {:7d}                100.00'.format(period_over_all_species) + os.linesep
        result += os.linesep + os.linesep

        return result

    @staticmethod
    def printspecies_abundanceYearSite(results: tuple, res_locations: tuple, res_species: tuple, \
                                      interval_minutes: int) -> str:
        """ Species average abundance by year and site
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
            interval_minutes: the interval between images to be considered the same period (in minutes)
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES AVERAGE ABUNDANCE BY YEAR AND SITE' + os.linesep
        result += 'One record of each species per location per PERIOD' + os.linesep
        result += '               Use maximum number of individuals per PERIOD' + os.linesep

        sorted_image_years = sorted(set([item['image_dt'].year for item in results['sorted_images_dt']]))
        for one_year in sorted_image_years:
            year_images = [item for item in results['sorted_images_dt'] if item['image_dt'].year == year]
            result += str(year) + os.linesep
            result += 'Species                     '

            for one_loc in res_locations:
                result += '{:<5s} '.format(one_loc['name'][:5])
            result += os.linesep

            for one_species in res_species:
                year_species_images = [one_image for one_image in year_images if Analysis.image_has_species(one_image, one_species['sci_name'])]
                result += '{%<28s}'.format(one_species['name'])

                for one_loc in res_locations:
                    year_species_loc_images = [one_image for one_image in year_species_images if one_image['loc'] == one_loc['idProperty']]
                    abundance = Analysis.abundanceForImageList(year_species_loc_images, res_species);

                    loc_species_images = [one_image for one_image in results['sorted_images_dt'] if \
                                                one_image['loc'] == one_loc['idProperty'] and Analysis.image_has_species(one_image, one_species)]
                    period = Analysis.periodForImageList(loc_species_image, interval_minutes);

                    result += '{:5.2f} '.format(0 if period == 0 else float(abundance) / float(period))

                result += os.linesep

            result += os.linesep

        return result
        
    @staticmethod
    def printspecies_abundanceSite(results: tuple, res_locations: tuple, res_species: tuple, \
                                  interval_minutes: int) -> str:
        """ Species average abundance by site for all years
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
            interval_minutes: the interval between images to be considered the same period (in minutes)
        Return:
            Returns the image analysis text
        """
        result = 'SPECIES AVERAGE ABUNDANCE BY SITE ALL YEARS' + os.linesep

        sorted_image_years = sorted(set([item['image_dt'].year for item in results['sorted_images_dt']]))
        num_years = len(sorted_image_years)
        if num_years > 0:
            result += 'Years ' + str(sorted_image_years[0]) + ' to ' + str(sorted_image_years[num_years - 1]) + os.linesep

        result += 'Species                     '
        for one_loc in res_locations:
            result += '{:<5s} '.format(one_loc['name'][:5])
        result += os.linesep

        for species in res_species:
            species_images = [one_image for one_image in year_images if Analysis.image_has_species(one_image, one_species['sci_name'])]
            result += '{:<28s}'.format(species['name'])

            for location in res_locations:
                species_loc_images = [one_image for one_image in species_images if one_image['loc'] == one_loc['idProperty']]
                abundance = Analysis.abundanceForImageList(species_loc_images, res_species);

                loc_species_images = [one_image for one_image in results['sorted_images_dt'] if \
                                            one_image['loc'] == one_loc['idProperty'] and Analysis.image_has_species(one_image, one_species)]
                period = Analysis.periodForImageList(loc_species_images, interval_minutes)

                result += '{:5.2f} '.format(0 if period == 0 else float(abundance) / float(period))

            result += os.linesep

        result += os.linesep

        return result
