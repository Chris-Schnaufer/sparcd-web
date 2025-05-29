""" Provides the formatting for Dr. Sanderson's results """

import datetime
import os

from text_formatters.activity_pattern_formatter import ActivityPatternFormatter
from text_formatters.act_per_abu_loc_formatter import ActPerAbuLocFormatter
from text_formatters.detection_rate_formatter import DetectionRateFormatter
from text_formatters.first_last_species_formatter import FirstLastSpeciesFormatter
from text_formatters.header_formatter import HeaderFormatter
from text_formatters.location_stat_formatter import LocationStatFormatter
from text_formatters.lunar_activity_formatter import LunarActivityFormatter
from text_formatters.occurance_formatter import OccuranceFormatter
from text_formatters.richness_formatter import RichnessFormatter
from text_formatters.species_loc_coord_formatter import SpeciesLocCoordFormatter
from text_formatters.total_day_formatter import TotalDayFormatter
from text_formatters.trap_days_and_effort_formatter import TrapDaysAndEffortFormatter
from text_formatters.results import Results

def elapsed_time_formatter(start: datetime.datetime, end: datetime.datetime) -> str:
    """ Formats the elapsed time output
    Arguments:
        start: the starting time
        end: the ending time
    Return:
        The formatted elapsed time. Will have an elapsed time of 'ERROR' if a problem
        is found
    """
    # pylint: disable=consider-using-f-string
    return "ELAPSED TIME " + "{:10.3f} ".format((end-start).total_seconds()) + "SECONDS" + \
            os.linesep

def get_dr_sanderson_output(results: Results) -> str:
    """ Converts the results to Dr Sanderson results
    Arguments:
        results: contains the results of the query
    Return:
        Returns the result text
    """
    if not results:
        return "No images found under directory"

    start_time = datetime.datetime.now()
    return  HeaderFormatter.print_locations(results) + \
            HeaderFormatter.print_species(results) + \
            HeaderFormatter.print_image_analysis_header(results) + \
            FirstLastSpeciesFormatter.print_days_in_camera_trap(results) + \
            FirstLastSpeciesFormatter.print_first_pic_of_each_species(results) + \
            FirstLastSpeciesFormatter.print_last_pic_of_each_species(results) + \
            FirstLastSpeciesFormatter.print_species_accumulation_curve(results) + \
            ActPerAbuLocFormatter.print_number_of_pictures_by_year(results) + \
            ActPerAbuLocFormatter.print_number_of_pictures_by_species_by_year(results) + \
            ActPerAbuLocFormatter.print_number_of_pictures_by_percent_total(results) + \
            TrapDaysAndEffortFormatter.print_camera_trap_days(results) + \
            TrapDaysAndEffortFormatter.print_camera_trap_effort(results) + \
            TrapDaysAndEffortFormatter.print_camera_trap_effort_summary(results) + \
            LocationStatFormatter.print_percent_of_species_in_loc(results) + \
            LocationStatFormatter.print_species_by_month_by_loc_by_year(results) + \
            LocationStatFormatter.print_species_by_month_by_loc(results) + \
            LocationStatFormatter.print_distance_between_locations(results) + \
            ActivityPatternFormatter.print_activity_patterns(results) + \
            ActivityPatternFormatter.print_species_pairs_activity_similarity(results) + \
            ActivityPatternFormatter.print_specie_pair_most_similar(results) + \
            ActivityPatternFormatter.print_chi_square_analysis_paired_activity(results) + \
            LunarActivityFormatter.print_lunar_activity(results) + \
            LunarActivityFormatter.print_lunar_activity_most_different(results) + \
            ActivityPatternFormatter.print_activity_patterns_season(results) + \
            ActPerAbuLocFormatter.print_species_abundance(results) + \
            RichnessFormatter.print_location_species_richness(results) + \
            LocationStatFormatter.print_loc_species_frequency_similiarity() + \
            LocationStatFormatter.print_loc_species_composition_similiarity() + \
            SpeciesLocCoordFormatter.print_species_by_loc_with_utm(results) + \
            LocationStatFormatter.print_species_overlap_at_loc(results) + \
            OccuranceFormatter.print_chi_sq_analysis_of_paired_specie_freq() + \
            TotalDayFormatter.print_pictures_by_month_year_loc(results) + \
            TotalDayFormatter.print_pictures_by_month_loc(results) + \
            TotalDayFormatter.print_pictures_by_month_year_species_richness(results) + \
            TotalDayFormatter.print_pictures_by_month_species_richness(results) + \
            TotalDayFormatter.print_pictures_by_month_species_loc_elevation(results) + \
            TotalDayFormatter.print_abundance_by_month_species_loc_elevation(results) + \
            TotalDayFormatter.print_species_by_loc_elevation_and_effort(results) + \
            TotalDayFormatter.print_species_by_loc_elevation_and_effort_table(results) + \
            ActPerAbuLocFormatter.print_species_abundance_year_site(results) + \
            ActPerAbuLocFormatter.print_species_abundance_site(results) + \
            OccuranceFormatter.print_co_occurance_matrix(results) + \
            OccuranceFormatter.print_absense_presence_matrix(results) + \
            OccuranceFormatter.print_max_min_species_elevation(results) + \
            DetectionRateFormatter.print_detection_rate_species_year(results) + \
            DetectionRateFormatter.print_detection_rate_summary(results) + \
            DetectionRateFormatter.print_detection_rate_location_month(results) + \
            DetectionRateFormatter.print_detection_rate_location_month_summary(results) + \
            DetectionRateFormatter.print_detection_rate_trend(results) + \
            OccuranceFormatter.print_native_occupancy(results) + \
            LocationStatFormatter.print_area_covered_by_traps() + \
            elapsed_time_formatter(start_time, datetime.datetime.now())

def get_dr_sanderson_pictures(results: Results) -> str:
    """ Returns the pictures links for Dr Sanderson's pictures
    Arguments:
        results: the query results
    Return:
        A tuple of image infodmation in a dict
    """
    image_data = []
    for one_image in results.get_images():
        if 'species' in one_image and one_image['species']:
            for one_species in one_image['species']:
                image_data.append({'location':results.get_location_name(one_image['loc']),
                                              'species':one_species['name'],
                                              'image':one_image['name']})

    return image_data
