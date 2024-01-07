#!/usr/bin/env bash
state_id1=$(echo 'SELECT id FROM states;' | sudo mysql hbnb_dev_db | head -8 | tail -1)
city_id=$(echo 'SELECT id FROM cities;' | sudo mysql hbnb_dev_db | head -8 | tail -1)
amenity_id=$(echo 'SELECT id FROM amenities;' | sudo mysql hbnb_dev_db | head -3 | tail -1)

echo "{\"states\": [\"$state_id1\"], \"cities\" : [\"$city_id\"], \"amenities\": [\"$amenity_id\"]}"
curl -X POST http://0.0.0.0:5000/api/v1/places_search -H "Content-Type: application/json" -d "{\"states\": [\"$state_id1\"], \"cities\" : [\"$city_id\"]}"
# \"states\": [\"$state_id1\"], 
# , \"amenities\": [\"$amenity_id\"]
