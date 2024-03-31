#!/usr/bin/python3
"""
Flask route that returns json status response(places)
"""
from flask import jsonify, abort, request
from api.v1.views import app_views
from models import storage
from models.place import Place
from models.city import City
from models.user import User


@app_views.route('/cities/<city_id>/places', methods=['GET'])
def get_city_places(city_id):
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<place_id>', methods=['GET'])
def get_place(place_id):
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'])
def delete_place(place_id):
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places', methods=['POST'])
def create_place(city_id):
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    if not request.json:
        abort(400, 'Not a JSON')
    data = request.json
    if 'user_id' not in data:
        abort(400, 'Missing user_id')
    user = storage.get(User, data['user_id'])
    if not user:
        abort(404)
    if 'name' not in data:
        abort(400, 'Missing name')
    place = Place(**data)
    place.city_id = city_id
    place.save()
    return jsonify(place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'])
def update_place(place_id):
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    if not request.json:
        abort(400, 'Not a JSON')
    data = request.json
    for key, value in data.items():
        if key not in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(place, key, value)
    place.save()
    return jsonify(place.to_dict()), 200


@app_views.route('/places_search', methods=['POST'])
def places_search():
    """Search for places based on JSON request body"""
    if not request.is_json:
        abort(400, description="Not a JSON")

    search_params = request.json
    states = search_params.get('states', [])
    cities = search_params.get('cities', [])
    amenities = search_params.get('amenities', [])

    places = []
    if not states and not cities and not amenities:
        places = storage.all('Place').values()
    else:
        # Retrieve places based on search parameters
        for state_id in states:
            state = storage.get('State', state_id)
            if state:
                places.extend(state.cities)
        for city_id in cities:
            city = storage.get('City', city_id)
            if city and city not in places:
                places.append(city)
        if amenities:
            amenities_set = set(amenities)
            places = [place for place in places if amenities_set.issubset(place.amenity_ids)]

    return jsonify([place.to_dict() for place in places])
