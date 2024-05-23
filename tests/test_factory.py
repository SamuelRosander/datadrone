from datadrone import create_app


def test_config():
    assert not create_app({"SQLALCHEMY_DATABASE_URI": "sqlite://"}).testing
    assert create_app({'TESTING': True,
                       "SQLALCHEMY_DATABASE_URI": "sqlite://"}).testing


def test_login_page(client):
    response = client.get("/auth/login")

    assert response.status_code == 200
    assert b"<title>DataDrone</title>" in response.data
