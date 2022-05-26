from http import HTTPStatus
import json
from urllib.parse import urlencode
from dotenv import load_dotenv
import os
from tinydb import TinyDB, Query

from ISerializable import ISerializable
from tiny_cache import TinyCache

class GMapsLocation():
    def __init__(self) -> None:
        self.lat = 0.0
        self.lng = 0.0
        
    @staticmethod
    def fromJson(json:dict):
        inst = GMapsLocation()
        inst.lat = getattr(json,'lat', 0.0)
        inst.lng = getattr(json,'lng', 0.0)
        return inst
        
    def toJson(self):
        return {
            'lat': self.lat,
            'lng': self.lng,
        }
        
        

class GMapsGeometry(ISerializable):
    def __init__(self) -> None:
        self.location = GMapsLocation()
        self.viewport = {
            "northeast": GMapsLocation(),
            "southwest": GMapsLocation(),
        }
        
    @staticmethod
    def fromJson(json:dict):
        inst = GMapsGeometry()
        inst.location = GMapsLocation.fromJson(json['location'])
        inst.viewport = {
            "northeast": GMapsLocation.fromJson(json['viewport']['northeast']),
            "southwest": GMapsLocation.fromJson(json['viewport']['southwest']),
        }
        return inst
    
    def toJson(self):
        return {
            "location": self.location.toJson(),
            "viewport":
            {
                "northeast": self.viewport['northeast'].toJson(),
                "southwest": self.viewport['southwest'].toJson(),
            },
        }
        
class GMapsFindPlaceFromTextCandidate:
    def __init__(self) -> None:
        self.formatted_address = ''
        self.geometry = GMapsGeometry()
        self.name = ""
        self.rating = 0.0
        
    @staticmethod
    def fromJson(json:dict):
        inst = GMapsFindPlaceFromTextCandidate()
        inst.formatted_address = getattr(json,'formatted_address', "")
        inst.name = getattr(json, 'name', "")
        inst.rating = getattr(json, 'rating', 0.0)
        inst.geometry = getattr(json, 'geometry', None)
        return inst
        
    def toJson(self):
        return {
            'formatted_address': self.formatted_address,
            'name': self.name,
            'rating': self.rating,
            'geometry': self.geometry.toJson(),
        }


class FindPlaceFromText(ISerializable):
    def __init__(self) -> None:
        self.status:str = ""
        self.candidates:list[GMapsFindPlaceFromTextCandidate] = []
        
    @staticmethod
    def fromJson(json:dict):
        inst = FindPlaceFromText()
        
        inst.status = getattr(json,'status',"")
        inst.candidates = [GMapsFindPlaceFromTextCandidate.fromJson(c) 
                           for c in getattr(json, 'candidates', [])]
        
        return inst
    
    def toJson(self):
        return {
            'status': self.status,
            'candidates': [c.toJson() for c in self.candidates]
        }
        

class GMapsPhotoRef:
    def __init__(self) -> None:
        self.height = 0.0
        self.width = 0.0
        self.html_attributions:list[str] = []
        self.photo_reference = ""
    
    @staticmethod   
    def fromJson(json:dict):
        inst = GMapsPhotoRef()
        inst.height = json['height']
        inst.width = json['width']
        inst.html_attributions = json['html_attributions']
        inst.photo_reference = json['photo_reference']
        return inst
    
    def toJson(self):
        return {
            'height': self.height,
            'width': self.width,
            'html_attributions': self.html_attributions,
            'photo_reference': self.photo_reference,
        }
        
        
class GMapsNearbyPlace:
    def __init__(self) -> None:
        self.business_status = ""
        self.geometry = GMapsGeometry()
        self.icon = ""
        # self.icon_background_color = ""
        # self.icon_mask_base_uri = ""
        self.name = ""
        # self.opening_hours = {
        #         "open_now": false
        #     },
        self.photos:list[GMapsPhotoRef] = []
        self.place_id = ""
        self.plus_code = {
                "compound_code": "",
                "global_code": "",
            }
        self.price_level:int = 0
        self.rating:float = 0.0
        self.reference = ""
        self.scope = "GOOGLE"
        self.types:list[str] = []
        self.user_ratings_total:int = 0
        self.vicinity = ""
        
    @staticmethod
    def fromJson(json:dict):
        inst = GMapsNearbyPlace()
        inst.business_status = json['business_status']
        inst.geometry = GMapsGeometry.fromJson(json['geometry'])
        inst.name = json['name']
        inst.icon = json['icon']
        inst.photos = [GMapsPhotoRef.fromJson(p) for p in getattr(json, 'photos', [])]
        inst.place_id = json['place_id']
        inst.price_level = json['price_level']
        inst.rating = json['rating']
        inst.reference = json['reference']
        inst.scope = json['scope']
        inst.types = json['types']
        inst.user_ratings_total = json['user_ratings_total']
        inst.vicinity = json['vicinity']
        return inst
    
    def toJson(self):
        return {
            'business_status': self.business_status,
            'geometry': self.geometry.toJson(),
            'name': self.name,
            'icon': self.icon,
            'photos': [p.toJson() for p in self.photos],
            'place_id': self.place_id,
            'price_level': self.price_level,
            'rating': self.rating,
            'reference': self.reference,
            'scope': self.scope,
            'types': self.types,
            'user_ratings_total': self.user_ratings_total,
            'vicinity': self.vicinity,
        }
        


class NearByPlaces(ISerializable):
    def __init__(self) -> None:
        self.html_attributions:list[str] = []
        self.next_page_token:str|None = None
        self.status:str=""
        self.results:list[GMapsNearbyPlace] = []
        
    @staticmethod
    def fromJson(json:dict):
        inst = NearByPlaces()
        inst.html_attributions = json['html_attributions']
        inst.next_page_token = json['next_page_token']
        inst.status = json['status']
        inst.results = [GMapsNearbyPlace.fromJson(r) for r in json['results']]
        return inst
    
    def toJson(self):
        return {
            'html_attributions': self.html_attributions,
            'next_page_token': self.next_page_token,
            'status': self.status,
            'results': [r.toJson() for r in self.results],
        }
        
load_dotenv()

API_KEY = os.getenv('API_KEY')

cache = TinyCache()
geodb = TinyDB('geodb.json')
        
class NearByPlacesRequest:
    @staticmethod
    def get(place_type:str, near: GMapsLocation, nearby_radius:float) -> NearByPlaces|None:
        nearby_params_of_type = {
            'location': ','.join([str(near.lat), str(near.lng)]),
            'radius': nearby_radius,
            'fields': '',
            'rankby': 'prominence', # if use distance then remove the radius parameter
            # 'keyword': 'station', # Note: Adding both `keyword` and `type` with the same value (`keyword=cafe&type=cafe` or `keyword=parking&type=parking`) can yield `ZERO_RESULTS`.
            'type': place_type,
            'key': API_KEY
        }
            
        nearby_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?{urlencode(nearby_params_of_type)}"
        response_text, status_code = cache.url_request(nearby_url)
        if status_code != HTTPStatus.OK:
            return None
        response_obj = json.loads(response_text)
        if hasattr(response_obj,'results'):
            nearby_results_response = NearByPlaces.fromJson(response_obj)
            if nearby_results_response.status == 'OK':
                # Add the nearby places to local projection of places for postcode
                for result in nearby_results_response.results:
                    geodb.insert({'name': result.name, 
                                'lat': result.geometry.location.lat,
                                'lng': result.geometry.location.lng,
                                'types': result.types,
                                })
                
                return nearby_results_response
        else:
            return None
        
        
class FindPlaceFromTextRequest:
    @staticmethod
    def get(query_address:str, property_engine_search_area:str|None=None) -> FindPlaceFromText|None:
        # Get geocoordinates of place:
        find_place_params = {
            **{
                'input': query_address,
                'inputtype': 'textquery',
                # 'fields': 'formatted_address,name,rating,opening_hours,geometry,type',
                'fields': 'formatted_address,geometry',
                'key': API_KEY
            },
            **({
                'locationbias': property_engine_search_area
                } if property_engine_search_area else {}
            )
        }
        find_place_url = f'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?{urlencode(find_place_params)}'
        response_text, status_code = cache.url_request(url=find_place_url)
        if status_code != HTTPStatus.OK:
            return None
        response_obj = json.loads(response_text)
        geocoordinate:GMapsLocation|None=None
        if hasattr(response_obj,'candidates'):
            find_place_response = FindPlaceFromText.fromJson(response_obj)
            
            # for candidate in response_obj['candidates']:
            #     geodb.insert({'formatted_address': candidate['formatted_address'], 
            #                   'lat': candidate['geometry']['location']['lat'],
            #                   'lng': candidate['geometry']['location']['lng'],
            #                   'types': candidate['types']
            #                   })
            for candidate in find_place_response.candidates:
                geodb.insert({'name': candidate.formatted_address, 
                            'lat': candidate.geometry.location.lat,
                            'lng': candidate.geometry.location.lng,
                            'types': ['property']
                            })
            return find_place_response
        else:
            raise Warning(f'No candidate results returned for search address: {query_address}')
        