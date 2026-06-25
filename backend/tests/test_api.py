def auth_headers(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "StrongPass123!",
        },
    )
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_registration_prediction_and_analytics(client):
    headers = auth_headers(client)
    prediction = client.post(
        "/api/v1/predictions",
        headers=headers,
        json={
            "amount": 1200,
            "time": "2026-06-25T13:30:00Z",
            "merchant_category": "grocery",
            "device_type": "android",
            "location": "Bengaluru",
            "transaction_frequency": 2,
        },
    )
    assert prediction.status_code == 200
    assert prediction.json()["prediction"] in {"Fraud", "Not Fraud"}

    summary = client.get("/api/v1/analytics/summary", headers=headers)
    assert summary.status_code == 200
    assert summary.json()["total_transactions"] == 1

    forbidden = client.get("/api/v1/admin/users", headers=headers)
    assert forbidden.status_code == 403

    export = client.get("/api/v1/transactions/export.csv", headers=headers)
    assert export.status_code == 200
    assert "secure-upi-report.csv" in export.headers["content-disposition"]
    assert "grocery" in export.text

    admin_login = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@secureupi.com", "password": "ChangeMe123!"},
    )
    assert admin_login.status_code == 200
    admin_headers = {
        "Authorization": f"Bearer {admin_login.json()['access_token']}"
    }
    users = client.get("/api/v1/admin/users", headers=admin_headers)
    assert users.status_code == 200
    assert len(users.json()) == 2
    admin_summary = client.get("/api/v1/analytics/summary", headers=admin_headers)
    assert admin_summary.json()["total_transactions"] == 1
