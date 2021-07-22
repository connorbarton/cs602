"""
Name: Connor Aulson
CS602: Section SN2
Data: NYC Collisions
Streamlit URL: https://share.streamlit.io/connorbarton/cs602/main/P5_aulson_conn.py
Github URL: https://github.com/connorbarton/cs602/blob/main/P5_aulson_conn.py
Description: This program utilizes NYC vehicular crash data and answers the following three queries:
1) How many vehicular crashes have there been relative to my location? [Geo Map]
2) How often are people injured or killed based on different collision reasons? [Pie Charts]
3) What is the most common time of day where certain crashes occur? [Heat Map]
"""

import pandas as pd
import streamlit as st
import requests
import urllib.parse
import geopy.distance
import pydeck as pdk
import matplotlib.pyplot as plt
import collections
import seaborn as sns
import random


# function to generate unique colors for my visuals throughout program
def get_color():
    r, g, b = random.random(), random.random(), random.random()
    color = (r, g, b)
    return color


# this function queries the 'Nominatim' service which in turn queries the 'Open Street Map' database to obtain
# the latitude and longitude of the location
def get_coordinates(street, city, state, country):
    address = str(f'{street}, {city}, {state}, {country}')
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) + '?format=json'
    response = requests.get(url).json()
    lat = float(response[0]["lat"])
    lon = float(response[0]["lon"])
    return lat, lon


# get the distance in miles between two coordinates using the geopy.distance module
def get_distance(coordinates1, coordinates2):
    distance = geopy.distance.distance(coordinates1, coordinates2).miles
    return distance


# map the coordinates of the input location and the closest store with matching amenities preferences using pydeck
def map_collisions(coordinates, filtered_data, map_style):
    location_layer = pdk.Layer(
        'ScatterplotLayer',
        data=[[coordinates[1], coordinates[0]]],
        get_position='-',
        get_color='[0, 64, 225]',
        get_radius=25,
        radius_min_pixels=5)
    collisions_layer = pdk.Layer(
        'ScatterplotLayer',
        filtered_data,
        get_position=['LONGITUDE', 'LATITUDE'],
        get_color='[180, 0, 200, 140]',
        get_radius=25,
        radius_min_pixels=5,
        get_fill_color='[180, 0, 200, 140]',
        pickable=True)
    view_state = pdk.ViewState(
        longitude=coordinates[1],
        latitude=coordinates[0],
        zoom=15,
        min_zoom=12,
        max_zoom=20,
        pitch=10,
        pickable=True)
    st.pydeck_chart(pdk.Deck(
        map_style=map_style,
        initial_view_state=view_state,
        layers=[location_layer, collisions_layer]))


# produce a variety of pie charts using matplotlib
def pie_charts(factor, vehicle, factor_filtered_data, vehicle_filtered_data):
    # pie chart 1
    st.markdown(f"This pie chart shows the proportion of instances where a collision resulting from {factor} left people unharmed, injured, or dead")
    first_title = f"Impact of Collisions Resulting from {factor.title()}"
    fig1 = plt.figure(1, figsize=(4, 4))
    # determine total hours of data so I can add the percentages while counting weather condition instances
    total_rows1 = factor_filtered_data.shape[0]
    # create a dictionary of each collision outcome and add the percentages associated with those outcomes
    results_dict = {'UNHARMED': 0, 'INJURED': 0, 'DEAD': 0}
    for index, row in factor_filtered_data.iterrows():
        if row['INJURIES'] == 0 and row['DEATHS'] == 0:
            results_dict['UNHARMED'] += 1 / total_rows1
        elif row['INJURIES'] != 0 and row['DEATHS'] == 0:
            results_dict['INJURED'] += 1 / total_rows1
        else:
            results_dict['DEAD'] += 1 / total_rows1
    # processing info from previously made dictionary to prep for plotting
    # also obtain unique wedge colors and determine largest wedge to explode
    results_list = []
    frequency_list = []
    wedge_list = []
    colors_list = []
    size = 0
    count = -1
    for k, v in results_dict.items():
        results_list.append(k.title())
        frequency_list.append(v)
        wedge_list.append(0)
        colors_list.append(get_color())
        count += 1
        if v >= size:
            size = v
            big_wedge_spot = count
    wedge_list[big_wedge_spot] = 0.1
    plt.pie(frequency_list, labels=results_list, explode=wedge_list, autopct='%1.1f%%', shadow=True, colors=colors_list, radius=1.2)
    plt.title(first_title)
    st.pyplot(fig1)

    # pie chart 2
    st.markdown(f"This pie chart shows the proportion of instances where a collision involving {vehicle} vehicles left people unharmed, injured, or dead")
    second_title = f"Impact of Collisions Involving {vehicle.title()}"
    fig2 = plt.figure(2, figsize=(4, 4))
    # determine total hours of data so I can add the percentages while counting weather condition instances
    total_rows2 = vehicle_filtered_data.shape[0]
    # create a dictionary of each collision outcome and add the percentages associated with those outcomes
    results_dict = {'UNHARMED': 0, 'INJURED': 0, 'DEAD': 0}
    for index, row in vehicle_filtered_data.iterrows():
        if row['INJURIES'] == 0 and row['DEATHS'] == 0:
            results_dict['UNHARMED'] += 1 / total_rows2
        elif row['INJURIES'] != 0 and row['DEATHS'] == 0:
            results_dict['INJURED'] += 1 / total_rows2
        else:
            results_dict['DEAD'] += 1 / total_rows2
    # processing info from previously made dictionary to prep for plotting
    # also obtain unique wedge colors and determine largest wedge to explode
    results_list = []
    frequency_list = []
    wedge_list = []
    colors_list = []
    size = 0
    count = -1
    for k, v in results_dict.items():
        results_list.append(k.title())
        frequency_list.append(v)
        wedge_list.append(0)
        colors_list.append(get_color())
        count += 1
        if v >= size:
            size = v
            big_wedge_spot = count
    wedge_list[big_wedge_spot] = 0.1
    plt.pie(frequency_list, labels=results_list, explode=wedge_list, autopct='%1.1f%%', shadow=True, colors=colors_list, radius=1.2)
    plt.title(second_title)
    st.pyplot(fig2)

    # pie chart 3
    st.markdown(f"For collisions due to {factor}, this pie chart shows the proportion of vehicle types involved")
    third_title = f"Vehicle Types as a Proportion of Collisions from {factor.title()}"
    fig3 = plt.figure(3, figsize=(10, 4))
    # determine total hours of data so I can add the percentages while counting weather condition instances
    total_rows3 = factor_filtered_data.shape[0]
    # create a dictionary of each collision outcome and add the percentages associated with those outcomes
    vehicles_dict = {}
    for index, row in factor_filtered_data.iterrows():
        if row['VEHICLE 1 TYPE'] not in vehicles_dict:
            vehicles_dict[row['VEHICLE 1 TYPE']] = 1 / total_rows3
        else:
            vehicles_dict[row['VEHICLE 1 TYPE']] += 1 / total_rows3
    # processing info from previously made dictionary to prep for plotting
    # also obtain unique wedge colors and determine largest wedge to explode
    vehicles_list = []
    frequency_list = []
    wedge_list = []
    colors_list = []
    size = 0
    count = -1
    for k, v in vehicles_dict.items():
        vehicles_list.append(k.title())
        frequency_list.append(v)
        wedge_list.append(0)
        colors_list.append(get_color())
        count += 1
        if v >= size:
            size = v
            big_wedge_spot = count
    wedge_list[big_wedge_spot] = 0.1
    plt.pie(frequency_list, explode=wedge_list, autopct='%1.1f%%', colors=colors_list, radius=1.2)
    plt.legend(vehicles_list, loc='best', prop={'size': 4})
    plt.title(third_title)
    st.pyplot(fig3)

    # pie chart 4
    st.markdown(f"For collisions involving {vehicle} vehicles, this pie chart shows the proportion of factors behind the collision")
    fourth_title = f"Factors as a Proportion of Collisions involving {vehicle.title()}"
    fig4 = plt.figure(4, figsize=(4, 10))
    # determine total hours of data so I can add the percentages while counting weather condition instances
    total_rows4 = vehicle_filtered_data.shape[0]
    # create a dictionary of each collision outcome and add the percentages associated with those outcomes
    factors_dict = {}
    for index, row in vehicle_filtered_data.iterrows():
        if row['VEHICLE 1 FACTOR'] not in factors_dict:
            factors_dict[row['VEHICLE 1 FACTOR']] = 1 / total_rows4
        else:
            factors_dict[row['VEHICLE 1 FACTOR']] += 1 / total_rows4
    # processing info from previously made dictionary to prep for plotting
    # also obtain unique wedge colors and determine largest wedge to explode
    factors_list = []
    frequency_list = []
    wedge_list = []
    colors_list = []
    size = 0
    count = -1
    for k, v in factors_dict.items():
        factors_list.append(k.title())
        frequency_list.append(v)
        wedge_list.append(0)
        colors_list.append(get_color())
        count += 1
        if v >= size:
            size = v
            big_wedge_spot = count
    wedge_list[big_wedge_spot] = 0.1
    plt.pie(frequency_list, explode=wedge_list, autopct='%1.1f%%', colors=colors_list, radius=1.2)
    plt.legend(factors_list, loc='best', prop={'size': 4})
    plt.tight_layout()
    plt.title(fourth_title)
    st.pyplot(fig4)


# create a heat map with Seaborn
def heat_map(title, filtered_data, color):
    # create dictionary where the keys are the factors that caused the collisions
    dict = {"index": ["Before 6:00 AM", "6:00 AM - 12:00 PM", "12:00 PM - 6:00 PM", "After - 6:00 PM"]}
    for index, row in filtered_data.iterrows():
        if row["VEHICLE 1 FACTOR"].title() not in dict:
            dict[row["VEHICLE 1 FACTOR"].title()] = [0, 0, 0, 0]

    # determine proportions of collisions occurring within each timeframe and append values to the list in the dictionary
    total_rows = filtered_data.shape[0]
    for index, row in filtered_data.iterrows():
        time = row["TIME"].split(":")
        hour = int(time[0])
        if hour < 6:
            dict[row["VEHICLE 1 FACTOR"].title()][0] += 1 / total_rows * 100
        elif 6 <= hour < 12:
            dict[row["VEHICLE 1 FACTOR"].title()][1] += 1 / total_rows * 100
        elif 12 <= hour < 18:
            dict[row["VEHICLE 1 FACTOR"].title()][2] += 1 / total_rows * 100
        else:
            dict[row["VEHICLE 1 FACTOR"].title()][3] += 1 / total_rows * 100

    sorted_dict = collections.OrderedDict(sorted(dict.items()))

    df = pd.DataFrame.from_dict(sorted_dict)
    df.set_index("index", drop=True, inplace=True)

    # plotting the visual
    fig = plt.figure()
    ax1 = fig.add_axes([1, 1, 2, 1])
    ax = sns.heatmap(df, vmin=0, vmax=2, linewidths=0.1, linecolor=get_color(), cmap=color, xticklabels=True, ax=ax1)
    ax.set_xlabel("Collision Factor")
    ax.set_ylabel("Time of Day")
    ax.set_title(title)
    st.markdown(f"Below is a heat map that highlights the time of day of collisions resulting from various factors occurred:")
    st.pyplot(fig)
    # include table of dataframe for more details
    st.markdown(f"Here is a table that shows more details about the percentages of all collisions that occur at a given time of day:")
    st.write(df)


def main():
    # read the NYC collision dataset csv file
    file = pd.read_csv('nyc_veh_crash_sample.csv')

    # establish program title and short description
    st.sidebar.title(f"NYC Collisions Program")

    page_list = ["Home Page", "Collisions near a location", "Collision factors and vehicle types", "Collisions based on time of day"]
    page = st.sidebar.selectbox("Choose your page!", page_list, 0)

    if page == page_list[0]:
        st.title(f"NYC Collisions Program - Home Page")
        st.markdown(f"Use the sidebar to select a page to navigate to!")
        st.markdown("==================================================================")
        st.markdown("This project analyzes vehicle collision data from NYC.  I hope you enjoy the program!")

    elif page == page_list[1]:
        collision_data = file
        st.title(f"{page_list[1].title()}")
        st.sidebar.markdown(f"Enter NYC address and specify a proximity to view all the collisions within the parameters!")

        # create fields for user's location, set default as 1 Wall Street
        street = st.sidebar.text_input("Address", "1 Wall St")
        city, state, country = "New York City", "New York", "United States"

        # create a slider for the user to select the proximity, set default as 5 miles
        proximity = st.sidebar.slider("Proximity (miles)", 0.1, 5.0, step=0.1, value=2.5)

        # determine the map style
        map_style_list = ['No Preference', 'Light Style', 'Dark Style', 'Satellite Style']
        map_options = ['mapbox://styles/mapbox/light-v9', 'mapbox://styles/mapbox/dark-v9', 'mapbox://styles/mapbox/satellite-v9']
        map_pick = st.sidebar.selectbox("What map style would you like?", map_style_list, 0)
        if map_pick == map_style_list[1]:
            map_style = map_options[0]
        elif map_pick == map_style_list[2]:
            map_style = map_options[1]
        elif map_pick == map_style_list[3]:
            map_style = map_options[2]
        else:
            pick = random.randint(0, 2)
            map_style = map_options[pick]

        # get lat and lon coordinates for inputted location
        coordinates = get_coordinates(street, city, state, country)

        # remove rows from dataset that are missing lon/lat data
        collision_data = collision_data[collision_data['LOCATION'].notna()]

        # create a list of distances between location and collision
        distances = []
        for index, row in collision_data.iterrows():
            distances.append(get_distance(coordinates, (float(row['LATITUDE']), float(row['LONGITUDE']))))

        # create a column in the dataframe for the distance the collision is away from the location
        collision_data['MILES AWAY'] = distances

        # only keep info from collisions within proximity
        within_proximity = collision_data.loc[collision_data['MILES AWAY'] <= proximity]

        # order the collisions from the filtered data by their proximity to the location
        filtered_data = within_proximity.nsmallest(n=len(within_proximity), columns='MILES AWAY')
        filtered_data = filtered_data.fillna("UNSPECIFIED")

        # initiate header and produce map
        st.markdown(f"Here is a map to show the collisions exact locations!")
        map_collisions(coordinates, filtered_data, map_style)

        # initiate header and write table of filtered dataframe with a few fields
        st.markdown(f"Here is what is found for collisions within {proximity} miles of {street}:")
        st.write(pd.DataFrame(filtered_data[['MILES AWAY', 'DATE', 'TIME', 'BOROUGH', 'VEHICLE 1 FACTOR', 'VEHICLE 1 TYPE', 'VEHICLE 2 TYPE']]))

    elif page == page_list[2]:
        collision_data = file
        collision_data = collision_data.fillna("UNSPECIFIED")
        st.title(f"{page_list[2].title()}")

        # create two columns in the dataframe for the total people injured/killed from collision, and configure factors selectbox options
        injuries = []
        deaths = []
        for index, row in collision_data.iterrows():
            injuries.append(row[11]+row[13]+row[15]+row[17])
            deaths.append(row[12]+row[14]+row[16]+row[18])
        collision_data['INJURIES'] = injuries
        collision_data['DEATHS'] = deaths

        # determine various variables/options for user to choose via selectbox
        factors_options = ['All factors']
        vehicle_options = ['All vehicles']
        for index, row in collision_data.iterrows():
            if row['VEHICLE 1 FACTOR'].title() not in factors_options:
                factors_options.append(row['VEHICLE 1 FACTOR'].title())
            if row['VEHICLE 1 TYPE'].title() not in vehicle_options:
                vehicle_options.append(row['VEHICLE 1 TYPE'].title())
        factor = st.sidebar.selectbox("Select a collision factor to view data for:", sorted(factors_options), 3)
        vehicle = st.sidebar.selectbox("Select a vehicle type to view data for:", sorted(vehicle_options), 0)

        # create filtered dataframes based on factor/vehicle preferences for various pie chart visualizations
        if factor != 'All factors':
            factor_filtered_data = collision_data.loc[collision_data['VEHICLE 1 FACTOR'] == factor.upper()]
        else:
            factor_filtered_data = collision_data
        if vehicle != 'All vehicles':
            vehicle_filtered_data = collision_data.loc[collision_data['VEHICLE 1 TYPE'] == vehicle.upper()]
        else:
            vehicle_filtered_data = collision_data

        # initiate function to produce each pie chart
        pie_charts(factor, vehicle, factor_filtered_data, vehicle_filtered_data)

    else:
        collision_data = file
        collision_data = collision_data[collision_data['TIME'].notna()]
        collision_data = collision_data.fillna("UNSPECIFIED")
        st.title(f"{page_list[3].title()}")

        # set the borough options for user to choose via selectbox
        borough_options = ['All boroughs']
        for index, row in collision_data.iterrows():
            if row['BOROUGH'].title() not in borough_options:
                borough_options.append(row['BOROUGH'].title())
        borough = st.sidebar.selectbox("Select a borough to view data for:", sorted(borough_options), 0)

        # set the color palette options for the use to choose via selectbox
        color_palette_options = ['No preference', 'Cubehelix', 'Flare', 'Magma', 'Viridis']
        color = st.sidebar.selectbox("Select a Seaborn color palette:", color_palette_options, 0)
        if color == color_palette_options[1]:
            color_style = color_palette_options[1].lower()
        elif color == color_palette_options[2]:
            color_style = color_palette_options[2].lower()
        elif color == color_palette_options[3]:
            color_style = color_palette_options[3].lower()
        elif color == color_palette_options[4]:
            color_style = color_palette_options[4].lower()
        else:
            pick = random.randint(1, 4)
            color_style = color_palette_options[pick].lower()

        # create filtered dataframes based on borough preferences for various visualizations
        if borough != 'All boroughs':
            filtered_data = collision_data.loc[collision_data['BOROUGH'] == borough.upper()]
        else:
            filtered_data = collision_data

        # initiate functions to produce output visuals
        title = f"Time of Day where Collisions Occur in {borough.title()}"
        heat_map(title, filtered_data, color_style)


main()
