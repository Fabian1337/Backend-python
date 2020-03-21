import os
os.environ['GOOGLE_MAPS_KEY'] = 'test'
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
import json

from app.main import app


client = TestClient(app)


def test_read_markets_zip_code():
    with patch('googlemaps.Client') as patched_client:
        response = client.get("/markets?zip_code=50933")
        assert response.status_code == 404


def test_read_markets_lat_lng():

    with patch('googlemaps.Client') as patched_client:
        with open('tests/resources/response_place_nearbysearch.json') as fp:
            patched_client.return_value.places_nearby.return_value = json.load(fp)
        response = client.get("/markets?latitude=50.935173&longitude=6.953101")
        assert response.status_code == 200
        markets = response.json()
        assert len(markets) == 20
        assert markets[0]['name'] == 'REWE'
        assert markets[0]['latitude'] == 50.9356314
        assert markets[0]['longitude'] == 6.9565733
        # verify address
        assert markets[0]['vicinity'] == 'Hohe Str. 30, Köln'
        # verify opening hours
        assert markets[0]['open_now'] is True
        # verify id
        assert markets[0]['id'] == "ChIJqQrWBrIlv0cRJJd5f3qooWM"
        # verify distance
        assert abs(markets[0]['distance'] - 0.2486) < 1e-4


def test_read_markets_radius():
    client.app.query_cache = []
    with patch('googlemaps.Client') as patched_client:
        response = client.get("/markets?latitude=50.935173&longitude=6.953101")
        assert patched_client.mock_calls[1][2]['radius'] == 1000

    client.app.query_cache = []
    with patch('googlemaps.Client') as patched_client:
        response = client.get("/markets?latitude=50.935173&longitude=6.953101&radius=2000")
        assert patched_client.mock_calls[1][2]['radius'] == 2000


def test_cache():
    client.app.query_cache = []
    with patch('googlemaps.Client') as patched_client:
        response = client.get("/markets?latitude=50.73438&longitude=7.09549")
        assert len(patched_client.mock_calls) == 3
        response = client.get("/cache/markets").json()
        assert len(response) == 1

    with patch('googlemaps.Client') as patched_client:
        response = client.get("/markets?latitude=50.73438&longitude=7.10000")
        assert len(patched_client.mock_calls) == 0
        response = client.get("/cache/markets").json()
        assert len(response) == 1

    # implement max size for cache
    assert True is False