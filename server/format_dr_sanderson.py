""" Provides the formatting for Dr. Sanderson's results """

import datetime
import os

def elapsed_time_formatter(start: datetime.datetime, end: datetime.datetime) -> str:
    """ Formats the elapsed time output
    Arguments:
        start: the starting time
        end: the ending time
    Return:
        The formatted elapsed time. Will have an elapsed time of 'ERROR' if a problem
        is found
    """
    return "ELAPSED TIME " + "%10.3f ".format((end-start).total_seconds()) + "SECONDS" +
            os.linesep

def get_dr_sanderson_output(results: tuple, all_locations:tuple, all_species:tuple) -> str:
    """ Converts the results to Dr Sanderson results
    Arguments:
        results: the results to search through
        all_locations: all available locations
        all_species: all available species
    Return:
        Returns the result text
    """
    if not results:
        return "No images found under directory"

    cur_locations = {}
    have_unknown = False
    for one_result in results:
        test_value = one_result[0]['loc']
        if not test_value in cur_locations:
            found_items = [one_loc for all_locations if one_loc['idProperty'] == test_value]
            if found_items and len(found_items) > 0:
                cur_locations[test_value] = found_items[0]
            else:
                have_unknown = True
    if have_unknown:
        cur_locations['unknown'] = True

    cur_species = {}
    have_unknown = False
    for one_result in results:
        for one_image in one_result[1]:
            test_value = one_image['species']['sci_name']
            if not test_value in cur_species:
                found_items = [one_species for all_species if one_species['scientificName'] == test_value]
                if found_items and len(found_items) > 0:
                    cur_species[test_value] = found_items[0]
                else:
                    have_unknown = True
    if have_unknown:
        cur_species['unknown'] = True

    start_time = datetime.datetime.now()
    return  HeaderFormatter.printLocations(results, cur_locations) +
            HeaderFormatter.printSpecies(results, cur_species) +
            HeaderFormatter.printImageAnalysisHeader(results, cur_locations, all_species) +
            FirstLastSpeciesFormatter.printDaysInCameraTrap(results, cur_locations, all_species) +
            FirstLastSpeciesFormatter.printFirstPicOfEachSpecies(results, all_locations, all_species) +
            FirstLastSpeciesFormatter.printLastPicOfEachSpecies(results, all_locations, all_species) +
            FirstLastSpeciesFormatter.printSpeciesAccumulationCurve(results, all_locations, all_species) +
            ActPerAbuLocFormatter.printNumberOfPicturesByYear(results, all_locations, all_species) +
            ActPerAbuLocFormatter.printNumberOfPicturesBySpeciesByYear(results, all_locations, all_species) +
            ActPerAbuLocFormatter.printNumberOfPicturesByPercentTotal(results, all_locations, all_species) +
            TrapDaysAndEffortFormatter.printCameraTrapDays(results, all_locations, all_species) +
            TrapDaysAndEffortFormatter.printCameraTrapEffort(results, all_locations, all_species) +
            TrapDaysAndEffortFormatter.printCameraTrapEffortSummary(results, all_locations, all_species) +
            LocationStatFormatter.printPercentOfSpeciesInLoc(results, all_locations, all_species) +
            LocationStatFormatter.printSpeciesByMonthByLocByYear(results, all_locations, all_species) +
            LocationStatFormatter.printSpeciesByMonthByLoc(results, all_locations, all_species) +
            LocationStatFormatter.printDistanceBetweenLocations(results, all_locations, all_species) +
            ActivityPatternFormatter.printActivityPatterns(results, all_locations, all_species) +
            ActivityPatternFormatter.printSpeciesPairsActivitySimilarity(results, all_locations, all_species) +
            ActivityPatternFormatter.printSpeciePairMostSimilar(results, all_locations, all_species) +
            ActivityPatternFormatter.printChiSquareAnalysisPairedActivity(results, all_locations, all_species) +
            LunarActivityFormatter.printLunarActivity(results, all_locations, all_species) +
            LunarActivityFormatter.printLunarActivityMostDifferent(results, all_locations, all_species) +
            ActivityPatternFormatter.printActivityPatternsSeason(results, all_locations, all_species) +
            ActPerAbuLocFormatter.printSpeciesAbundance(results, all_locations, all_species) +
            RichnessFormatter.printLocationSpeciesRichness(results, all_locations, all_species) +
            LocationStatFormatter.printLocSpeciesFrequencySimiliarity(results, all_locations, all_species) +
            LocationStatFormatter.printLocSpeciesCompositionSimiliarity(results, all_locations, all_species) +
            SpeciesLocCoordFormatter.printSpeciesByLocWithUTM(results, all_locations, all_species) +
            LocationStatFormatter.printSpeciesOverlapAtLoc(results, all_locations, all_species) +
            OccuranceFormatter.printCHISqAnalysisOfPairedSpecieFreq(results, all_locations, all_species) +
            TotalDayFormatter.printPicturesByMonthYearLoc(results, all_locations, all_species) +
            TotalDayFormatter.printPicturesByMonthLoc(results, all_locations, all_species) +
            TotalDayFormatter.printPicturesByMonthYearSpeciesRichness(results, all_locations, all_species) +
            TotalDayFormatter.printPicturesByMonthSpeciesRichness(results, all_locations, all_species) +
            TotalDayFormatter.printPicturesByMonthSpeciesLocElevation(results, all_locations, all_species) +
            TotalDayFormatter.printAbundanceByMonthSpeciesLocElevation(results, all_locations, all_species) +
            TotalDayFormatter.printSpeciesByLocElevationAndEffort(results, all_locations, all_species) +
            TotalDayFormatter.printSpeciesByLocElevationAndEffortTable(results, all_locations, all_species) +
            ActPerAbuLocFormatter.printSpeciesAbundanceYearSite(results, all_locations, all_species) +
            ActPerAbuLocFormatter.printSpeciesAbundanceSite(results, all_locations, all_species) +
            OccuranceFormatter.printCoOccuranceMatrix(results, all_locations, all_species) +
            OccuranceFormatter.printAbsensePresenceMatrix(results, all_locations, all_species) +
            OccuranceFormatter.printMaxMinSpeciesElevation(results, all_locations, all_species) +
            DetectionRateFormatter.printDetectionRateSpeciesYear(results, all_locations, all_species) +
            DetectionRateFormatter.printDetectionRateSummary(results, all_locations, all_species) +
            DetectionRateFormatter.printDetectionRateLocationMonth(results, all_locations, all_species) +
            DetectionRateFormatter.printDetectionRateLocationMonthSummary(results, all_locations, all_species) +
            DetectionRateFormatter.printDetectionRateTrend(results, all_locations, all_species) +
            OccuranceFormatter.printNativeOccupancy(results, all_locations, all_species) +
            LocationStatFormatter.printAreaCoveredByTraps(results, all_locations, all_species) +
            elapsed_time_formatter(start_time, datetime.datetime.now())
