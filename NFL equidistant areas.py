# Generate dot map of closest team given hardcoded home stadium coordinates
# Methodology:
#   If a team played home games in a given year, they get their color on the map
#   If they were home in multiple stadiums, but one more than others, use the one with more
#   If they were home in multiple staduims similar number of games, take a point between them
#   If two teams had the same home stadium, show as stripes in the joint area
#   Team color is the author's choice, although effort was made to:
#       pick from the team's color set,
#       be consistent year-to-year, and
#       keep adjacent colors on the map from being too similar
# Then compose into a gif file

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.ticker import NullFormatter, FixedLocator
import math
from colorama import Fore, Back, Style
import os
import glob
from PIL import Image


# Set your output path
output_path = os.path.join(os.getcwd(), 'NFL gif')


# Convert hex colors to RGB
valid_hex = '0123456789ABCDEF'.__contains__
def cleanhex(data):
    return ''.join(filter(valid_hex, data.upper()))

def fore_fromhex(text, hexcode):
    """print in a hex defined color"""
    hexint = int(cleanhex(hexcode), 16)

    if hexint >= 808080: # Bad way to do between white and black
        background = Back.BLACK
    else:
        background = Back.WHITE

    print(background
          + "\x1B[38;2;{};{};{}m{}\x1B[0m".format(hexint>>16
                                                  , hexint>>8&0xFF
                                                  , hexint&0xFF
                                                  , text)
         )


# All stadium data since 1920 with lat/long, team, and start/end
# Includes AFL 1960-69
stadia_header = ['coordinates', 'latitude', 'longitude', 'color', 'start', 'end']
stadia_alltime = [
    # Current NFL teams
    # https://en.wikipedia.org/wiki/Chronology_of_home_stadiums_for_current_National_Football_League_teams
    # Raiders
      ['36°05′27″N 115°11′01″W', '#a5acaf', 2020, np.inf]
    , ['37°45′6″N 122°12′2″W'  , '#a5acaf', 1995, 2019  ]
    , ['34°0′51″N 118°17′16″W' , '#a5acaf', 1982, 1994  ]
    , ['37°45′6″N 122°12′2″W'  , '#a5acaf', 1966, 1981  ]
    , ['37°47′38″N 122°15′47″W', '#a5acaf', 1962, 1965  ]
    , ['37°42′49″N 122°23′10″W', '#a5acaf', 1961, 1961  ]
    , ['37°44′25″N 122°25′16″W', '#a5acaf', 1960, 1960  ] # Between two home stadiums
    # Rams + Chargers
    , ['33°57′12″N 118°20′21″W', '#fed02a', 2020, np.inf] # stripes of #0073cf
    , ['34°0′51″N 118°17′16″W' , '#fed02a', 1960, 1960  ]
    # Chargers
    , ['33°51′50″N 118°15′40″W', '#0073cf', 2017, 2019  ]
    , ['32°46′59″N 117°7′10″W' , '#0073cf', 1967, 2016  ]
    , ['32°43′15″N 117°9′2″W'  , '#0073cf', 1961, 1966  ]
    # Rams
    , ['34°0′51″N 118°17′16″W' , '#fed02a', 2016, 2019  ]
    , ['38°37′58″N 90°11′19″W' , '#fed02a', 1996, 2015  ]
    , ['38°37′42″N 90°11′31″W' , '#fed02a', 1995, 1995  ] # Between two home stadiums
    , ['33°48′1″N 117°52′58″W' , '#fed02a', 1980, 1994  ]
    , ['34°0′51″N 118°17′16″W' , '#fed02a', 1961, 1979  ]
    , ['34°0′51″N 118°17′16″W' , '#fed02a', 1946, 1959  ]
    , ['41°30′41″N 81°38′39″W' , '#fed02a', 1944, 1945  ]
    , ['41°30′41″N 81°38′39″W' , '#fed02a', 1942, 1942  ]
    , ['41°30′24″N 81°41′50″W' , '#fed02a', 1939, 1941  ]
    , ['41°32′27″N 81°35′00″W' , '#fed02a', 1938, 1938  ]
    , ['41°30′41″N 81°38′39″W' , '#fed02a', 1937, 1937  ]
    # Falcons
    , ['33°45′20″N 84°24′00″W' , '#a71930', 2017, np.inf]
    , ['33°45′29″N 84°24′4″W'  , '#a71930', 1992, 2016  ]
    , ['33°44′20″N 84°23′20″W' , '#a71930', 1966, 1991  ]
    # Vikings
    , ['44°58′26″N 93°15′29″W' , '#4f2683', 2016, np.inf]
    , ['44°58′34″N 93°13′30″W' , '#4f2683', 2014, 2015  ]
    , ['44°58′26″N 93°15′29″W' , '#4f2683', 1982, 2013  ]
    , ['44°51′16″N 93°14′31″W' , '#4f2683', 1961, 1981  ]
    # 49ers
    , ['37°24′10″N 121°58′12″W', '#aa0000', 2014, np.inf]
    , ['37°42′49″N 122°23′10″W', '#aa0000', 1971, 2013  ]
    , ['37°46′1″N 122°27′22″W' , '#aa0000', 1946, 1970  ]
    # Giants + Jets
    , ['40°48′48″N 74°4′27″W'  , '#0b2265', 2010, np.inf] # stripes
    , ['40°48′44″N 74°4′37″W'  , '#0b2265', 1984, 2009  ]
    , ['40°45′20″N 73°50′53″W' , '#0b2265', 1975, 1975  ]
    # Jets-Titans
    , ['40°45′20″N 73°50′53″W' , '#003f2d', 1976, 1983  ]
    , ['40°45′20″N 73°50′53″W' , '#003f2d', 1964, 1974  ]
    , ['40°49′51″N 73°56′15″W' , '#003f2d', 1960, 1963  ]
    # Giants (owned by the Maras)
    , ['40°48′44″N 74°4′37″W'  , '#0b2265', 1976, 1983  ]
    , ['41°18′47″N 72°57′36″W' , '#0b2265', 1973, 1974  ]
    , ['40°49′37″N 73°55′41″W' , '#0b2265', 1956, 1972  ]
    , ['40°49′51″N 73°56′15″W' , '#0b2265', 1925, 1955  ]
    # Cowboys
    , ['32°44′52″N 97°5′34″W'  , '#002244', 2009, np.inf]
    , ['32°50′24″N 96°54′40″W' , '#002244', 1971, 2008  ]
    , ['32°46′44″N 96°45′37″W' , '#002244', 1963, 1970  ]
    # As stripes in Dallas's Cotton bowl in 1960-62
    # Colts
    , ['39°45′36″N 86°9′49″W'  , '#002C5F', 2008, np.inf]
    , ['39°45′49″N 86°9′48″W'  , '#002C5F', 1984, 2007  ]
    , ['39°19′46″N 76°36′5″W'  , '#002C5F', 1953, 1983  ]
    , ['39°19′46″N 76°36′5″W'  , '#008000', 1950, 1952  ] # Officially a different franchise
    # Cardinals
    , ['33°31′40″N 112°15′46″W', '#97233f', 2006, np.inf]
    , ['33°25′35″N 111°55′57″W', '#97233f', 1988, 2005  ]
    , ['38°37′26″N 90°11′33″W' , '#97233f', 1966, 1987  ]
    , ['38°39′21″N 90°13′12″W' , '#97233f', 1960, 1965  ]
    , ['43°21′30″N 90°19′46″W' , '#97233f', 1959, 1959  ] # Between two home stadiums
    , ['41°49′55″N 87°38′2″W'  , '#97233f', 1945, 1958  ]
    , ['41°49′55″N 87°38′2″W'  , '#FFB612', 1944, 1944  ] # Card-Pitt
    , ['41°49′55″N 87°38′2″W'  , '#97233f', 1929, 1943  ]
    , ['41°46′53″N 87°39′16″W' , '#97233f', 1926, 1928  ]
    , ['41°49′55″N 87°38′2″W'  , '#97233f', 1922, 1925  ]
    , ['41°46′53″N 87°39′16″W' , '#97233f', 1920, 1921  ]
    # Eagles
    , ['39°54′3″N 75°10′3″W'   , '#004c54', 2003, np.inf]
    , ['39°54′24″N 75°10′16″W' , '#004c54', 1971, 2002  ]
    , ['39°57′0″N 75°11′24″W'  , '#004c54', 1958, 1970  ]
    , ['39°59′46″N 75°9′54″W'  , '#004c54', 1944, 1957  ]
    , ['39°59′46″N 75°9′54″W'  , '#FFB612', 1943, 1943  ] # Steagles
    , ['39°59′46″N 75°9′54″W'  , '#004c54', 1942, 1952  ]
    , ['39°54′05″N 75°10′19″W' , '#004c54', 1941, 1941  ]
    , ['39°59′46″N 75°9′54″W'  , '#004c54', 1940, 1940  ]
    , ['39°54′05″N 75°10′19″W' , '#004c54', 1936, 1939  ]
    , ['39°59′35″N 75°9′21″W'  , '#004c54', 1933, 1935  ]
    # Lions-Spartans
    , ['42°20′24″N 83°2′44″W'  , '#0076B6', 2002, np.inf]
    , ['42°38′45″N 83°15′18″W' , '#0076B6', 1975, 2001  ]
    , ['42°19′55″N 83°4′8″W'   , '#0076B6', 1938, 1974  ]
    , ['42°24′57″N 83°8′12″W'  , '#0076B6', 1934, 1937  ]
    , ['38°43′43″N 82°58′42″W' , '#500878', 1930, 1933  ]
    # Seahawks
    , ['47°35′42″N 122°19′53″W', '#002244', 2002, np.inf]
    , ['47°39′1″N 122°18′6″W'  , '#002244', 2000, 2001  ]
    , ['47°35′43″N 122°19′53″W', '#002244', 1976, 1999  ]
    # Patriots
    , ['42°05′28″N 71°15′50″W' , '#b0b7bc', 2002, np.inf]
    , ['42°05′34″N 71°16′03″W' , '#b0b7bc', 1971, 2001  ]
    , ['42°21′59″N 71°7′38″W'  , '#b0b7bc', 1970, 1970  ]
    , ['42°20′6″N 71°09′59″W'  , '#b0b7bc', 1969, 1969  ]
    , ['42°20′47″N 71°5′52″W'  , '#b0b7bc', 1963, 1968  ]
    , ['42°21′11″N 71°7′9″W'   , '#b0b7bc', 1960, 1962  ]
    # Texans of Houston
    , ['29°41′5″N 95°24′39″W'  , '#A71930', 2002, np.inf]
    # Broncos
    , ['39°44′38″N 105°1′12″W' , '#FB4F14', 2001, np.inf]
    , ['39°44′46″N 105°1′18″W' , '#FB4F14', 1960, 2000  ]
    # Steelers-Pirates
    , ['40°26′48″N 80°0′57″W'  , '#FFB612', 2001, np.inf]
    , ['40°26′48″N 80°0′46″W'  , '#FFB612', 1970, 2000  ]
    , ['40°26′39″N 79°57′43″W' , '#FFB612', 1964, 1969  ]
    , ['40°26′35″N 79°57′29″W' , '#FFB612', 1958, 1963  ] # Between two home stadiums
    , ['40°26′31″N 79°57′15″W' , '#FFB612', 1933, 1957  ]
    # Bengals
    , ['39°5′42″N 84°30′57″W'  , '#fb4f14', 2000, np.inf]
    , ['39°5′48″N 84°30′30″W'  , '#fb4f14', 1970, 1999  ]
    , ['39°7′52″N 84°30′58″W'  , '#fb4f14', 1968, 1969  ]
    # Browns
    , ['41°30′22″N 81°41′58″W' , '#311d00', 1999, np.inf] # Note gap
    , ['41°30′24″N 81°41′50″W' , '#311d00', 1946, 1995  ]
    # Titans-Oilers
    , ['36°9′59″N 86°46′17″W'  , '#4b92db', 1999, np.inf]
    , ['36°8′39″N 86°48′32″W'  , '#4b92db', 1998, 1998  ]
    , ['35°7′16″N 89°58′39″W'  , '#4b92db', 1997, 1997  ]
    , ['29°41′6″N 95°24′28″W'  , '#4b92db', 1968, 1996  ]
    , ['29°42′59″N 95°24′33″W' , '#4b92db', 1965, 1967  ]
    , ['29°43′19″N 95°20′57″W' , '#4b92db', 1960, 1964  ]
    # Ravens
    , ['39°16′41″N 76°37′22″W' , '#241773', 1998, np.inf]
    , ['39°19′46″N 76°36′5″W'  , '#241773', 1996, 1997  ]
    # Buccaneers of Tampa Bay
    , ['27°58′33″N 82°30′12″W' , '#34302b', 1998, np.inf]
    , ['27°58′44″N 82°30′13″W' , '#34302b', 1976, 1997  ]
    # Washington Football Team and predecessors
    , ['38°54′28″N 76°51′52″W' , '#773141', 1997, np.inf]
    , ['38°53′24″N 76°58′19″W' , '#773141', 1961, 1996  ]
    , ['38°55′3″N 77°1′13″W'   , '#773141', 1937, 1960  ]
    , ['42°20′47″N 71°5′52″W'  , '#773141', 1933, 1936  ]
    , ['42°21′11″N 71°7′8″W'   , '#773141', 1932, 1932  ]
    # Panthers of Carolina
    , ['35°13′33″N 80°51′10″W' , '#0085ca', 1996, np.inf]
    , ['34°40′43″N 82°50′35″W' , '#0085ca', 1995, 1995  ]
    # Jaguars
    , ['30°19′26″N 81°38′15″W' , '#006778', 1995, np.inf]
    # Dolphins
    , ['25°57′29″N 80°14′20″W' , '#008e97', 1987, np.inf]
    , ['25°46′41″N 80°13′12″W' , '#008e97', 1966, 1986  ]
    # Saints
    , ['29°57′3″N 90°4′52″W'   , '#d3bc8d', 2006, np.inf]
    , ['29°54′34″N 94°49′55″W' , '#d3bc8d', 2005, 2005  ] # Between two home stadiums, excluding one home game in New Jersey
    , ['29°57′3″N 90°4′52″W'   , '#d3bc8d', 1975, 2004  ]
    , ['29°56′34″N 90°7′3″W'   , '#d3bc8d', 1967, 1974  ]
    # Bills
    , ['42°46′26″N 78°47′13″W' , '#c60c30', 1973, 2027  ]
    , ['42°54′18″N 78°51′22″W' , '#c60c30', 1960, 1972  ]
    # Chiefs-Texans
    , ['39°2′56″N 94°29′2″W'   , '#e31837', 1972, np.inf]
    , ['39°5′10″N 94°33′29″W'  , '#e31837', 1963, 1972  ]
    , ['32°46′44″N 96°45′37″W' , '#e31837', 1960, 1962  ] # Cowboys striped in
    # Packers
    , ['44°30′5″N 88°3′44″W'   , '#203731', 1995, np.inf]
    , ['43°45′57″N 88°1′5″W'   , '#203731', 1957, 1994  ] # Between two home stadiums
    , ['43°46′8″N 87°59′0″W'   , '#203731', 1953, 1956  ] # Between two home stadiums
    , ['43°46′38″N 87°58′37″W' , '#203731', 1952, 1952  ] # Between two home stadiums
    , ['43°46′23″N 88°0′40″W'  , '#203731', 1934, 1951  ] # Between two home stadiums
    , ['44°30′27″N 87°59′33″W' , '#203731', 1926, 1933  ]
    , ['44°30′15″N 87°59′2″W'  , '#203731', 1923, 1925  ]
    , ['44°30′25″N 87°59′33″W' , '#203731', 1919, 1922  ]
    # Bears-Staleys
    , ['41°51′44″N 87°37′0″W'  , '#0b162a', 2003, 2033  ]
    , ['40°5′57″N 88°14′9″W'   , '#0b162a', 2002, 2002  ]
    , ['41°51′44″N 87°37′0″W'  , '#0b162a', 1971, 2001  ]
    , ['41°56′53″N 87°39′20″W' , '#0b162a', 1922, 1970  ]
    , ['41°56′53″N 87°39′20″W' , '#94795D', 1921, 1921  ]
    , ['39°50′48″N 88°55′35″W' , '#94795D', 1920, 1920  ]

    # Defunct franchises
    # https://en.wikipedia.org/wiki/List_of_defunct_National_Football_League_franchises
    # Pros and successors
    , ['41°4′30″N 81°29′58″W'  , '#B9975B', 1920, 1926  ]
    # Bulldogs-Maroons
    , ['40°43′6″N 76°20′56″W'  , '#862633', 1925, 1928  ]
    , ['42°21′11″N 71°7′8″W'   , '#862633', 1929, 1929  ]
    # Tigers-Dodgers-Triangles
    , ['39°47′6″N 84°11′59″W'  , '#002D72', 1920, 1929  ]
    , ['40°39′54″N 73°57′29″W' , '#008000', 1930, 1943  ]
    , ['40°39′54″N 73°57′29″W' , '#cc5500', 1944, 1944  ]
    # Horsemen-Lions
    , ['40°39′54″N 73°57′29″W' , '#046A38', 1926, 1926  ]
    # Rangers - Bisons - All-Americans
    , ['42°55′31″N 78°51′10″W' , '#FF6720', 1920, 1923  ] # Home stadium claimed by multiple venues
    , ['42°54′54″N 78°51′43″W' , '#FF6720', 1924, 1927  ]
    , ['42°54′54″N 78°51′43″W' , '#FF6720', 1929, 1929  ]
    # Bulldogs
    , ['40°49′12″N 81°23′53″W' , '#800000', 1920, 1922  ]
    , ['40°49′12″N 81°23′53″W' , '#800000', 1924, 1926  ]
    # Tigers of Chicago
    , ['41°56′53″N 87°39′20″W' , '#FF6720', 1920, 1920  ]
    # Reds
    , ['39°7′0″N 84°32′7″W'    , '#C8102E', 1933, 1934  ]
    # Tigers and successors
    , ['41°30′41″N 81°38′39″W' , '#680817', 1920, 1921  ]
    # Bulldogs and predecessors
    , ['41°30′41″N 81°38′39″W' , '#C8102E', 1923, 1923  ]
    , ['41°30′41″N 81°38′39″W' , '#B00000', 1924, 1925  ]
    , ['41°30′41″N 81°38′39″W' , '#B00000', 1927, 1927  ]
    # Team in Cleveland (1931)
    , ['41°30′24″N 81°41′50″W' , '#E4002B', 1931, 1931  ]
    # Tigers-Heralds
    , ['42°19′55″N 83°4′8″W'   , '#C8102E', 1920, 1920  ]
    , ['42°19′55″N 83°4′8″W'   , '#FF6720', 1921, 1921  ]
    # Panthers of Detroit
    , ['42°19′55″N 83°4′8″W'   , '#F2A900', 1925, 1926  ]
    # Wolverines
    , ['42°24′57″N 83°8′12″W'  , '#8097A9', 1928, 1928  ] # Color is blue and white
    # Eskimos-Kelleys
    , ['46°45′22″N 92°8′45″W'  , '#C8102E', 1923, 1925  ] # Did not play home games in 1926-27
    # Crimson Giants
    , ['37°59′34″N 87°33′44″W' , '#BA0C2F', 1921, 1922  ]
    # Yellow Jackets
    , ['40°1′37″N 75°3′50″W'   , '#F2A900', 1924, 1930  ]
    , ['39°56′50″N 75°9′50″W'  , '#F2A900', 1931, 1931  ] # Between two home stadiums
    # Pros
    , ['41°35′05″N 87°30′01″W' , '#800080', 1923, 1923  ] # Did not play home games in 1920-22
    , ['41°35′05″N 87°30′01″W' , '#800080', 1926, 1926  ] # Did not play home games in 1924-25
    # Blues
    , ['41°46′2″N 72°39′39″W'  , '#6495ED', 1926, 1926  ]
    # Maroons of Kenosha
    , ['42°35′10″N 87°50′36″W' , '#800000', 1924, 1924  ]
    # Colonels-Brecks
    , ['38°14′26″N 85°45′54″W' , '#DBC8B6', 1921, 1923  ] # No home games in 1926
    # Badgers
    , ['43°4′26″N 87°55′14″W'  , '#E35205', 1922, 1925  ]
    , ['43°4′26″N 87°55′14″W'  , '#6F263D', 1926, 1926  ]
    # Red Jackets - Marines
    , ['44°59′14″N 93°15′16″W' , '#C8102E', 1921, 1924  ] # Exact location contested
    , ['44°59′14″N 93°15′16″W' , '#C8102E', 1929, 1929  ] # Exact location contested
    , ['44°56′51″N 93°16′43″W' , '#C8102E', 1930, 1930  ]
    # Flyers
    , ['40°11′36″N 85°23′17″W' , '#EB9599', 1920, 1921  ] # Exact location unknown
    # Texans-Yanks-Bulldogs
    , ['42°20′47″N 71°5′52″W'  , '#4cbb17', 1943, 1948  ] # 1945 one home game in New York ignored
    , ['40°49′37″N 73°55′41″W' , '#C0C0C0', 1950, 1951  ] # 1949 is as stripes
    , ['39°5′10″N 94°33′29″W'  , '#4169e1', 1952, 1952  ]
    # Yankees
    , ['40°49′37″N 73°55′41″W' , '#C8102E', 1927, 1929  ]
    # Giants (owned by Charles Brickley)
    , ['40°39′45″N 73°56′27″W' , '#808080', 1921, 1921  ] # Most common home stadium used
    # Tornadoes
    , ['40°46′10″N 74°12′17″W' , '#E35205', 1929, 1929  ]
    , ['40°46′12″N 74°11′5″W'  , '#E35205', 1930, 1930  ]
    # Steam Roller
    , ['41°51′25″N 71°24′7″W'  , '#E35205', 1925, 1931  ]
    # Tornadoes-Legion
    , ['42°44′30″N 87°48′3″W'  , '#BA0C2F', 1922, 1924  ]
    , ['42°44′30″N 87°48′3″W'  , '#BA0C2F', 1926, 1926  ]
    # Jeffersons
    , ['43°8′5″N 77°54′18″W'   , '#C8102E', 1920, 1922  ]
    , ['43°10′22″N 77°38′4″W'  , '#C8102E', 1923, 1923  ] # No home games 1924-25
    # Independents
    , ['41°29′42″N 90°35′07″W' , '#006747', 1920, 1925  ]
    # All-Stars
    , ['38°39′29″N 90°13′12″W' , '#002D72', 1923, 1923  ]
    # Gunners
    , ['38°39′15″N 90°15′56″W' , '#B31942', 1934, 1934  ] # Between two home stadiums
    # Stapes-Stapletons
    , ['40°37′15″N 74°04′51″W' , '#FFCD00', 1929, 1932  ]
    # Maroons of Toledo
    , ['41°39′56″N 83°34′15″W' , '#600000', 1922, 1922  ] # Color adjusted for differentiation
    , ['41°39′23″N 83°32′10″W' , '#600000', 1923, 1923  ]
    # Oorang Indians
    , ['40°35′19″N 83°07′43″W' , '#F2A900', 1922, 1922  ] # No home games in 1923

    # Traveling teams are not in this list. Shown below for completeness
    # Celts (1921)
    # Tigers-Panhandles (1920-26)
    # Cowboys-Blues (1924-26)
    # Buccaneers of Los Angeles (1926)
    # Kardex (1921)
    # Senators (1921)
]

# Use stripes for a second team in the same home stadium
stripes = [ # year start, year end, from color, to color
      [1975, 1975,   '#0b2265', '#003f2d'] # New York: Giants to Jets
    , [1984, np.inf, '#0b2265', '#003f2d']
    , [1949, 1949,   '#0b2265', '#C0C0C0'] # New York: Giants to Bulldogs
    , [1960, 1960,   '#fed02a', '#0073cf'] # LA: Rams to Chargers
    , [2020, np.inf, '#fed02a', '#0073cf']
    , [1960, 1962,   '#e31837', '#002244'] # Dallas: Texans to Cowboys
    , [1945, 1945,   '#4cbb17', '#cc5500'] # Boston: Yanks to Tigers
    , [1943, 1943,   '#FFB612', '#004c54'] # Pittsburgh and Philadelphia: Steelers to Eagles
    , [1944, 1944,   '#FFB612', '#97233f'] # Pittsburgh and Chicago: Steelers to Cardinals
]

# Convert from coordinates as entered to floats
delims = ['°', '′', '″']
divisors = [1., 60., 3600.]

for i in stadia_alltime:
    if i[0].__contains__(delims[0]):
        lat = 0
        for j in range(len(delims)):
            if j == 0:
                start = 0
            else:
                start = i[0].find(delims[j - 1]) + 1
            lat += float(i[0][start : i[0].find(delims[j])]) / divisors[j]
        i.insert(1, lat)

        long = 0
        for j in range(len(delims)):
            if j == 0:
                start = i[0].find(' ') + 1
            else:
                start = i[0].rfind(delims[j - 1]) + 1
            long += float(i[0][start : i[0].rfind(delims[j])]) / divisors[j]
        i.insert(2, long * -1) # Western hemisphere is negative in decimal

    elif i[0].__contains__(', -'):
        i.insert(1, float(i[0][ : i[0].find(',')])) # lat
        i.insert(2, float(i[0][i[0].find(' ') + 1 : ])) # long

    else:
        raise Exception ('Please reformat: {}'.format(i))


# Use a scatter plot to show closest team to everywhere in the US
# Pros: don't have to draw lines or fit things to mercator projections
# Cons: very time and resource intensive and some dots are outside the US

# Get points to check closest team
# http://download.geonames.org/export/dump/US.zip accessed on Oct 11 2021
us_coords = pd.read_csv('US_Coords\\US.txt'
                        , sep = '\t'
                        , names = [
                            'geonameid'
                            , 'name'
                            , 'asciiname'
                            , 'alternatenames'
                            , 'latitude'
                            , 'longitude'
                            , 'feature class'
                            , 'feature code'
                            , 'country code'
                            , 'cc2'
                            , 'admin1 code'
                            , 'admin2 code'
                            , 'admin3 code'
                            , 'admin4 code'
                            , 'population'
                            , 'elevation'
                            , 'dem'
                            , 'timezone'
                            , 'modification date'
                          ]
                       )

# Set up plot space as coordinates containing continental US
BBox = (-124.7844079, -66.9513812
        , 24.7433195, 49.3457868)

df_points = us_coords[['latitude', 'longitude']].sample(frac = 1, random_state = 1)
# Sample for faster rendering
# frac = 1 means no sample, for better picture


for yr in range(1920, 2022): # may have to do in segments to stay within RAM limits
    stadia_this_year = [i for i in stadia_alltime if i[4] <= yr and i[5] >= yr]
    print('\n', yr)
    # print an alert for changes
    for team in stadia_this_year:
         if yr == team[4]:
            fore_fromhex('New stadium: ' + team[0], team[3])

    # get the closest stadium for every geographic point this year
    closest_team = []
    for index, here in df_points.iterrows(): # better ways than iterrows
        min_dist = np.inf
        team_color = ''
        for ls_stadium in stadia_this_year:
            # Meas distances based on pythagorean theorem. There are better ways
            dist = math.sqrt(
                (here[1] - ls_stadium[2])**2
                + (here[0] - ls_stadium[1])**2
                # lon^2 + lat^2
            )
            if dist < min_dist:
                min_dist = dist
                team_color = ls_stadium[3] # color for now instead
        closest_team.append(team_color)

    df_points['closest_team'] = closest_team

    for i in stripes:
        if yr >= i[0] and yr <= i[1]:
            print('STRIPES TRIGGERED')
            i_stripes = df_points[df_points['closest_team'] == i[2]]

            # Remove diagonal swathes from whole eligible area
            i_stripes = i_stripes[
                round(i_stripes['latitude'] + i_stripes['longitude'], 0)
                % 2
                == 0
            ]

            i_stripes['closest_team'] = i[3]
            df_points.update(i_stripes)

    ''' Kinda neat if you want to just see where the color changes
    # Print a map of changes
    if not first_loop:
        df_changes = df_points[df_points['closest_team'] != old_closest]
        if len(df_changes.index) == 0:
            print('No changes')
        else:
            print('CHANGES MAP TRIGGERED')
            fig, axs = plt.subplots(figsize = (24, 16))
            axs.scatter(df_changes['longitude']
                       , df_changes['latitude']
                       , zorder = 1
                       , alpha = 0.15
                       , c = df_changes['closest_team'] # could map to color if 'closest_team' generalized
                       , s = 10
                      )
            axs.set_title('Changes in ' + str(yr))
            axs.set_xlim(BBox[0], BBox[1])
            axs.set_ylim(BBox[2], BBox[3])
            axs.set_yscale('linear')
            plt.xticks([])
            plt.yticks([])
            plt.savefig(os.path.join(output_path, str(yr) + ' NFL cities change map.png')
                        , transparent = True
                       )
            plt.show()

        # testing why changes never show
        # break
    '''

    if yr <= 1921:
        league = 'APFA'
    elif 1960 <= yr <= 1969:
        league = 'NFL or AFL '
    else:
        league = 'NFL'

    # Show a full map
    fig, axs = plt.subplots(figsize = (24, 16))
    axs.scatter(df_points['longitude']
               , df_points['latitude']
               , zorder = 1
               , alpha = 0.15 # With the data used, there are some errant points that are nice to transparent out
               , c = df_points['closest_team'] # could map to color if 'closest_team' generalized
               , s = 10
              )
    axs.set_title('Closest NFL ' + is_afl + 'team ' + str(yr))
    axs.set_xlim(BBox[0], BBox[1])
    axs.set_ylim(BBox[2], BBox[3])
    axs.set_yscale('linear')

    # TODO: fix
    #     # Add dots for stadiums
    #     plt.scatter(
    #           stadia_this_year[:][2] # west
    #         , stadia_this_year[:][1] # north
    #         , zorder = 1
    #         , alpha = 1
    #         , c = 'black'
    #         , s = 10
    #     )

    plt.xticks([]) # Look like a picture, not a scatter plot
    plt.yticks([])
    plt.savefig(os.path.join(output_path, str(yr) + ' NFL cities full map.png')
                , transparent = True
               )
    # plt.show()

    '''
    # REALLY not getting why this isn't different from the next year's closest team
    old_closest = df_points['closest_team']

    # Curious if there is a consensus style here. Could always set first_loop = False
    if first_loop:
        first_loop = False
    '''


def make_gif(frame_folder):
    frames = [Image.open(image) for image in glob.glob(f"{frame_folder}\\*.PNG")]
    frame_one = frames[0]
    frame_one.save(
          "Closest NFL City.gif"
        , format = "GIF"
        , append_images = frames
        , save_all = True
        , duration = 588 # 1 minute runtime for 102 frames
        , loop = 0 # Infinite
    )

make_gif("C:\\Users\\Admin\\Desktop\\NFL gif")


'''
# TODO: Integrate with this visibile on top of full color map
# Plot layer with just points for stadium location
for yr in [1955, 2019, 2020, 2021]:
    stadia_this_year = pd.DataFrame(
        [i for i in stadia_alltime if i[4] <= yr and i[5] >= yr]
    )

    fig, axs = plt.subplots(figsize = (24, 16))
    plt.scatter(stadia_this_year[:][2] # west
                   , stadia_this_year[:][1] # north
                   , zorder = 1
                   , alpha = 1
                   , c = 'black'
                   , s = 10
               )

    axs.set_title('NFL Cities')
    axs.set_xlim(BBox[0], BBox[1])
    axs.set_ylim(BBox[2], BBox[3])
    axs.set_yscale('linear')

    plt.show()
'''
