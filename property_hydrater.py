from http import HTTPStatus
import json
from googlemaps_places_api import FindPlaceFromText, FindPlaceFromTextRequest, GMapsLocation, NearByPlaces, NearByPlacesRequest, geodb
import geo_distancer


from tinydb import Query






def hydrate_property(address:str, property_engine_search_area:str=''):
    '''Pull information from Alternative data sources using the property address'''
    assert address is not None, f'{__name__}.hydrate_property[address] can not be None'
    
    # define the properties to hydrate
    num_train_stations_near_to_property = 0.0
    num_underground_stations_near_to_property = 0.0
    num_transit_stations_near_to_property = 0.0
    num_supermarkets_near_to_property = 0.0
    num_schools_near_to_property = 0.0
    
    
    find_place_response = FindPlaceFromTextRequest.get(address, property_engine_search_area)
    if find_place_response is None:
        return
    else:
        geocoordinates = {candidate.formatted_address: candidate.geometry.location 
                            for candidate in find_place_response.candidates}
    
    
    geocoordinate = list(geocoordinates.values())[0]
    
    nearby_radius = 1500 # 1.5km
    
    # locate nearest coordinate in the db
    (north, east, south, west) = geo_distancer.calculate_points_radius(geocoordinate.lat,geocoordinate.lng, nearby_radius / 1000.0)
    qry = Query()
    near_points = geodb.search(qry.lat <= north[0] and
                 qry.lon <= east[1] and
                 qry.lat >= south[0] and
                 qry.lon >= west[1])
    
    
    
    def pull_nearyby_places_of_type(type_place:str):
        '''type_place must be in https://developers.google.com/maps/documentation/places/web-service/supported_types#table1'''
        nearby_typed_places = [p for p in near_points if type_place in p['types']]
        if nearby_typed_places:
            return len(nearby_typed_places)
        else:
            nearby_results_response = NearByPlacesRequest.get(type_place, geocoordinate, nearby_radius)
            if nearby_results_response is None:
                return 0
            return len([p for p in nearby_results_response.results if type_place in p.types])
            
    
    
    num_train_stations_near_to_property = pull_nearyby_places_of_type('train_station')
    num_underground_stations_near_to_property = pull_nearyby_places_of_type('subway_station')
    num_transit_stations_near_to_property = pull_nearyby_places_of_type('transit_station')
    num_supermarkets_near_to_property = pull_nearyby_places_of_type('supermarket')
    num_schools_near_to_property = pull_nearyby_places_of_type('school')
    
    return {
        'num_stations_near_to_property': num_stations_near_to_property,
        'num_supermarkets_near_to_property': num_supermarkets_near_to_property,
        'num_schools_near_to_property': num_schools_near_to_property,
    }
    
        
    



hydrated_property = hydrate_property(address='Prince Edwin Street, Liverpool, L5')
print(hydrate_property)