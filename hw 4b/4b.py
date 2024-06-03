#import necessary libraries
import altair as alt
from vega_datasets import data

# Since these data are each more than 5,000 rows we'll import from the URLs
airports = data.airports.url
flights_airport = data.flights_airport.url

# get US states topology features from data 
states = alt.topo_feature(data.us_10m.url, feature="states")

# Create pointerover selection
select_city = alt.selection_point(
    on="pointerover", nearest=True, fields=["origin"], empty=False
)

# Define which attributes to lookup from airports.csv
lookup_data = alt.LookupData(
    airports, key="iata", fields=["state", "latitude", "longitude"]
)

# create empty gray geoshape background of the United States with state outlines
background = alt.Chart(states).mark_geoshape(
    fill="lightgray",
    stroke="white"
).properties(
    width=750,
    height=500
).project("albersUsa")

# create connection lines between airports
connections = alt.Chart(flights_airport).mark_rule(opacity=0.35).encode(
    latitude="latitude:Q",  # the starting latitude for a connection line
    longitude="longitude:Q",  # the starting longitude for a connection line
    latitude2="lat2:Q",    # end lat for connection
    longitude2="lon2:Q"   # end long for connection
).transform_lookup(
    lookup="origin",   # add lookup details
    from_=lookup_data
).transform_lookup(
    lookup="destination",   # add lookup details
    from_=lookup_data,
    as_=["state", "lat2", "lon2"]
).transform_filter(
    select_city   # add filter option to filter on selected city
)

# create points for each airport, sized depending on the number of routes it has
points = alt.Chart(flights_airport).mark_circle().encode(
    latitude="latitude:Q",  # lat and long for airport point
    longitude="longitude:Q",
    size=alt.Size("routes:Q").legend(None).scale(range=[0, 1000]),  #Size point based on routes, no legend, scale point size
    order=alt.Order("routes:Q").sort("descending"),
    tooltip=["origin:N", "routes:Q"]  # add tooltip with airport's number of routes + code
).transform_aggregate(
    routes="count()",
    groupby=["origin"]
).transform_lookup(  
    lookup="origin",   #add lookup details
    from_=lookup_data
).transform_filter(
    (alt.datum.state != "PR") & (alt.datum.state != "VI")   #exclude Puerto Rico and Virgin Islands from filter
).add_params(
    select_city
)

# combine background map, connection lines, airport points into one whole interactive map
(background + connections + points).configure_view(stroke=None)