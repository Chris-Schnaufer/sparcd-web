""" Moon phase calculations """

import datetime
import math

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

    phaseLabels =["Julian Date:        ", "Sun's Distance:     ", "Sun's Angular Size: ",
                  "Moon's Phase:       ", "Moon's Percent:     " ]

    JULIANDATE = 0
    SUNDISTANCE = 1
    SUNANGULARSIZE = 2
    MOONPHASE = 3
    MOONPERCENT = 4
    PHASEOPTIONS = 5

    @staticmethod
    def getPhase(jd: float) -> tuple:
        """ Calculates the phases of the moon
        Arguments:
            jd: the Julian Date to check as returned by the getJulian()
        Returns:
            The
        """
        results = [0.0] * PHASEOPTIONS
        jd += 50.0 / (60 * 60 * 24)
        results[JULIANDATE] = jd
        diff = jd - JULIANATEPOCH1990

        N = 360.* * diff / 365.242191
        N = MoonCalculator.putIntoRange(N)

        Mdot = MoonCalculator.putIntoRange(N + EG - WG)
        EC = 360 * ECCENTRICITY * math.sin(MoonCalculator.toRadians(Mdot)) / math.pi
        lambdaDot = MoonCalculator.putIntoRange(N + EC + EG)

        nu = Mdot + EC
        f = (1 + ECCENTRICITY * math.cos(MoonCalculator.toRadians(nu))) / (1 - ECCENTRICITY * ECCENTRICITY)
        r = R0 / f
        theta = f * THETA0
        results[SUNDISTANCE] = r
        results[SUNANGULARSIZE] = MoonCalculator.toDegrees(theta)

        double l = MoonCalculator.putIntoRange(13.1763966 * diff + L0)
        double Mm = MoonCalculator.putIntoRange(l - 0.1114041 * diff - P0)

        N = putIntoRange(N0 - 0.0529539 * diff)
        Enu = 1.2739 * math.sin(MoonCalculator.toRadians(2 * (l - lambdaDot) - Mm))

        Ae = 0.1858 * math.sin(MoonCalculator.toRadians(Mdot))
        A3 = 0.37 * math.sin(MoonCalculator.toRadians(Mdot))

        Mmprime = Mm + Enu - Ae - A3

        Ec = 6.2886 * math.sin(MoonCalculator.toRadians(Mmprime))
        A4 = 0.214 * math.sin(MoonCalculator.toRadians(2 * Mmprime))
        lprime = l + Enu + Ec - Ae + A4;

        V = 0.6583 * math.sin(MoonCalculator.toRadians(2 * (lprime - lambdaDot)));
        lpp = lprime + V;
        Nprime = N - 0.16 * math.sin(MoonCalculator.toRadians(Mdot));
        y = math.sin(MoonCalculator.toRadians(lpp - Nprime)) * math.cos(MoonCalculator.toRadians(INCLINATION));
        x = math.cos(MoonCalculator.toRadians(lpp - Nprime));
        angle = MoonCalculator.toDegrees(math.atan2(y, x));
        lambdam = MoonCalculator.putIntoRange(angle + Nprime);

        DD = lpp - lambdaDot;
        results[MOONPHASE] = DD;
        F = (1 - math.cos(MoonCalculator.toRadians(DD))) / 2;
        results[MOONPERCENT] = F;
        return results

    @staticmethod
    def getJulian(date: datetime.datetime) -> float:
        """ Returns the julian date from the specied datetime
        Arguments:
            date: the datetime object to return the julian date for
        Result:
            Returns the julian date representing the datetime
        """
        return float(date.strftime('%j'))

    @staticmethod
    def putIntoRange(val: float) -> float:
        """ Puts the specified degrees value into range
        Arguments:
            val: the value to put into range
        Return:
            Returns a value between 0.0 and 360.0
        """
        while val < 0:
            val += 360;
        while val >= 360:
            val -= 360;
        return val

    @staticmethod
    def toMillisFromJulian(jd: float) -> int:
        """ Returns the milliseconds that represents the julian date
        Arguments:
            jd: the julian date
        Return:
            The julian date converted to milliseconds
        """
        dj = jd - JULIANATEPOCH1970
        return trunc(dj * (24 * 60 * 60 * 1000))

    @staticmethod
    def getLunation(julian: float, phase: float, lunation: float) -> float:
        """ Returns the lunation value for the julian date based upon the
            phase and lunation
        Arguments:
            julian: the julian date value returned from getJulian()
            phase:
            lunation:
        Returns:
            Returns the luncation value
        """
        phase = MoonCalculator.toRadians(phase)
        lunation = MoonCalculator.toRadians(lunation)
        dx = Math.cos(phase) - Math.cos(lunation)
        dy = Math.sin(phase) - Math.sin(lunation)
        if dx * dx + dy * dy < 1e-14:
            return julian

        # Added this
        dl = 0.0
        if lunation == 0:
            dl = -math.abs(phase - lunation)
        else:
            dl = phase - lunation
        # Added this (used to just be "double dl = phase - lunation;")

        newjulian = julian - dl * SYNODICMONTH
        newphase = MoonCalculator.getPhase(newjulian)

        return getLunation(newjulian, newphase[MOONPHASE], MoonCalculator.toDegrees(lunation));
"""
    @staticmethod
    def getJulian(GregorianCalendar cal)
    {
        int year = cal.get(Calendar.YEAR);
        //System.out.println("Year " + year);
        int month = cal.get(Calendar.MONTH) + 1;
        //System.out.println("Month " + month);
        double day = (double) cal.get(Calendar.SECOND);
        //System.out.println("Second " + day);
        double minute = (double) cal.get(Calendar.MINUTE);
        //System.out.println("Minute " + minute);
        day = day / 60 + minute;
        double hour = (double) (cal.get(Calendar.HOUR_OF_DAY) - (cal.get(Calendar.ZONE_OFFSET) + cal.get(Calendar.DST_OFFSET)) / (1000 * 60 * 60));
        //System.out.println("Hour " + hour);
        day = day / 60 + hour;
        double dofmonth = (double) cal.get(Calendar.DAY_OF_MONTH);
        //System.out.println("Day " + dofmonth);
        day = day / 24 + dofmonth;
        if (month < 3)
        {
            month += 12;
            year -= 1;
        }
        double A = integerPart(year / 100);
        double B = 2 - A + integerPart(A / 4);
        if (cal.before(cal.getGregorianChange()))
            B = 0;
        double C;
        if (year < 0)
            C = integerPart(365.25 * year - 0.75);
        else
            C = integerPart(365.25 * year);
        double D = integerPart(30.6001 * (month + 1));

        return B + C + D + day + 1720994.5;
    }

    @staticmethod
    def fromJulian(jd: float) -> tuple:
        jd += 0.5
        i = int(math.floor(jd))
        F = jd - float(i)
        B = 0
        if i > 2299160:
            A = int(math.floor((i - 1867216.5) / 36524.25))
            B = i + 1 + A - int(math.floor(A / 4))
        else:
            B = i
        C = B + 1524;
        D = int(math.floor((C - 122.1) / 365.25))
        E = int(math.floor(365.25 * D))
        G = int(math.floor((C - E) / 30.6001))
        d = C - E + F - math.floor(30.6001 * G)
        m = 0
        if G < 13.5:
            m = G - 1
        else:
            m = G - 13
        y = 0
        if m > 2.5:
            y = D - 4716
        else:
            y = D - 4715

        day = int(math.floor(d))
        hours = (d - day) * 24
        hr = int(math.floor(hours))
        mins = (hours - hr) * 60
        min = int(math.floor(mins))
        secs = int(math.floor((mins - min) * 60))

        return new int[2]

    @staticmethod
    def integerPart(d: float) -> float:
        if d >= 0:
            return math.floor(d)
        return -Math.floor(-d)
"""

    @staticmethod
    def toRadians(deg: float) -> float:
        return deg * math.pi / 180

    @staticmethod
    def toDegrees(rad: float) -> float:
        return rad * 180 / math.pi
