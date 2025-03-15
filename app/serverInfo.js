'use client'

/** @module serverInfo */

import { createContext } from 'react';

/** React context for base URL */
export const BaseURLContext = createContext(null);
/** React context for Collections information */
export const CollectionsInfoContext = createContext(null);
/** React context for locations information */
export const LocationsInfoContext = createContext([
  {
    "nameProperty": "Apache Pass - Fort Bowie",
    "idProperty": "DOS09",
    "latProperty": 32.158,
    "lngProperty": -109.4478,
    "elevationProperty": 1415.0
  },
  {
    "nameProperty": "Shake Spring - CNM",
    "idProperty": "CHI98",
    "latProperty": 32.0217,
    "lngProperty": -109.3391,
    "elevationProperty": 1753.0
  },
  {
    "nameProperty": "Simpson Spring ",
    "idProperty": "WHE11",
    "latProperty": 31.784,
    "lngProperty": -110.4642,
    "elevationProperty": 1637.0
  },
  {
    "nameProperty": "Walker Basin",
    "idProperty": "SAN11",
    "latProperty": 31.635,
    "lngProperty": -110.7891,
    "elevationProperty": 1585.0
  },
  {
    "nameProperty": "Devils Canyon",
    "idProperty": "CHI28",
    "latProperty": 31.749,
    "lngProperty": -109.3788,
    "elevationProperty": 1724.0
  },
  {
    "nameProperty": "Sweetwater Reservoir",
    "idProperty": "SAN73",
    "latProperty": 31.7142,
    "lngProperty": -110.7975,
    "elevationProperty": 1733.0
  },
  {
    "nameProperty": "Bathtub Water b",
    "idProperty": "SAN25b",
    "latProperty": 31.6663,
    "lngProperty": -110.7817,
    "elevationProperty": 1482.0
  },
  {
    "nameProperty": "Walker II",
    "idProperty": "SAN24",
    "latProperty": 31.6646,
    "lngProperty": -110.8037,
    "elevationProperty": 1625.0
  },
  {
    "nameProperty": "Prospect Dam 2",
    "idProperty": "SAN70",
    "latProperty": 31.6612,
    "lngProperty": -110.8,
    "elevationProperty": 1621.0
  },
  {
    "nameProperty": "Fire Canyon",
    "idProperty": "CHI47",
    "latProperty": 31.8072,
    "lngProperty": -109.3601,
    "elevationProperty": 1985.0
  },
  {
    "nameProperty": "Walker Big Casa Confluence",
    "idProperty": "SAN74",
    "latProperty": 31.6632,
    "lngProperty": -110.7808,
    "elevationProperty": 1585.0
  },
  {
    "nameProperty": "Bathtub Water",
    "idProperty": "SAN25",
    "latProperty": 31.6663,
    "lngProperty": -110.7817,
    "elevationProperty": 1470.0
  },
  {
    "nameProperty": "French Joe",
    "idProperty": "WHE04",
    "latProperty": 31.8291,
    "lngProperty": -110.3991,
    "elevationProperty": 1604.0
  },
  {
    "nameProperty": "Dos Cabezas 3/BLM DC03",
    "idProperty": "DOS06",
    "latProperty": 32.2245,
    "lngProperty": -109.5044,
    "elevationProperty": 1576.0
  },
  {
    "nameProperty": "DO NOT USE _ WILL BE DELETED AFTER DATA CLEANUP - BAD SITEIDTotal Wreck Mine_K2",
    "idProperty": "10b",
    "latProperty": 31.8992,
    "lngProperty": -110.587,
    "elevationProperty": 0.0
  },
  {
    "nameProperty": "Green Canyon",
    "idProperty": "CHI38",
    "latProperty": 31.9563,
    "lngProperty": -109.3554,
    "elevationProperty": 1741.0
  },
  {
    "nameProperty": "Barrel Spring II",
    "idProperty": "CHI50",
    "latProperty": 32.0162,
    "lngProperty": -109.3026,
    "elevationProperty": 1760.0
  },
  {
    "nameProperty": "Culvert",
    "idProperty": "SAN17",
    "latProperty": 31.7988,
    "lngProperty": -110.775,
    "elevationProperty": 1466.0
  },
  {
    "nameProperty": "Mascot Mine 2",
    "idProperty": "DOS16",
    "latProperty": 32.2185,
    "lngProperty": -109.5914,
    "elevationProperty": 2158.0
  },
  {
    "nameProperty": "Bear Springs -Whetstone",
    "idProperty": "WHE08",
    "latProperty": 31.7755,
    "lngProperty": -110.4617,
    "elevationProperty": 1705.0
  },
  {
    "nameProperty": "North Bruno Creek",
    "idProperty": "CHI42N",
    "latProperty": 31.7102,
    "lngProperty": -109.3898,
    "elevationProperty": 1733.0
  },
  {
    "nameProperty": "Indian Creek ",
    "idProperty": "CHI48",
    "latProperty": 32.0171,
    "lngProperty": -109.2905,
    "elevationProperty": 1718.0
  },
  {
    "nameProperty": "Whitetail III",
    "idProperty": "CHI49",
    "latProperty": 32.0164,
    "lngProperty": -109.2986,
    "elevationProperty": 1718.0
  },
  {
    "nameProperty": "Slavin Gulch Tributary 1",
    "idProperty": "DRA07",
    "latProperty": 31.888,
    "lngProperty": -110.0182,
    "elevationProperty": 1510.0
  },
  {
    "nameProperty": "Dos Cabezas 1 ",
    "idProperty": "DOS02",
    "latProperty": 32.1753,
    "lngProperty": -109.4996,
    "elevationProperty": 1684.0
  },
  {
    "nameProperty": "Sycamore Grove",
    "idProperty": "SAN15",
    "latProperty": 31.8054,
    "lngProperty": -110.7675,
    "elevationProperty": 1540.0
  },
  {
    "nameProperty": "Box 1",
    "idProperty": "SAN01",
    "latProperty": 31.7988,
    "lngProperty": -110.7802,
    "elevationProperty": 1440.0
  },
  {
    "nameProperty": "Cottonwood Canyon Road  -  CHI",
    "idProperty": "CHI63",
    "latProperty": 31.7346,
    "lngProperty": -109.3411,
    "elevationProperty": 1763.0
  },
  {
    "nameProperty": "Pole Bridge",
    "idProperty": "CHI51",
    "latProperty": 31.857,
    "lngProperty": -109.338,
    "elevationProperty": 1923.0
  },
  {
    "nameProperty": "Kyle\u0027s Pick",
    "idProperty": "EMP05",
    "latProperty": 31.8909,
    "lngProperty": -110.6209,
    "elevationProperty": 1508.0
  },
  {
    "nameProperty": "Prospect Dam",
    "idProperty": "SAN32",
    "latProperty": 31.635,
    "lngProperty": -110.7891,
    "elevationProperty": 1650.0
  },
  {
    "nameProperty": "Walker II",
    "idProperty": "SAN24",
    "latProperty": 31.635,
    "lngProperty": -110.7891,
    "elevationProperty": 1625.0
  },
  {
    "nameProperty": "Chiminea",
    "idProperty": "EMP07",
    "latProperty": 31.9037,
    "lngProperty": -110.6025,
    "elevationProperty": 0.0
  },
  {
    "nameProperty": "John Long Road",
    "idProperty": "CHI56",
    "latProperty": 31.8047,
    "lngProperty": -109.3594,
    "elevationProperty": 1944.0
  },
  {
    "nameProperty": "D\u0026H Canyon II",
    "idProperty": "SAN30",
    "latProperty": 31.635,
    "lngProperty": -110.7891,
    "elevationProperty": 1495.0
  },
  {
    "nameProperty": "Basin Spring ",
    "idProperty": "SAN16",
    "latProperty": 31.8045,
    "lngProperty": -110.7822,
    "elevationProperty": 1526.0
  },
  {
    "nameProperty": "Canyon Bottom",
    "idProperty": "EMP06",
    "latProperty": 31.8956,
    "lngProperty": -110.6136,
    "elevationProperty": 0.0
  },
  {
    "nameProperty": "EMPIRE",
    "idProperty": "EMP06",
    "latProperty": 31.8937,
    "lngProperty": -110.6136,
    "elevationProperty": 0.0
  },
  {
    "nameProperty": "Cienega Narrows",
    "idProperty": "EMP02",
    "latProperty": 31.8862,
    "lngProperty": -110.5494,
    "elevationProperty": 1230.0
  },
  {
    "nameProperty": "Turkey Confluence",
    "idProperty": "CHI62",
    "latProperty": 31.8581,
    "lngProperty": -109.3314,
    "elevationProperty": 1947.0
  },
  {
    "nameProperty": "John Long",
    "idProperty": "CHI27",
    "latProperty": 31.7907,
    "lngProperty": -109.3644,
    "elevationProperty": 1913.0
  },
  {
    "nameProperty": "Total Wreck Mine",
    "idProperty": "EMP10b",
    "latProperty": 31.8992,
    "lngProperty": -110.587,
    "elevationProperty": 1372.0
  },
  {
    "nameProperty": "Copper Canyon",
    "idProperty": "SAN39",
    "latProperty": 31.6351,
    "lngProperty": -110.8945,
    "elevationProperty": 1700.0
  },
  {
    "nameProperty": "Whitetail III",
    "idProperty": "CHI49",
    "latProperty": 32.0163,
    "lngProperty": -109.2987,
    "elevationProperty": 1683.0
  },
  {
    "nameProperty": "Monte Vista Trail",
    "idProperty": "CHI33",
    "latProperty": 31.801,
    "lngProperty": -109.3197,
    "elevationProperty": 2024.0
  },
  {
    "nameProperty": "Cienega",
    "idProperty": "EMP01",
    "latProperty": 31.8035,
    "lngProperty": -110.5885,
    "elevationProperty": 0.0
  },
  {
    "nameProperty": "Empire Gultch",
    "idProperty": "EMP11",
    "latProperty": 31.7877,
    "lngProperty": -110.6572,
    "elevationProperty": 0.0
  },
  {
    "nameProperty": "Lion Track",
    "idProperty": "EMP12",
    "latProperty": 31.8034,
    "lngProperty": -110.6888,
    "elevationProperty": 4987.0
  },
  {
    "nameProperty": "Sycamore Cub Trail ",
    "idProperty": "CHI40",
    "latProperty": 31.7944,
    "lngProperty": -109.3603,
    "elevationProperty": 1942.0
  },
  {
    "nameProperty": "Iron Spring",
    "idProperty": "CHI45",
    "latProperty": 31.957,
    "lngProperty": -109.2832,
    "elevationProperty": 1808.0
  },
  {
    "nameProperty": "Price Canyon",
    "idProperty": "CHI58",
    "latProperty": 31.7647,
    "lngProperty": -109.2629,
    "elevationProperty": 1817.0
  },
  {
    "nameProperty": "Rattlesnake Trail",
    "idProperty": "CHI53",
    "latProperty": 31.9164,
    "lngProperty": -109.3156,
    "elevationProperty": 2006.0
  },
  {
    "nameProperty": "Morse Canyon",
    "idProperty": "CHI61",
    "latProperty": 31.8448,
    "lngProperty": -109.3263,
    "elevationProperty": 2106.0
  },
  {
    "nameProperty": "Cienega Creek",
    "idProperty": "EMP01",
    "latProperty": 31.8125,
    "lngProperty": -110.5913,
    "elevationProperty": 1329.0
  },
  {
    "nameProperty": "Guidanai Canyon",
    "idProperty": "WHE03",
    "latProperty": 31.8419,
    "lngProperty": -110.3713,
    "elevationProperty": 1512.0
  },
  {
    "nameProperty": "Ridgetop",
    "idProperty": "EMP04",
    "latProperty": 31.89,
    "lngProperty": -110.6109,
    "elevationProperty": 0.0
  },
  {
    "nameProperty": "Walker II",
    "idProperty": "SAN24",
    "latProperty": 31.6645,
    "lngProperty": -110.8047,
    "elevationProperty": 1625.0
  },
  {
    "nameProperty": "McGrew Spring",
    "idProperty": "WHE13",
    "latProperty": 31.8511,
    "lngProperty": -110.3571,
    "elevationProperty": 1464.0
  },
  {
    "nameProperty": "Davidson Canyon",
    "idProperty": "EMP09",
    "latProperty": 31.9755,
    "lngProperty": -110.6495,
    "elevationProperty": 0.0
  },
  {
    "nameProperty": "Lakeside",
    "idProperty": "DOS17",
    "latProperty": 32.1556,
    "lngProperty": -109.4714,
    "elevationProperty": 1504.0
  },
  {
    "nameProperty": "Little Wood Spring",
    "idProperty": "CHI57",
    "latProperty": 32.1313,
    "lngProperty": -109.3307,
    "elevationProperty": 1657.0
  },
  {
    "nameProperty": "Davidson_2",
    "idProperty": "EMP09",
    "latProperty": 31.9704,
    "lngProperty": -110.6481,
    "elevationProperty": 0.0
  },
  {
    "nameProperty": "Empire Gulch",
    "idProperty": "EMP11",
    "latProperty": 31.787,
    "lngProperty": -110.6501,
    "elevationProperty": 1406.0
  },
  {
    "nameProperty": "Lion Track",
    "idProperty": "EMP12",
    "latProperty": 31.8032,
    "lngProperty": -110.6888,
    "elevationProperty": 1520.0
  },
  {
    "nameProperty": "Saddle",
    "idProperty": "EMP08",
    "latProperty": 31.9143,
    "lngProperty": -110.6223,
    "elevationProperty": 0.0
  },
  {
    "nameProperty": "Mansfield-3",
    "idProperty": "SAN19",
    "latProperty": 31.6238,
    "lngProperty": -110.8435,
    "elevationProperty": 1770.0
  },
  {
    "nameProperty": "Rock Creek - Fife Canyon",
    "idProperty": "CHI34",
    "latProperty": 31.8963,
    "lngProperty": -109.3639,
    "elevationProperty": 1806.0
  },
  {
    "nameProperty": "Sycamore Canyon",
    "idProperty": "CHI43",
    "latProperty": 31.7485,
    "lngProperty": -109.3448,
    "elevationProperty": 1871.0
  },
  {
    "nameProperty": "Mel\u0027s Pick davidson",
    "idProperty": "EMP13",
    "latProperty": 32.0164,
    "lngProperty": -110.6427,
    "elevationProperty": 1036.0
  },
  {
    "nameProperty": "Temporal Gultch II",
    "idProperty": "SAN29",
    "latProperty": 31.6564,
    "lngProperty": -110.8317,
    "elevationProperty": 0.0
  },
  {
    "nameProperty": "Sunnyside Canyon",
    "idProperty": "HUA11",
    "latProperty": 31.43,
    "lngProperty": -110.3712,
    "elevationProperty": 2020.0
  },
  {
    "nameProperty": "Peterson Peak",
    "idProperty": "HUA25",
    "latProperty": 31.4776,
    "lngProperty": -110.3934,
    "elevationProperty": 1974.0
  },
  {
    "nameProperty": "Sanders Peak",
    "idProperty": "CHI03",
    "latProperty": 31.876,
    "lngProperty": -109.2276,
    "elevationProperty": 1721.0
  },
  {
    "nameProperty": "South Fork Trail ",
    "idProperty": "CHI73",
    "latProperty": 31.8706,
    "lngProperty": -109.1871,
    "elevationProperty": 1621.0
  },
  {
    "nameProperty": "North Bonita Canyon II - CNM",
    "idProperty": "CHI78",
    "latProperty": 32.0234,
    "lngProperty": -109.3478,
    "elevationProperty": 1685.0
  },
  {
    "nameProperty": "West Whitetail Canyon - CNM",
    "idProperty": "CHI79",
    "latProperty": 32.0549,
    "lngProperty": -109.3571,
    "elevationProperty": 1753.0
  },
  {
    "nameProperty": "Little Picket - CNM",
    "idProperty": "CHI81",
    "latProperty": 32.0178,
    "lngProperty": -109.3849,
    "elevationProperty": 1596.0
  },
  {
    "nameProperty": "Newton Canyon - CNM",
    "idProperty": "CHI83",
    "latProperty": 31.998,
    "lngProperty": -109.3681,
    "elevationProperty": 1677.0
  },
  {
    "nameProperty": "Lower Rhyolite Trail - CNM",
    "idProperty": "CHI84",
    "latProperty": 32.0015,
    "lngProperty": -109.3339,
    "elevationProperty": 1778.0
  },
  {
    "nameProperty": "Sarah Deming - CNM",
    "idProperty": "CHI85",
    "latProperty": 32.002,
    "lngProperty": -109.3302,
    "elevationProperty": 1792.0
  },
  {
    "nameProperty": "Inspiration Point - CNM",
    "idProperty": "CHI86",
    "latProperty": 32.0027,
    "lngProperty": -109.3143,
    "elevationProperty": 1961.0
  },
  {
    "nameProperty": "Picket Park - CNM ",
    "idProperty": "CHI89",
    "latProperty": 32.0256,
    "lngProperty": -109.3627,
    "elevationProperty": 1720.0
  },
  {
    "nameProperty": "Copper Canyon-2 ",
    "idProperty": "HUA23",
    "latProperty": 31.3684,
    "lngProperty": -110.295,
    "elevationProperty": 2010.0
  },
  {
    "nameProperty": "Greenhouse Crest",
    "idProperty": "CHI20",
    "latProperty": 31.8614,
    "lngProperty": -109.2874,
    "elevationProperty": 2827.0
  },
  {
    "nameProperty": "Dos Cabezas - BLM DC01",
    "idProperty": "DOS04",
    "latProperty": 32.1997,
    "lngProperty": -109.5214,
    "elevationProperty": 1810.0
  },
  {
    "nameProperty": "Government Peak",
    "idProperty": "DOS18",
    "latProperty": 32.2184,
    "lngProperty": -109.5092,
    "elevationProperty": 1724.0
  },
  {
    "nameProperty": "Booger Spring",
    "idProperty": "CHI69",
    "latProperty": 31.8667,
    "lngProperty": -109.282,
    "elevationProperty": 2815.0
  },
  {
    "nameProperty": "Onion Creek ",
    "idProperty": "CHI71",
    "latProperty": 31.9311,
    "lngProperty": -109.2586,
    "elevationProperty": 2266.0
  },
  {
    "nameProperty": "Miller",
    "idProperty": "HUA27",
    "latProperty": 31.3801,
    "lngProperty": -110.2911,
    "elevationProperty": 2566.0
  },
  {
    "nameProperty": "Turkey Pen Tinaja",
    "idProperty": "CHI67",
    "latProperty": 31.8839,
    "lngProperty": -109.3513,
    "elevationProperty": 1868.0
  },
  {
    "nameProperty": "Lower Walker Canyon",
    "idProperty": "SAN75",
    "latProperty": 31.6662,
    "lngProperty": -110.789,
    "elevationProperty": 1511.0
  },
  {
    "nameProperty": "Pole Saddle",
    "idProperty": "CHI65",
    "latProperty": 31.8399,
    "lngProperty": -109.3443,
    "elevationProperty": 2443.0
  },
  {
    "nameProperty": "Cathedral Vista",
    "idProperty": "CHI74",
    "latProperty": 31.8847,
    "lngProperty": -109.1736,
    "elevationProperty": 1562.0
  },
  {
    "nameProperty": "Idlewild",
    "idProperty": "CHI75",
    "latProperty": 31.8941,
    "lngProperty": -109.1669,
    "elevationProperty": 1533.0
  },
  {
    "nameProperty": "West Turkey Pool",
    "idProperty": "CHI77",
    "latProperty": 31.8643,
    "lngProperty": -109.3551,
    "elevationProperty": 1818.0
  },
  {
    "nameProperty": "Mormon Trail",
    "idProperty": "CHI76",
    "latProperty": 31.8631,
    "lngProperty": -109.3379,
    "elevationProperty": 1883.0
  },
  {
    "nameProperty": "Caslink",
    "idProperty": "DRA13",
    "latProperty": 31.9535,
    "lngProperty": -109.9681,
    "elevationProperty": 1607.0
  },
  {
    "nameProperty": "Shaw Tank III",
    "idProperty": "DRA17",
    "latProperty": 31.9058,
    "lngProperty": -109.9595,
    "elevationProperty": 1620.0
  },
  {
    "nameProperty": "Halfmoon",
    "idProperty": "DRA18",
    "latProperty": 31.9115,
    "lngProperty": -109.9778,
    "elevationProperty": 1748.0
  },
  {
    "nameProperty": "Pipe Spring",
    "idProperty": "PAT26",
    "latProperty": 31.4991,
    "lngProperty": -110.7066,
    "elevationProperty": 1373.0
  },
  {
    "nameProperty": "Cave",
    "idProperty": "HUA22",
    "latProperty": 31.3848,
    "lngProperty": -110.31,
    "elevationProperty": 2093.0
  },
  {
    "nameProperty": "Korn Canyon",
    "idProperty": "HUA18",
    "latProperty": 31.4834,
    "lngProperty": -110.4273,
    "elevationProperty": 1793.0
  },
  {
    "nameProperty": "Lone Mountain North",
    "idProperty": "HUA09",
    "latProperty": 31.4139,
    "lngProperty": -110.4082,
    "elevationProperty": 1744.0
  },
  {
    "nameProperty": "Lone Mountain South",
    "idProperty": "HUA20",
    "latProperty": 31.3894,
    "lngProperty": -110.3671,
    "elevationProperty": 1702.0
  },
  {
    "nameProperty": "Red Rock Canyon Spring",
    "idProperty": "CAN06",
    "latProperty": 31.553,
    "lngProperty": -110.6883,
    "elevationProperty": 1333.0
  },
  {
    "nameProperty": "Lampshire Pass",
    "idProperty": "CAN18",
    "latProperty": 31.5475,
    "lngProperty": -110.6333,
    "elevationProperty": 1480.0
  },
  {
    "nameProperty": "Cottonwood Springs Trail  -  CAN",
    "idProperty": "CAN16",
    "latProperty": 31.5483,
    "lngProperty": -110.6379,
    "elevationProperty": 1494.0
  },
  {
    "nameProperty": "A_test_Julian",
    "idProperty": "AUG07",
    "latProperty": 32.3456,
    "lngProperty": -110.3848,
    "elevationProperty": 6543.0
  },
  {
    "nameProperty": "Little Wood Spring",
    "idProperty": "CHI57",
    "latProperty": 32.1332,
    "lngProperty": -109.3312,
    "elevationProperty": 1651.0
  },
  {
    "nameProperty": "Goodwin1",
    "idProperty": "DOS12",
    "latProperty": 32.1595,
    "lngProperty": -109.4666,
    "elevationProperty": 1455.0
  },
  {
    "nameProperty": "Old Fort Bowie - FOBO",
    "idProperty": "DOS22",
    "latProperty": 32.1478,
    "lngProperty": -109.4334,
    "elevationProperty": 1486.0
  },
  {
    "nameProperty": "Droopy Tree - FOBO",
    "idProperty": "DOS23",
    "latProperty": 32.1563,
    "lngProperty": -109.4547,
    "elevationProperty": 1439.0
  },
  {
    "nameProperty": "Butterfield - FOBO",
    "idProperty": "DOS24",
    "latProperty": 32.1489,
    "lngProperty": -109.4599,
    "elevationProperty": 1508.0
  },
  {
    "nameProperty": "Oak Grove Spring",
    "idProperty": "CAN07",
    "latProperty": 31.5644,
    "lngProperty": -110.665,
    "elevationProperty": 4490.0
  },
  {
    "nameProperty": "Granite Pool ",
    "idProperty": "CHI70",
    "latProperty": 31.9106,
    "lngProperty": -109.2519,
    "elevationProperty": 1978.0
  },
  {
    "nameProperty": "East Turkey Creek ",
    "idProperty": "CHI72",
    "latProperty": 31.9089,
    "lngProperty": -109.2535,
    "elevationProperty": 1987.0
  },
  {
    "nameProperty": "Sorin Pass Road",
    "idProperty": "DRA12",
    "latProperty": 31.8886,
    "lngProperty": -109.9704,
    "elevationProperty": 1898.0
  },
  {
    "nameProperty": "Slavin Gulch Tributary 2",
    "idProperty": "DRA14",
    "latProperty": 31.8895,
    "lngProperty": -110.0182,
    "elevationProperty": 1510.0
  },
  {
    "nameProperty": "Guindani Bathtub",
    "idProperty": "WHE12",
    "latProperty": 31.8542,
    "lngProperty": -110.4022,
    "elevationProperty": 1817.0
  },
  {
    "nameProperty": "Silver Spur Spring - CNM",
    "idProperty": "CHI80",
    "latProperty": 32.0085,
    "lngProperty": -109.3611,
    "elevationProperty": 1621.0
  },
  {
    "nameProperty": "Slavin Gulch Big Pool",
    "idProperty": "DRA11",
    "latProperty": 31.8891,
    "lngProperty": -110.0126,
    "elevationProperty": 1549.0
  },
  {
    "nameProperty": "Slavin Gulch Lower",
    "idProperty": "DRA09",
    "latProperty": 31.8888,
    "lngProperty": -110.0132,
    "elevationProperty": 1525.0
  },
  {
    "nameProperty": "Slavin Gulch ",
    "idProperty": "DRA16",
    "latProperty": 31.8912,
    "lngProperty": -110.0105,
    "elevationProperty": 1654.0
  },
  {
    "nameProperty": "West Stronghold",
    "idProperty": "DRA01",
    "latProperty": 31.9328,
    "lngProperty": -109.9973,
    "elevationProperty": 1569.0
  },
  {
    "nameProperty": "Guzzler",
    "idProperty": "SAN08",
    "latProperty": 31.8264,
    "lngProperty": -110.7743,
    "elevationProperty": 1810.0
  },
  {
    "nameProperty": "Halfmoon Tank",
    "idProperty": "DRA02",
    "latProperty": 31.9328,
    "lngProperty": -109.9973,
    "elevationProperty": 1747.0
  },
  {
    "nameProperty": "Madrone Canyon - CNM",
    "idProperty": "CHI100",
    "latProperty": 32.004,
    "lngProperty": -109.3554,
    "elevationProperty": 1665.0
  },
  {
    "nameProperty": "Goodwin Canyon 2",
    "idProperty": "DOS13",
    "latProperty": 32.1571,
    "lngProperty": -109.4651,
    "elevationProperty": 1467.0
  },
  {
    "nameProperty": "Apache Pass",
    "idProperty": "DOS08",
    "latProperty": 32.158,
    "lngProperty": -109.4478,
    "elevationProperty": 1412.0
  },
  {
    "nameProperty": "DO NOT USE - WILL BE DELETED AFTER DATA CLEANUP - BAD SITEIDGranite Pool",
    "idProperty": "CHI 70",
    "latProperty": 31.9106,
    "lngProperty": -109.2519,
    "elevationProperty": 1978.0
  },
  {
    "nameProperty": "North Fork - CNM",
    "idProperty": "CHI10",
    "latProperty": 31.9665,
    "lngProperty": -109.3084,
    "elevationProperty": 1788.0
  },
  {
    "nameProperty": "Turkey Creek Overlook",
    "idProperty": "CHI105",
    "latProperty": 31.9207,
    "lngProperty": -109.2292,
    "elevationProperty": 1762.0
  },
  {
    "nameProperty": "Paradise Waterfall",
    "idProperty": "CHI106",
    "latProperty": 31.9162,
    "lngProperty": -109.2329,
    "elevationProperty": 1799.0
  },
  {
    "nameProperty": "Badger Hill",
    "idProperty": "CHI107",
    "latProperty": 31.9208,
    "lngProperty": -109.2186,
    "elevationProperty": 1740.0
  },
  {
    "nameProperty": "South Fork II",
    "idProperty": "CHI109",
    "latProperty": 31.8728,
    "lngProperty": -109.1847,
    "elevationProperty": 1615.0
  },
  {
    "nameProperty": "Little Wood Spring b",
    "idProperty": "CHI57b",
    "latProperty": 32.1332,
    "lngProperty": -109.3312,
    "elevationProperty": 1651.0
  },
  {
    "nameProperty": "Droopy Tree b - FOBO",
    "idProperty": "DOS23b",
    "latProperty": 32.1563,
    "lngProperty": -109.4547,
    "elevationProperty": 1439.0
  },
  {
    "nameProperty": "Old Fort Bowie b - FOBO",
    "idProperty": "DOS22b",
    "latProperty": 32.1478,
    "lngProperty": -109.4334,
    "elevationProperty": 1486.0
  },
  {
    "nameProperty": " Clear data coordinates",
    "idProperty": "0000",
    "latProperty": 32.2308,
    "lngProperty": -110.9512,
    "elevationProperty": 792.0
  },
  {
    "nameProperty": "Garden - FORT MONITORED",
    "idProperty": "eDNA00",
    "latProperty": 31.4695,
    "lngProperty": -110.3468,
    "elevationProperty": 0.0
  },
  {
    "nameProperty": "Sawmill   FORT Monitoring",
    "idProperty": "HUA15",
    "latProperty": 31.439,
    "lngProperty": -110.3549,
    "elevationProperty": 2160.0
  },
  {
    "nameProperty": "Pat Scott Peak",
    "idProperty": "HUA28",
    "latProperty": 31.4231,
    "lngProperty": -110.3465,
    "elevationProperty": 2553.0
  },
  {
    "nameProperty": "McClure",
    "idProperty": "HUA16",
    "latProperty": 31.475,
    "lngProperty": -110.3717,
    "elevationProperty": 1859.0
  },
  {
    "nameProperty": "Granite 1",
    "idProperty": "HUA26",
    "latProperty": 31.4135,
    "lngProperty": -110.3363,
    "elevationProperty": 2558.0
  },
  {
    "nameProperty": "Indian Tank",
    "idProperty": "COY01",
    "latProperty": 32.0094,
    "lngProperty": -111.4865,
    "elevationProperty": 943.0
  },
  {
    "nameProperty": "Dills Best",
    "idProperty": "COY05",
    "latProperty": 32.0093,
    "lngProperty": -111.5003,
    "elevationProperty": 1097.0
  },
  {
    "nameProperty": "Granite 2",
    "idProperty": "HUA26",
    "latProperty": 31.4115,
    "lngProperty": -110.3309,
    "elevationProperty": 2499.0
  },
  {
    "nameProperty": "Sycamore Cub Trail #2",
    "idProperty": "CHI104",
    "latProperty": 31.794,
    "lngProperty": -109.3544,
    "elevationProperty": 1996.0
  },
  {
    "nameProperty": "West Bonita Creek - CNM",
    "idProperty": "CHI101",
    "latProperty": 32.0107,
    "lngProperty": -109.3844,
    "elevationProperty": 1581.0
  },
  {
    "nameProperty": "Peterson Peak",
    "idProperty": "HUA25 E",
    "latProperty": 31.4776,
    "lngProperty": -110.3934,
    "elevationProperty": 6476.0
  },
  {
    "nameProperty": "Miller Spring",
    "idProperty": "PEL25",
    "latProperty": 31.4803,
    "lngProperty": -109.0532,
    "elevationProperty": 1570.0
  },
  {
    "nameProperty": "Clanton Tank Wash - active",
    "idProperty": "PEL28",
    "latProperty": 31.526,
    "lngProperty": -108.9964,
    "elevationProperty": 1680.0
  },
  {
    "nameProperty": "South Clanton Draw",
    "idProperty": "PEL29",
    "latProperty": 31.5093,
    "lngProperty": -108.9905,
    "elevationProperty": 1680.0
  },
  {
    "nameProperty": "Swaggerty Trail",
    "idProperty": "PEL32",
    "latProperty": 31.4428,
    "lngProperty": -109.0633,
    "elevationProperty": 1593.0
  },
  {
    "nameProperty": "Whitetail Pass - CNM",
    "idProperty": "CHI103",
    "latProperty": 32.0451,
    "lngProperty": -109.3327,
    "elevationProperty": 2030.0
  },
  {
    "nameProperty": "Bear Spring - Huachuca",
    "idProperty": "HUA21",
    "latProperty": 31.4049,
    "lngProperty": -110.3227,
    "elevationProperty": 2304.0
  },
  {
    "nameProperty": "Crest \u0026 Sawmill ",
    "idProperty": "HUA35",
    "latProperty": 31.4502,
    "lngProperty": -110.3803,
    "elevationProperty": 2077.0
  },
  {
    "nameProperty": "Bear Saddle",
    "idProperty": "HUA36",
    "latProperty": 31.4113,
    "lngProperty": -110.3247,
    "elevationProperty": 0.0
  },
  {
    "nameProperty": "Clanton Tank Wash 1 retired",
    "idProperty": "PEL28",
    "latProperty": 31.5258,
    "lngProperty": -108.9983,
    "elevationProperty": 1700.0
  },
  {
    "nameProperty": "Mushroom Rock - CNM",
    "idProperty": "CHI102",
    "latProperty": 31.9987,
    "lngProperty": -109.3075,
    "elevationProperty": 2059.0
  },
  {
    "nameProperty": "Jesse James Canyon - CNM",
    "idProperty": "CHI88",
    "latProperty": 31.9808,
    "lngProperty": -109.3499,
    "elevationProperty": 1822.0
  },
  {
    "nameProperty": "Sugarloaf Mountain Trail - CNM",
    "idProperty": "CHI97",
    "latProperty": 32.0156,
    "lngProperty": -109.3225,
    "elevationProperty": 2094.0
  },
  {
    "nameProperty": "No Name Spring B - FOBO",
    "idProperty": "CHI64b",
    "latProperty": 32.1398,
    "lngProperty": -109.4467,
    "elevationProperty": 1512.0
  },
  {
    "nameProperty": "Totem Canyon - CNM",
    "idProperty": "CHI108",
    "latProperty": 32.0022,
    "lngProperty": -109.3138,
    "elevationProperty": 1940.0
  },
  {
    "nameProperty": "No Name Spring - FOBO",
    "idProperty": "CHI64",
    "latProperty": 32.1398,
    "lngProperty": -109.4467,
    "elevationProperty": 1512.0
  },
  {
    "nameProperty": "DO NOT USE - WILL BE DELETED AFTER DATA CLEANUP - WRONG SITEID DOS12-Goodwin1",
    "idProperty": "Goodwin1",
    "latProperty": 32.1595,
    "lngProperty": -109.4666,
    "elevationProperty": 1455.0
  },
  {
    "nameProperty": "Cave Canyon",
    "idProperty": "HUA08",
    "latProperty": 31.3823,
    "lngProperty": -110.3217,
    "elevationProperty": 0.0
  },
  {
    "nameProperty": "Jones Canyon III",
    "idProperty": "SAN54",
    "latProperty": 31.635,
    "lngProperty": -110.7891,
    "elevationProperty": 1555.0
  },
  {
    "nameProperty": "Woods_Canyon",
    "idProperty": "DOS01",
    "latProperty": 32.1954,
    "lngProperty": -109.5195,
    "elevationProperty": 1838.0
  },
  {
    "nameProperty": "AP01",
    "idProperty": "DOS19",
    "latProperty": 32.1643,
    "lngProperty": -109.471,
    "elevationProperty": 1829.0
  },
  {
    "nameProperty": "AP02",
    "idProperty": "DOS20",
    "latProperty": 32.1693,
    "lngProperty": -109.4775,
    "elevationProperty": 1576.0
  },
  {
    "nameProperty": "AP03",
    "idProperty": "DOS21",
    "latProperty": 32.1671,
    "lngProperty": -109.4828,
    "elevationProperty": 1629.0
  },
  {
    "nameProperty": "Mansfield Canyon",
    "idProperty": "SAN13",
    "latProperty": 31.619,
    "lngProperty": -110.8273,
    "elevationProperty": 1561.0
  },
  {
    "nameProperty": "Sugarloaf Mountain ",
    "idProperty": "CHI97 ",
    "latProperty": 32.0156,
    "lngProperty": -109.3225,
    "elevationProperty": 2094.0
  },
  {
    "nameProperty": "Jones Canyon III",
    "idProperty": "SAN54",
    "latProperty": 31.6334,
    "lngProperty": -110.8125,
    "elevationProperty": 1555.0
  },
  {
    "nameProperty": "DO NOT USE  - WILL BE DELETED AFTER DATA CLEANUP - WRONG SITEIDCHI64-No Name Spring",
    "idProperty": "No Name Spring",
    "latProperty": 32.1397,
    "lngProperty": -109.4467,
    "elevationProperty": 1530.0
  },
  {
    "nameProperty": "Turkey Pen Tinajas",
    "idProperty": "CHI67",
    "latProperty": 31.893,
    "lngProperty": -109.3509,
    "elevationProperty": 1860.0
  },
  {
    "nameProperty": "Caslink Canyon Narrows",
    "idProperty": "DRA06",
    "latProperty": 31.951,
    "lngProperty": -109.9613,
    "elevationProperty": 1507.0
  },
  {
    "nameProperty": "Fitch Junction ",
    "idProperty": "CHI66",
    "latProperty": 31.8969,
    "lngProperty": -109.3369,
    "elevationProperty": 1971.0
  },
  {
    "nameProperty": "No Name Tank - SAN",
    "idProperty": "SAN37",
    "latProperty": 31.635,
    "lngProperty": -110.7891,
    "elevationProperty": 1585.0
  },
  {
    "nameProperty": "Walker Spring",
    "idProperty": "SAN23",
    "latProperty": 31.635,
    "lngProperty": -110.7891,
    "elevationProperty": 1720.0
  },
  {
    "nameProperty": "Bear Springs - Santa Rita",
    "idProperty": "SAN22",
    "latProperty": 31.7252,
    "lngProperty": -110.7889,
    "elevationProperty": 1755.0
  },
  {
    "nameProperty": "*DO NOT USE* Mansfield-3",
    "idProperty": "SAN19",
    "latProperty": 31.6351,
    "lngProperty": -110.8945,
    "elevationProperty": 1770.0
  },
  {
    "nameProperty": "DO NOT USE - WILL BE DELETED AFTER DATA CLEANUP WRONG SITEID CH157-Little Wood Spring",
    "idProperty": "Little Wood Spring",
    "latProperty": 32.1332,
    "lngProperty": -109.3312,
    "elevationProperty": 1651.0
  },
  {
    "nameProperty": "Josephine Canyon",
    "idProperty": "SAN40",
    "latProperty": 31.6351,
    "lngProperty": -110.8945,
    "elevationProperty": 1730.0
  },
  {
    "nameProperty": "Shaw Tank",
    "idProperty": "DRA03",
    "latProperty": 31.9063,
    "lngProperty": -109.958,
    "elevationProperty": 1623.0
  },
  {
    "nameProperty": "BSC Ridge",
    "idProperty": "SAN28",
    "latProperty": 31.7252,
    "lngProperty": -110.7889,
    "elevationProperty": 1690.0
  },
  {
    "nameProperty": "Dart Ranch ",
    "idProperty": "CHI68",
    "latProperty": 31.7808,
    "lngProperty": -109.3954,
    "elevationProperty": 1795.0
  },
  {
    "nameProperty": "West Stronghold Canyon",
    "idProperty": "DRA05",
    "latProperty": 31.9287,
    "lngProperty": -109.9922,
    "elevationProperty": 1619.0
  },
  {
    "nameProperty": "Goodwin Canyon 1",
    "idProperty": "DOS12",
    "latProperty": 32.1595,
    "lngProperty": -109.4667,
    "elevationProperty": 1455.0
  },
  {
    "nameProperty": "AZ Trail",
    "idProperty": "SAN49",
    "latProperty": 31.7252,
    "lngProperty": -110.7889,
    "elevationProperty": 1795.0
  },
  {
    "nameProperty": "Shaw Tank II",
    "idProperty": "DRA04",
    "latProperty": 31.9064,
    "lngProperty": -109.958,
    "elevationProperty": 1628.0
  },
  {
    "nameProperty": "Ridgetop b",
    "idProperty": "EMP04b",
    "latProperty": 31.8937,
    "lngProperty": -110.6139,
    "elevationProperty": 1446.0
  },
  {
    "nameProperty": "Bloody Trail ",
    "idProperty": "DOS10",
    "latProperty": 32.227,
    "lngProperty": -109.5441,
    "elevationProperty": 1487.0
  },
  {
    "nameProperty": "Pipe Springs",
    "idProperty": "PAT26",
    "latProperty": 31.499,
    "lngProperty": -110.7063,
    "elevationProperty": 1376.0
  },
  {
    "nameProperty": "Sorin Pass",
    "idProperty": "DRA10",
    "latProperty": 31.8875,
    "lngProperty": -110.0142,
    "elevationProperty": 1519.0
  },
  {
    "nameProperty": "Gilda Spring ",
    "idProperty": "DRA15",
    "latProperty": 31.8634,
    "lngProperty": -109.9482,
    "elevationProperty": 1782.0
  },
  {
    "nameProperty": "DOS23_Droopy Tree",
    "idProperty": "Droopy Tree",
    "latProperty": 3.2182,
    "lngProperty": -109.6885,
    "elevationProperty": 4720.0
  },
  {
    "nameProperty": "Newton Canyon - CNM",
    "idProperty": "CHI83m",
    "latProperty": 31.998,
    "lngProperty": -109.3681,
    "elevationProperty": 1677.0
  },
  {
    "nameProperty": "Tule",
    "idProperty": "PBR01",
    "latProperty": 34.0898,
    "lngProperty": -113.9059,
    "elevationProperty": 0.0
  },
  {
    "nameProperty": "Jesse James II - CNM",
    "idProperty": "CHI110",
    "latProperty": 31.9825,
    "lngProperty": -109.3473,
    "elevationProperty": 1738.0
  },
  {
    "nameProperty": "Grapes",
    "idProperty": "CHI112",
    "latProperty": 31.7561,
    "lngProperty": -109.3601,
    "elevationProperty": 1715.0
  },
  {
    "nameProperty": "Goodwin1",
    "idProperty": "DOS12",
    "latProperty": 0.1595,
    "lngProperty": -109.4666,
    "elevationProperty": 1455.0
  },
  {
    "nameProperty": "Walker Spring",
    "idProperty": "SAN23",
    "latProperty": 31.6667,
    "lngProperty": -110.8168,
    "elevationProperty": 1721.0
  },
  {
    "nameProperty": "D\u0026H Canyon II",
    "idProperty": "SAN30",
    "latProperty": 31.6525,
    "lngProperty": -110.8159,
    "elevationProperty": 1624.0
  },
  {
    "nameProperty": "Deep Pool",
    "idProperty": "CHI111",
    "latProperty": 31.7694,
    "lngProperty": -109.3511,
    "elevationProperty": 1763.0
  },
  {
    "nameProperty": "West Stronghold",
    "idProperty": "DRA05",
    "latProperty": 31.9288,
    "lngProperty": -109.9922,
    "elevationProperty": 5488.0
  },
  {
    "nameProperty": "Spark",
    "idProperty": "HUA31",
    "latProperty": 31.3485,
    "lngProperty": -110.2729,
    "elevationProperty": 2297.0
  },
  {
    "nameProperty": "GATE ACCESS",
    "idProperty": "eDNA Access",
    "latProperty": 31.3351,
    "lngProperty": -110.2883,
    "elevationProperty": 0.0
  },
  {
    "nameProperty": "Texas Mine ",
    "idProperty": "HUA34",
    "latProperty": 31.3522,
    "lngProperty": -110.2731,
    "elevationProperty": 1632.0
  },
  {
    "nameProperty": "Blue Water",
    "idProperty": "HUA32",
    "latProperty": 31.3502,
    "lngProperty": -110.258,
    "elevationProperty": 1644.0
  },
  {
    "nameProperty": "Yaqui Spring ",
    "idProperty": "HUA33",
    "latProperty": 31.3346,
    "lngProperty": -110.2865,
    "elevationProperty": 2008.0
  },
  {
    "nameProperty": "Little Oaks",
    "idProperty": "CHI113",
    "latProperty": 31.7162,
    "lngProperty": -109.2274,
    "elevationProperty": 1610.0
  },
  {
    "nameProperty": "Brushy Wash",
    "idProperty": "CHI112",
    "latProperty": 31.7181,
    "lngProperty": -109.2285,
    "elevationProperty": 1615.0
  },
  {
    "nameProperty": "Yucca Wash",
    "idProperty": "CHI114",
    "latProperty": 31.7091,
    "lngProperty": -109.2297,
    "elevationProperty": 1595.0
  },
  {
    "nameProperty": "Upper Foster Draw",
    "idProperty": "PEL37",
    "latProperty": 31.4842,
    "lngProperty": -108.982,
    "elevationProperty": 1713.0
  }
].sort((a,b) => a.idProperty.localeCompare(b.idProperty)));

/** React context for sandbox uploaded folders */
export const SandboxInfoContext = createContext(null);
/** React context for species information */
export const SpeciesInfoContext = createContext([
  {
    "name": "Badger",
    "scientificName": "Taxidea taxus",
    "speciesIconURL": "https://arizona.box.com/shared/static/le9xa515z0h4143xtgjlp4z4w5xy3lgy.jpg",
    "keyBinding": "E"
  },
  {
    "name": "Bear",
    "scientificName": "Ursus americanus",
    "speciesIconURL": "https://arizona.box.com/shared/static/dcxcm0y8u6cnwcz6tftovo68ixkcd2c0.jpg",
    "keyBinding": "B"
  },
  {
    "name": "Bighorn",
    "scientificName": "Ovis Canadensis nelsoni",
    "speciesIconURL": "https://arizona.box.com/shared/static/hr9fbm3b6fnbb8yg8uloymmeji4ja51q.jpg",
    "keyBinding": null
  },
  {
    "name": "Grey Hawk",
    "scientificName": "Buteo plagiatus",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  },
  {
    "name": "Bobcat",
    "scientificName": "Lynx rufus",
    "speciesIconURL": "https://arizona.box.com/shared/static/wo7la9yp6vjgjxnwna5ohb3wt4xozpf7.jpg",
    "keyBinding": "L"
  },
  {
    "name": "Coatimundi",
    "scientificName": "Nasua narica",
    "speciesIconURL": "https://arizona.box.com/shared/static/2q0f04h3tqiqcexugksleqv26jhv015v.jpg",
    "keyBinding": "O"
  },
  {
    "name": "Cow",
    "scientificName": "Bos tarus",
    "speciesIconURL": "https://arizona.box.com/shared/static/zz058f4tqloy78tfkh7yau4t2org4ey8.jpg",
    "keyBinding": "C"
  },
  {
    "name": "Coyote",
    "scientificName": "Canis latrans",
    "speciesIconURL": "https://arizona.box.com/shared/static/k6zcxzjfymezhjpocmcvl6qrb9dulo0i.jpg",
    "keyBinding": "Y"
  },
  {
    "name": "Domestic Dog",
    "scientificName": "Canis familiaris",
    "speciesIconURL": "https://arizona.box.com/shared/static/bo10uf996fa6cb75c2rbhwla8e3el1tu.jpg",
    "keyBinding": "D"
  },
  {
    "name": "Fox",
    "scientificName": "Urocyon sp. Vulpes spp.",
    "speciesIconURL": "https://arizona.box.com/shared/static/hjjb6d6ysl6ufksfjtvjvyebysm1bvr9.jpg",
    "keyBinding": "F"
  },
  {
    "name": "Ghost",
    "scientificName": "Casper",
    "speciesIconURL": "https://arizona.box.com/shared/static/b68jxx9b364ccklcy3qss5b3eur2imwh.jpg",
    "keyBinding": "G"
  },
  {
    "name": "Gila Monster",
    "scientificName": "Heloderma suspectum",
    "speciesIconURL": "https://arizona.box.com/shared/static/gac34vf3pc83910u6guhslm66gxw5z8k.jpg",
    "keyBinding": null
  },
  {
    "name": "Horse",
    "scientificName": "Equus caballus",
    "speciesIconURL": "https://arizona.box.com/shared/static/0obmlj0j3uo3u4nxgkf8zmpod7eb87w3.jpg",
    "keyBinding": "Q"
  },
  {
    "name": "Human",
    "scientificName": "Homo sapiens",
    "speciesIconURL": "https://arizona.box.com/shared/static/6wb3424e4gqccpn3t58kgaybs2splv41.jpg",
    "keyBinding": "H"
  },
  {
    "name": "Jaguar",
    "scientificName": "Panthera onca",
    "speciesIconURL": "https://arizona.box.com/shared/static/lw9rz5oegolvryos1npm3coteltinw40.jpg",
    "keyBinding": null
  },
  {
    "name": "Javelina",
    "scientificName": "Pecari tajacu",
    "speciesIconURL": "https://arizona.box.com/shared/static/ck0ust0gl7ub4eb8rgsbyujo13zvtmrq.jpg",
    "keyBinding": "J"
  },
  {
    "name": "Lizard",
    "scientificName": "Lacertilia spp.",
    "speciesIconURL": "https://arizona.box.com/shared/static/81ilzi7f26lsmzrq0atb2aojl7uzw40e.jpg",
    "keyBinding": null
  },
  {
    "name": "Deer (Mule)",
    "scientificName": "Odocoileus hemionus",
    "speciesIconURL": "https://arizona.box.com/shared/static/gu5ici81nmmelubnzb602mjg88dhqp8r.jpg",
    "keyBinding": "M"
  },
  {
    "name": "Deer (White-Tailed)",
    "scientificName": "Odocoileus virginianus",
    "speciesIconURL": "https://arizona.box.com/shared/static/9pe69jwbv8z65c9isugtbpak2w6cbn8g.jpg",
    "keyBinding": "W"
  },
  {
    "name": "Ocelot",
    "scientificName": "Leopardus pardalis",
    "speciesIconURL": "https://arizona.box.com/shared/static/9tvofcred8qgy4jmi91dflqtc5r9pbjv.jpg",
    "keyBinding": null
  },
  {
    "name": "Opossum",
    "scientificName": "Didelphis marsupialis",
    "speciesIconURL": "https://arizona.box.com/shared/static/sh0gwe9s907i1ky8f1ezoogbmbh7r4f3.jpg",
    "keyBinding": null
  },
  {
    "name": "Pronghorn",
    "scientificName": "Antilocapra americana",
    "speciesIconURL": "https://arizona.box.com/shared/static/14j5w4drxre29i0vipmo2jgcnnaf5qa1.jpg",
    "keyBinding": null
  },
  {
    "name": "Puma",
    "scientificName": "Puma concolor",
    "speciesIconURL": "https://arizona.box.com/shared/static/nk4mndfkzl48ecpdty65ps34fev3voy6.jpg",
    "keyBinding": "P"
  },
  {
    "name": "Racoon",
    "scientificName": "Procyon lotor",
    "speciesIconURL": "https://arizona.box.com/shared/static/fy4r198unut8yeaockis3iirt12je7z1.jpg",
    "keyBinding": "A"
  },
  {
    "name": "Ringtail",
    "scientificName": "Bassariscus astutus",
    "speciesIconURL": "https://arizona.box.com/shared/static/mfawvlr604jwecqner76aznqxc0403d6.jpg",
    "keyBinding": "N"
  },
  {
    "name": "Rodent",
    "scientificName": "Rodentia",
    "speciesIconURL": "https://arizona.box.com/shared/static/qek2tp6hz88x4l3cmqhy7k8pwu7qwptn.jpg",
    "keyBinding": "Z"
  },
  {
    "name": "Skunk",
    "scientificName": "Mephitis spp. Spilogale sp. Conepatus sp.",
    "speciesIconURL": "https://arizona.box.com/shared/static/mysrtwqnazahzp3jyun58y3c7gpz0qm9.jpg",
    "keyBinding": null
  },
  {
    "name": "Skunk (Hog-Nosed)",
    "scientificName": "Conepatus leuconotus",
    "speciesIconURL": "https://arizona.box.com/shared/static/hpay9f13riudz1bcgvel54xs7i8jlkpg.jpg",
    "keyBinding": null
  },
  {
    "name": "Skunk (Hooded)",
    "scientificName": "Mephitis macroura",
    "speciesIconURL": "https://arizona.box.com/shared/static/ht5ks1kx5lpyg9xnf1amxgaibq9f7r0z.jpg",
    "keyBinding": null
  },
  {
    "name": "Skunk (Striped)",
    "scientificName": "Mephitis mephitis",
    "speciesIconURL": "https://arizona.box.com/shared/static/ff1qzko7jipfr381cjddvtfcf7dc01ig.jpg",
    "keyBinding": null
  },
  {
    "name": "Skunk (Western Spotted)",
    "scientificName": "Spilogale gracilis",
    "speciesIconURL": "https://arizona.box.com/shared/static/kn4qr64s3wfsb6gegscgv4z7461uajpn.jpg",
    "keyBinding": null
  },
  {
    "name": "Sonoran Mud Turtle",
    "scientificName": "Kinosternon sonoriense",
    "speciesIconURL": "https://arizona.box.com/shared/static/q0pzwiow20q8nawmeip2kpbhwk54ev2o.jpg",
    "keyBinding": null
  },
  {
    "name": "Spotted Owl",
    "scientificName": "Strix occidentalis",
    "speciesIconURL": "https://arizona.box.com/shared/static/nd8l4pia5grlymxv1bycsb2mwli80obu.jpg",
    "keyBinding": null
  },
  {
    "name": "Squirrel",
    "scientificName": "Sciurus spp.",
    "speciesIconURL": "https://arizona.box.com/shared/static/w4437lx1wpsgzb55r95e1vajpro5pvsl.jpg",
    "keyBinding": "S"
  },
  {
    "name": "Tortoise",
    "scientificName": "Gopherus morafkai",
    "speciesIconURL": "https://arizona.box.com/shared/static/ahx3293u8j41ejzf4vcwjjwuy7beb155.jpg",
    "keyBinding": null
  },
  {
    "name": "Turkey",
    "scientificName": "Meleagris gallopavo",
    "speciesIconURL": "https://arizona.box.com/shared/static/1xt2pasyyzjkqiirc5pz87uye3duklvy.jpg",
    "keyBinding": "U"
  },
  {
    "name": "Test",
    "scientificName": "Test",
    "speciesIconURL": "https://arizona.box.com/shared/static/9505fzv7yd0vj8dhhwu9p662emmq1fj5.jpg",
    "keyBinding": "T"
  },
  {
    "name": "Frog",
    "scientificName": "Rana Temporaria",
    "speciesIconURL": "https://arizona.box.com/shared/static/y2ebc37cpx31imfvo3buiss632aper59.jpg",
    "keyBinding": null
  },
  {
    "name": "Rabbit (Desert Cottontail)",
    "scientificName": "Sylvilagus audubonii",
    "speciesIconURL": "https://arizona.box.com/shared/static/w2zl2w4j008119ctk1x52aakgroa800f.jpg",
    "keyBinding": null
  },
  {
    "name": "Hare (Black-Tailed Jackrabbit)",
    "scientificName": "Lepus californicus",
    "speciesIconURL": "https://arizona.box.com/shared/static/ygqexm7urzsm1ephi3aov5u5fwx0lzbq.jpg",
    "keyBinding": null
  },
  {
    "name": "Hare (Antelope Jackrabbit)",
    "scientificName": " Lepus alleni",
    "speciesIconURL": "https://arizona.box.com/shared/static/oz0zgd3trb44b7n2kdng9uvq7uawrvxk.jpg",
    "keyBinding": null
  },
  {
    "name": "Hare (Jackrabbits other)",
    "scientificName": "Lepus spp.",
    "speciesIconURL": "https://arizona.box.com/shared/static/yvtfk4554rabw31wspxe0b58f1i0abv4.jpg",
    "keyBinding": null
  },
  {
    "name": "Unknown",
    "scientificName": "Incognita",
    "speciesIconURL": "https://arizona.box.com/shared/static/5i52i7uw79cydn8lrbi74qonbqgxmir3.png",
    "keyBinding": "SLASH"
  },
  {
    "name": "Owl",
    "scientificName": "Strigiformes",
    "speciesIconURL": "https://arizona.box.com/shared/static/m7pnij0v5h21kkhcjifbq9wdb2czn4ck.jpg",
    "keyBinding": null
  },
  {
    "name": "Porcupine",
    "scientificName": "Erethizon dorsatum",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  },
  {
    "name": "Raptor",
    "scientificName": "Falconiformes",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  },
  {
    "name": "Insect (flying)",
    "scientificName": "Arthropodus aviator",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  },
  {
    "name": "Snake",
    "scientificName": "Serpentes",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  },
  {
    "name": "Caterpillar (moths \u0026 butterflies)",
    "scientificName": "Lepidoptera",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  },
  {
    "name": "Montezuma Quail",
    "scientificName": "Cyrtonyx montezumae",
    "speciesIconURL": "https://upload.wikimedia.org/wikipedia/commons/e/ea/072_-_MONTEZUMA_QUAIL_%288-20-2014%29_78_circulo_montana%2C_patagonia_lake_ranch_estates%2C_scc%2C_az_-01_%2814805362757%29.jpg",
    "keyBinding": null
  },
  {
    "name": "Rock Squirrel",
    "scientificName": "Otospermophilus variegatus",
    "speciesIconURL": "https://skyislandalliance.org/wp-content/uploads/2020/08/5205548038_bdd96920f0_b.jpg",
    "keyBinding": "V"
  },
  {
    "name": "Bat",
    "scientificName": "Chiroptera",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  },
  {
    "name": "Bird",
    "scientificName": "Aves",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": "I"
  },
  {
    "name": "Northern Goshawk ",
    "scientificName": "Accipiter Gentilis",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  },
  {
    "name": "Mexican Gray Wolf",
    "scientificName": "Canis lupus baileyi",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  }
].sort((a,b) => a.name.localeCompare(b.name)));

/** React context for user login token */
export const TokenContext = createContext(null);
/** React context for running on a mobile device */
export const MobileDeviceContext = createContext(false);
/** React context for narrow windows */
export const NarrowWindowContext = createContext(false);
