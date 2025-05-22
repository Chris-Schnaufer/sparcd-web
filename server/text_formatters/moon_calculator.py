""" Moon phase calculations """

import dataclasses
import datetime
import math

# pylint: disable=invalid-name

EG = 279.403303
WG = 282.768422
ECCENTRICITY = 0.016713
R0 = 1.495985E8
THETA0 = 0.533128
L0 = 318.351648
P0 = 36.340410
N0 = 318.510107
INCLINATION = 5.145396
MOONECCENTRICITY = 0.054900
a = 384401
MOONTHETA0 = 0.5181
PI0 = 0.9507
JULIANATEPOCH1990 = 2447891.5
JULIANATEPOCH1970 = 2447891.5 - 20 * 365 - 4
SYNODICMONTH = 29.5306 / (2 * math.pi)

@dataclasses.dataclass
class MoonCalculator:
    """ Calculates moon phses
    """
    # pylint: disable=too-many-locals

    phaseLabels =["Julian Date:        ", "Sun's Distance:     ", "Sun's Angular Size: ",
                  "Moon's Phase:       ", "Moon's Percent:     " ]

    JULIANDATE = 0
    SUNDISTANCE = 1
    SUNANGULARSIZE = 2
    MOONPHASE = 3
    MOONPERCENT = 4
    PHASEOPTIONS = 5

    @staticmethod
    def get_phase(jd: float) -> tuple:
        """ Calculates the phases of the moon
        Arguments:
            jd: the Julian Date to check as returned by the getJulian()
        Returns:
        """
        results = [0.0] * MoonCalculator.PHASEOPTIONS
        jd += 50.0 / (60 * 60 * 24)
        results[MoonCalculator.JULIANDATE] = jd
        diff = jd - JULIANATEPOCH1990

        N = 360.0 * diff / 365.242191
        N = MoonCalculator.put_into_range(N)

        Mdot = MoonCalculator.put_into_range(N + EG - WG)
        EC = 360 * ECCENTRICITY * math.sin(MoonCalculator.to_radians(Mdot)) / math.pi
        lambdaDot = MoonCalculator.put_into_range(N + EC + EG)

        nu = Mdot + EC
        f = (1 + ECCENTRICITY * math.cos(MoonCalculator.to_radians(nu))) / \
                                                                (1 - ECCENTRICITY * ECCENTRICITY)
        r = R0 / f
        theta = f * THETA0
        results[MoonCalculator.SUNDISTANCE] = r
        results[MoonCalculator.SUNANGULARSIZE] = MoonCalculator.to_degrees(theta)

        l = MoonCalculator.put_into_range(13.1763966 * diff + L0)
        Mm = MoonCalculator.put_into_range(l - 0.1114041 * diff - P0)

        N = MoonCalculator.put_into_range(N0 - 0.0529539 * diff)
        Enu = 1.2739 * math.sin(MoonCalculator.to_radians(2 * (l - lambdaDot) - Mm))

        Ae = 0.1858 * math.sin(MoonCalculator.to_radians(Mdot))
        A3 = 0.37 * math.sin(MoonCalculator.to_radians(Mdot))

        Mmprime = Mm + Enu - Ae - A3

        Ec = 6.2886 * math.sin(MoonCalculator.to_radians(Mmprime))
        A4 = 0.214 * math.sin(MoonCalculator.to_radians(2 * Mmprime))
        lprime = l + Enu + Ec - Ae + A4

        V = 0.6583 * math.sin(MoonCalculator.to_radians(2 * (lprime - lambdaDot)))
        lpp = lprime + V
        #Nprime = N - 0.16 * math.sin(MoonCalculator.to_radians(Mdot))
        #y = math.sin(MoonCalculator.to_radians(lpp - Nprime)) * \
        #                                      math.cos(MoonCalculator.to_radians(INCLINATION))
        #x = math.cos(MoonCalculator.to_radians(lpp - Nprime))
        #angle = MoonCalculator.to_degrees(math.atan2(y, x))
        #lambdam = MoonCalculator.put_into_range(angle + Nprime)

        DD = lpp - lambdaDot
        results[ MoonCalculator.MOONPHASE] = DD
        F = (1 - math.cos(MoonCalculator.to_radians(DD))) / 2
        results[MoonCalculator.MOONPERCENT] = F
        return results

    @staticmethod
    def get_julian(date: datetime.datetime) -> float:
        """ Returns the julian date from the specied datetime
        Arguments:
            date: the datetime object to return the julian date for
        Result:
            Returns the julian date representing the datetime
        """
        return float(date.strftime('%j'))

    @staticmethod
    def put_into_range(val: float) -> float:
        """ Puts the specified degrees value into range
        Arguments:
            val: the value to put into range
        Return:
            Returns a value between 0.0 and 360.0
        """
        while val < 0:
            val += 360
        while val >= 360:
            val -= 360
        return val

    @staticmethod
    def to_millis_from_julian(jd: float) -> int:
        """ Returns the milliseconds that represents the julian date
        Arguments:
            jd: the julian date
        Return:
            The julian date converted to milliseconds
        """
        dj = jd - JULIANATEPOCH1970
        return math.trunc(dj * (24 * 60 * 60 * 1000))

    @staticmethod
    def get_lunation(julian: float, phase: float, lunation: float) -> float:
        """ Returns the lunation value for the julian date based upon the
            phase and lunation
        Arguments:
            julian: the julian date value returned from getJulian()
            phase:
            lunation:
        Returns:
            Returns the luncation value
        """
        phase = MoonCalculator.to_radians(phase)
        lunation = MoonCalculator.to_radians(lunation)
        dx = math.cos(phase) - math.cos(lunation)
        dy = math.sin(phase) - math.sin(lunation)
        if dx * dx + dy * dy < 1e-14:
            return julian

        # Added this
        dl = 0.0
        if lunation == 0:
            dl = -math.fabs(phase - lunation)
        else:
            dl = phase - lunation
        # Added this (used to just be "double dl = phase - lunation")

        newjulian = julian - dl * SYNODICMONTH
        newphase = MoonCalculator.get_phase(newjulian)

        return MoonCalculator.get_lunation(newjulian, newphase[ MoonCalculator.MOONPHASE], \
                                                                MoonCalculator.to_degrees(lunation))

    #@staticmethod
    #def getJulian(GregorianCalendar cal)
    #{
    #    int year = cal.get(Calendar.YEAR)
    #    //System.out.println("Year " + year)
    #    int month = cal.get(Calendar.MONTH) + 1
    #    //System.out.println("Month " + month)
    #    double day = (double) cal.get(Calendar.SECOND)
    #    //System.out.println("Second " + day)
    #    double minute = (double) cal.get(Calendar.MINUTE)
    #    //System.out.println("Minute " + minute)
    #    day = day / 60 + minute
    #    double hour = (double) (cal.get(Calendar.HOUR_OF_DAY) - (cal.get(Calendar.ZONE_OFFSET) \
    #                                           + cal.get(Calendar.DST_OFFSET)) / (1000 * 60 * 60))
    #    //System.out.println("Hour " + hour)
    #    day = day / 60 + hour
    #    double dofmonth = (double) cal.get(Calendar.DAY_OF_MONTH)
    #    //System.out.println("Day " + dofmonth)
    #    day = day / 24 + dofmonth
    #    if (month < 3)
    #    {
    #        month += 12
    #        year -= 1
    #    }
    #    double A = integerPart(year / 100)
    #    double B = 2 - A + integerPart(A / 4)
    #    if (cal.before(cal.getGregorianChange()))
    #        B = 0
    #    double C
    #    if (year < 0)
    #        C = integerPart(365.25 * year - 0.75)
    #    else
    #        C = integerPart(365.25 * year)
    #    double D = integerPart(30.6001 * (month + 1))
#
    #    return B + C + D + day + 1720994.5
    #}
#
    #@staticmethod
    #def fromJulian(jd: float) -> tuple:
    #    jd += 0.5
    #    i = int(math.floor(jd))
    #    F = jd - float(i)
    #    B = 0
    #    if i > 2299160:
    #        A = int(math.floor((i - 1867216.5) / 36524.25))
    #        B = i + 1 + A - int(math.floor(A / 4))
    #    else:
    #        B = i
    #    C = B + 1524
    #    D = int(math.floor((C - 122.1) / 365.25))
    #    E = int(math.floor(365.25 * D))
    #    G = int(math.floor((C - E) / 30.6001))
    #    d = C - E + F - math.floor(30.6001 * G)
    #    m = 0
    #    if G < 13.5:
    #        m = G - 1
    #    else:
    #        m = G - 13
    #    y = 0
    #    if m > 2.5:
    #        y = D - 4716
    #    else:
    #        y = D - 4715
#
    #    day = int(math.floor(d))
    #    hours = (d - day) * 24
    #    hr = int(math.floor(hours))
    #    mins = (hours - hr) * 60
    #    min = int(math.floor(mins))
    #    secs = int(math.floor((mins - min) * 60))
#
    #    return new int[2]
#
    #@staticmethod
    #def integerPart(d: float) -> float:
    #    if d >= 0:
    #        return math.floor(d)
    #    return -Math.floor(-d)

    @staticmethod
    def to_radians(deg: float) -> float:
        """Converts degrees to radians """
        return deg * math.pi / 180

    @staticmethod
    def to_degrees(rad: float) -> float:
        """Converts radians to degrees """
        return rad * 180 / math.pi
