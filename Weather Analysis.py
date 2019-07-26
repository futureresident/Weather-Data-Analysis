from os import walk
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import basemap
import re


def load_station_info(directory='./data/'):
    """
    Loads information about each weather station and stores it in a nested dictionary.
    :param directory: Directory (folder) containing the station information file.
    :return: A nested dictionary STATION ID -> dict of STATION INFO
    """
    temp_station_file = open(directory + 'Temperature_Stations.csv', 'r')
    temp_station_lines = temp_station_file.readlines()[4:]
    temp_station_dict = dict()
    for line in temp_station_lines:
        line = re.sub(r'[^a-zA-Z0-9.,-]+', '', line)
        line = line.strip().split(',')
        prov = line[0]
        station_name = line[1]
        station_id = line[2]
        begin_year = int(line[3])
        begin_month = int(line[4])
        end_year = int(line[5])
        end_month = int(line[6])
        lat = float(line[7])
        lon = float(line[8])
        elev = int(line[9])
        joined = line[10]

        temp_station_dict[station_id] = {'prov': prov, 'station_name': station_name, 'station_id': station_id,
                                         'begin_year': begin_year, 'begin_month': begin_month, 'end_year': end_year,
                                         'end_month': end_month,
                                         'lat': lat, 'lon': lon, 'elev': elev, 'joined': joined}

    return temp_station_dict

# station_info_dict

def load_temperature_data(directory='./data/'):
    """
    Loads temperature data from all files into a nested dict with station_id as top level keys.
    Data for each station is then stored as a dict: YEAR -> list of monthly mean temperatures.
    NOTE: Missing data is not handled gracefully - it is simply ignored.
    :param directory: Directory containing the temperature data files.
    :return: A nested dictionary STATION ID -> YEAR -> LIST OF TEMPERATURES
    """
    all_stations_temp_dict = dict()
    for _, _, files in walk(directory):
        for file_name in files:
            if file_name.startswith('mm'):
                station_temp_dict = dict()
                file = open(directory + file_name, 'r')
                station_id = file.readline().strip().split(',')[0]
                file.seek(0)
                file_lines = file.readlines()[4:]
                for line in file_lines:
                    line = re.sub(r'[^a-zA-Z0-9.,-]+', '', line)
                    line = line.strip().split(',')
                    year = int(line[0])
                    monthly_temperatures = []
                    for i in range(1, 24, 2):
                        value = float(line[i])
                        if value > -100:
                            monthly_temperatures.append(value)
                    station_temp_dict[year] = monthly_temperatures
                all_stations_temp_dict[station_id] = station_temp_dict
    return all_stations_temp_dict

# temperature_data_dict


def draw_map(plot_title, data_dict):
    """
    Draws a map of North America with temperature station names and values. Positive values are drawn next to red dots
    and negative values next to blue dots. The location of values are determined by the latitude and longitude. A
    dictionary (data_dict) is used to provide a map from station_name names to a tuple containing the (latitude, longitude, value)
    used for drawing.
    :param plot_title: Title for the plot.
    :param data_dict: A dictionary STATION NAME -> tuple(LATITUDE, LONGITUDE, VALUE)
    """
    fig = plt.figure(figsize=(9, 9))
    map1 = Basemap(projection='lcc', resolution=None, width=8E6, height=8E6, lat_0=53, lon_0=-97, )
    map1.etopo(scale=0.5, alpha=0.5)

    for station_name_name in data_dict:
        data = data_dict[station_name_name]
        print(station_name_name, data)
        x, y = map1(data[1], data[0])
        value = data[2]
        color = 'black'
        if value < 0:
            color = 'blue'
        elif value > 0:
            color = 'red'
        plt.plot(x, y, 'ok', markersize=2, color=color)
        plt.text(x, y, '{}\n {:.2f}℃'.format(station_name_name, value), fontsize=8)
    plt.title(plot_title)
    plt.show()


def make_station_name_dict(station_names, station_info_dict):
    """
    Makes a dictionary mapping station names to station ids.
    :param station_names: A list of station names. Station names must be in data file.
    :param station_info_dict: A dictionary STATION ID -> dict of STATION INFO
    :return: A dictionary STATION NAME -> STATION ID.
    """
    station_names_dict = dict()
    for name in station_names:
        for station_id in station_info_dict:
            station_details = station_info_dict[station_id]
            station_name = station_details['station_name']
            if station_name.lower() == name.lower():
                station_id = station_details['station_id']
                station_names_dict[name] = station_id
    return station_names_dict




def get_temperatures_for_year(station_name, year, station_name_dict, temperature_data_dict):
    """
    Given a station name and a year, use the two data dictionaries together to return a list of
    the station's temperature data for the year.

    HINT: station_name is a valid key for station_name_dict. What are temperature_data_dict's keys?

    :param station_name: The station name as a string.
    :param year: A year as an integer.
    :param station_name_dict: Dictionary mapping STATION NAME -> STATION ID
    :param temperature_data_dict: Dictionary mapping STATION NAME -> YEAR -> LIST OF TEMPERATURES
    :return: A list of temperatures.
    """

    # Stores the given station name as a list in order for it to be used in the make_station_dict function
    name = [station_name]
    # Stores the dictionary of the given station that is mapped to its station ID, into a variable
    station_name_dict = make_station_name_dict(name, station_data)
    # Stores the list of temperatures for the given year, obtained from the station id of the given station name, in a variable.
    temperatures = temperature_data_dict[station_name_dict[station_name]][year]
    return temperatures



def get_station_coordinates(station_name, station_name_dict, station_data):
    """
    Given a station_name, find its station_id using station_name_dict. Then use the station_id
    to find and return the station_name's coordinates (longitude and latitute) using station_data.
    Return the coordinates as a tuple (latidude, longitude).

    :param station_name: The station name as a string.
    :param station_name_dict: Dictionary mapping STATION NAME -> STATION ID
    :param station_data: Dictionary mapping STATION ID -> dict of STATION INFO
    :return: A tuple (longitude, latitude)
    """

    # Stores the given station name as a list in order for it to be used in the make_station_dict function
    name = [station_name]
    # Stores the dictionary of the given station that is mapped to its station ID, into a variable
    station_name_dict = make_station_name_dict(name, station_data)
    # Stores the latitude of the station of interest based on its station ID in a variable
    lat = station_data[station_name_dict[station_name]]['lat']
    # Stores the longitude of the station of interest based on its station ID in a variable
    lon = station_data[station_name_dict[station_name]]['lon']
    # Returns the latitude and longitude as a tuple
    return (lat, lon)

def compute_average_temp(temperatures):
    """
    Compute the average of a list of temperatures.
    :param temperatures: A list of temperature values.
    :return: Their average.
    """
    return np.mean(temperatures)

def compute_average_change(temperatures):
    """
    Compute the average CHANGE over a list of temperatures. For example,
    if temperatures is [0, 1, 2, 3, 4], this function should return 1.0.
    If annual_temperatures is [2, 1.5, 1, 0.5, 0], this function should return -0.5
    :param temperatures: A list of temperature values.
    :return: The average change of these values.
    """
    # This is a list initialized that will contain a list of differences between each consecutive temperature values
    sub_average_list = []
    # A counter variable for indexing
    i = 0
    # This for loop will iterate over every temperature in the list. The if statement will ensure that the for loop doesn't exceed the length of the list of temperatures
    for temp in temperatures:
        if i+1 < len(temperatures):
            # This will obtain the difference between the first two temperature values
            sub_average = temperatures[i+1] - temperatures[i]
            # This will append the difference to the list initialized earlier
            sub_average_list.append(sub_average)
        i += 1
    # Returns the average of the differences of the temperature values
    return np.mean(sub_average_list)

def make_average_change_dict(station_names, station_name_dict, temperature_data_dict, start_year, end_year):
    """
    Create a dictionary that maps STATION NAMES to the AVERAGE CHANGE IN TEMPERATURE over the period
    from start_year (inclusive) to end_year (exclusive). For example, the average change
    over 5 years of temperatures can be computed first by computing the average temperature for each of the 5 years,
    and then computing the average change over those average temperatures.

    HINT: The challenge for this function is to create a dictionary with the right keys and values. You need to
    correctly use the previous two functions (compute_average_temp and compute_average_change) to compute the 'value'
    part of the dictionary.

    :param station_names: A list of station names as strings.
    :param station_name_dict: Dictionary mapping STATION NAME -> STATION ID
    :param temperature_data_dict: Dictionary mapping STATION NAME -> YEAR -> LIST OF TEMPERATURES
    :param start_year: Start year, as integer, inclusive, for years in analysis.
    :param end_year: End year, as integer, exclusive, for years in analysis.
    :return: Dictionary mapping STATION NAME -> AVERAGE TEMPERATURE CHANGE BETWEEN START_YEAR AND END_YEAR (float)
    """
    # Initiates a dictionary  to be used later
    average_change_dict = {}
    # For loop that iterates first over the list of station names
    for station_name in station_names:
        # Initiates a list to include the the average temperature of years for each station
        sub_average_list = []
        # For loop that then iterates over every year in the range of years given, for every station.
        for year in list(range(start_year, end_year)):
            # Computes the average temp for every year indicated by the range
            sub_average = compute_average_temp(temperature_data_dict[station_name_dict[station_name]][year])
            # Appends to the list initiated earlier
            sub_average_list.append(sub_average)
        # Computes average change over the average temps, and stores it in a key in the dictionary initiated earlier
        average_change_dict[station_name] = compute_average_change(sub_average_list)
    # Returns a dictionary mapping each station to its average change in temperature in the range of values given
    return average_change_dict


def make_average_change_dict_for_map(station_names, station_name_dict, station_data, temperature_data_dict, start_year, end_year):
    """
    Create a dictionary mapping STATION NAMES to tuples(LATITUDE, LONGITUDE, AVERAGE TEMP CHANGE) over the range from
    start_year (inclusive) to end_year (exclusive).

    :param station_names: A list of station names as strings.
    :param station_name_dict: Dictionary mapping STATION NAME -> STATION ID
    :param station_data: Dictionary mapping STATION ID -> dict of STATION INFO
    :param temperature_data_dict: Dictionary mapping STATION NAME -> YEAR -> LIST OF TEMPERATURES
    :param start_year: Start year, as integer, inclusive, for years in analysis.
    :param end_year: End year, as integer, exclusive, for years in analysis.
    :return: A dictionary STATION NAME -> (LATITUDE, LONGITUDE, AVERAGE TEMP CHANGE)
    """

    # Initiates a dictionary that will be used later on
    dict_for_map = {}
    # Creates a dictionary using the previous function and stores in a variable to be used later for indexing
    average_change_dict = make_average_change_dict(station_names, station_name_dict, temperature_data_dict, start_year, end_year)
    # A for loop that iterates over each name in the list of names given
    for station_name in station_names:
        # Obtains the the coordinates of each station and stores it in coord
        coord = get_station_coordinates(station_name, station_name_dict, station_data)
        # stores the average change of temperatures over the provided years in a tuple
        average_change = (average_change_dict[station_name], )
        # Creates a new tuple that includes the coordinates as well as the average change over the years
        final_tuple = coord + average_change
        # Maps the station to the tuple created to make the dictionary
        dict_for_map[station_name] = final_tuple
    # Returns the dictionary mapping stations to station coordinates as well as average change over the years provided
    return dict_for_map

def draw_avg_change_map(station_names, station_name_dict, station_data, temperature_data_dict, start_year, end_year):
    """
    Given the various data structure parameters together with a start_year (inclusive) and end_year (exclusive),
    create an 'average change dictionary' (use the function make_average_change_dict_for_map) that will be used
    in a call to the draw_map function. You also need a plot title to call this function, so make a string that
    uses start_year and end_year to create an appropriate title, e.g 'Average Annual Temperature Change Between 1990
    and 1999.
    :param station_names: A list of station names as strings.
    :param station_name_dict: Dictionary mapping STATION NAME -> STATION ID
    :param station_data: Dictionary mapping STATION ID -> dict of STATION INFO
    :param temperature_data_dict: Dictionary mapping STATION NAME -> YEAR -> LIST OF TEMPERATURES
    :param start_year: Start year, as integer, inclusive, for years in analysis.
    :param end_year: end_year: End year, as integer, exclusive, for years in analysis.
    :return: No return statement.
    """
    # Creates a dictionary using a previous function and stores in a variable that will be used as a parameter
    avg_change_dict = make_average_change_dict_for_map(station_names, station_name_dict, station_data, temperature_data_dict, start_year, end_year)
    # Draws a map with a title that plots stations in their locations based on coordinates and indicates their average change of temperature over the range of years provided
    draw_map(("Average Annual Temperature Change Between {} and {}").format(start_year, end_year - 1), avg_change_dict)



def draw_maps_by_range(station_names, station_name_dict, station_data, temperature_data_dict, start_year, years_per_map, n):
    """
    Given the various data structure parameters, a start_year (inclusive, integer), years_per_map (integer), and n (integer),
    draw n maps, each showing the average change in temperature over years_per_map. For example, calling
    draw_maps_by_range(station_names, station_name_dict, station_data, temperature_data, 1950, 10, 2) will draw two maps,
    one with data from 1950 to 1959, and the other from 1960 to 1969.

    HINT: You can use a loop here to draw the maps!

    :param station_names: A list of station names as strings
    :param station_name_dict: Dictionary mapping STATION NAME -> STATION ID
    :param station_data: Dictionary mapping STATION ID -> dict of STATION INFO
    :param temperature_data_dict: Dictionary mapping STATION NAME -> YEAR -> LIST OF TEMPERATURES
    :param start_year: Start year, as integer, inclusive, for years in analysis.
    :param years_per_map: Number of years to be analyzed per map
    :param n: Number of maps to be drawn
    :return: No return statement.
    """

    # This will ensure that the end year will be after whatever is indicated by years_per_map
    end_year = start_year + years_per_map
    # A for loop to iterate over the number 'n' that will draw maps that many times
    for i in range(n):
        # Draws the map using given parameters
        draw_avg_change_map(station_names, station_name_dict, station_data, temperature_data_dict, start_year, end_year)
        # Now changes start_year to the next segment after years_per_map
        start_year = start_year + years_per_map
        # And this changes the end year to years_per_map past the previous end year
        end_year = end_year + years_per_map




# # Nested dict of station details.
station_data = load_station_info()

# # Nested dict of temperature data.
temperature_data_dict = load_temperature_data()

# # A list of selected station names from across Canada with temperature records.
 # Try using different station names - but make sure they're part of the data set!
station_names = ['Vancouver', 'Whitehorse', 'Yellowknife', 'Iqaluit', 'Calgary',
                 'Regina', 'Winnipeg', 'London', 'Quebec', 'Halifax', 'Gander']

# # Dict mapping station_name names to their station ids.
station_name_dict = make_station_name_dict(station_names, station_data)

# # Draw multiple temperature change maps. This call should result in two maps being drawn:
# # one for years 1950 to 1959, and the other from 1960 to 1969.
draw_maps_by_range(station_names, station_name_dict, station_data, temperature_data_dict, 1950, 10, 2)
