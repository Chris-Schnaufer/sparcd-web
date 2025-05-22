""" Provides the formatting for Dr. Sanderson's results """

import datetime
import os

from header_formatter import HeaderFormatter
from results import Results

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
    return  HeaderFormatter.printLocations(results) +
            HeaderFormatter.printSpecies(results) +
            HeaderFormatter.printImageAnalysisHeader(results) +
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
