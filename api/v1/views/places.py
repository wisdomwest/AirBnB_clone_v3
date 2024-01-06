#!/usr/bin/python3
"""View for Place objects that handles all default RESTFul API actions"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from models import storage
from models.amenity import Amenity
from models.city import City
from models.state import State
from models.place import Place
from models.user import User


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_all_city_places(city_id):
    """return all the places linked to the city with city_id"""
    city = storage.get(City, city_id)

    if not city:
        abort(404)

    return jsonify([place.to_dict() for place in city.places])


@app_views.route('/places/<place_id>', methods=['GET'],
                 strict_slashes=False)
def get_place(place_id):
    """return a place by id in the database"""
    place = storage.get(Place, place_id)

    if not place:
        abort(404)

    return jsonify(place.to_dict()), 200


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """delete a place by id in the database"""
    place = storage.get(Place, place_id)

    if not place:
        abort(404)

    place.delete()
    storage.save()

    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    """create a place linked to the city with city_id"""
    city = storage.get(City, city_id)

    if not city:
        abort(404)

    try:
        place_dict = request.get_json()
    except Exception:
        return 'Not a JSON', 400

    if not place_dict:
        return 'Not a JSON', 400
    elif 'user_id' not in place_dict:
        return 'Missing user_id', 400
    elif not storage.get(User, place_dict['user_id']):
        abort(404)
    elif 'name' not in place_dict:
        return 'Missing name', 400

    place_dict['city_id'] = city_id
    new_place = Place(**place_dict)
    new_place.save()
    return jsonify(new_place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'],
                 strict_slashes=False)
def update_place(place_id):
    """update a place by id in the database"""
    place = storage.get(Place, place_id)

    if not place:
        abort(404)

    try:
        place_dict = request.get_json()
    except Exception:
        return 'Not a JSON', 400

    if not place_dict:
        return 'Not a JSON', 400

    ignored_keys = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']

    for key, value in place_dict.items():
        if key not in ignored_keys:
            setattr(place, key, value)

    place.save()

    return jsonify(place.to_dict()), 200


@app_views.route('/places_search', methods=['POST'],
                 strict_slashes=False)
def places_search():
    """retrieve places depending on JSON request"""

    try:
        request_dict = request.get_json()
    except Exception:
        return 'Not a JSON', 400

    if request_dict is None:
        return 'Not a JSON', 400

    if len(request_dict) == 0:
        return jsonify([obj.to_dict() for obj in storage.all(Place).values()])

    states = request_dict.get('states')
    cities = request_dict.get('cities')
    if cities is None:
        cities = []
    amenities = request_dict.get('amenities')

    if not states and not cities and not amenities:
        places = storage.all(Place).values()
    else:
        places = []
        if states:
            for state_id in states:
                state = storage.get(State, state_id)
                if not state:
                    abort(404)
                for city in state.cities:
                    if city.id not in cities:
                        cities.append(city.id)
        if cities:
            for city_id in cities:
                city = storage.get(City, city_id)
                if not city:
                    abort(404)
                for place in city.places:
                    places.append(place)

    amenity_ids = request_dict.get('amenities')
    if amenity_ids:
        for place in places:
            place_amenity_ids = [amn.id for amn in place.amenities]
            for amenity_id in amenity_ids:
                if not amenity_id in place_amenity_ids:
                    places.remove(place)
                    break

    return jsonify([place.to_dict() for place in places])
