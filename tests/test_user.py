def test_register(client):
    response = client.get("/user/register")

    assert response.status_code == 200
    assert b"<title>DataDrone</title>" in response.data


def test_reset_password(client):
    response = client.get("/user/reset_password")

    assert response.status_code == 200
    assert b"<title>DataDrone</title>" in response.data


def test_account(client):
    response = client.get("/user/account")

    assert response.status_code == 302
