import os
import tempfile
import pytest
from unittest.mock import patch
from app import app, get_db_connection

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DB_PATH'] = ':memory:'

    with app.test_client() as client:
        with app.app_context():
            conn = get_db_connection()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_time TEXT,
                    incident_number TEXT,
                    incident_location TEXT,
                    nature TEXT,
                    incident_ori TEXT
                )
            """)
            conn.commit()
            conn.close()
        yield client

def test_index_get(client):
    """
    Test that the index page loads successfully.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"Upload Incidents" in response.data

def test_index_post_with_url(client, mocker):
    """
    Test submitting a URL via the index page.
    """
    mocker.patch('app.fetchincidents', return_value=b'%PDF-1.4 try_fake pdf data')
    mocker.patch('app.extractincidents', return_value=[
        {
            'Date/Time': '12/13/2024 12:00',
            'Incident Number': '66666',
            'Location': 'Florida',
            'Nature': 'Gator Attack',
            'Incident ORI': 'ORI777'
        }
    ])
    mocker.patch('app.populatedb', return_value=None)

    data = {'incident_url': 'http://example.com/try_fake.pdf'}
    response = client.post('/', data=data, follow_redirects=True)

    assert response.status_code == 200
    assert b"Visualizations" in response.data

def test_visualizations_get(client):
    """
    Test that the visualizations page loads successfully.
    """
    response = client.get('/visualizations')
    assert response.status_code == 200
    assert b"Visualizations" in response.data
