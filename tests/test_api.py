def test_create_and_get_job(client, job):
    assert job["status"] == "open" and job["quotes"] == []
    assert client.get(f"/jobs/{job['id']}").json()["title"] == "Reforma de baño"


def test_quote_and_accept_flow(client, job):
    q1 = client.post(f"/jobs/{job['id']}/quotes", json={"professional": "Baños Pro", "amount_eur": "6500.00"}).json()
    client.post(f"/jobs/{job['id']}/quotes", json={"professional": "Reformas Ya", "amount_eur": "7100"})

    accepted = client.post(f"/jobs/{job['id']}/quotes/{q1['id']}/accept").json()

    assert accepted["status"] == "accepted"
    assert {q["professional"]: q["status"] for q in accepted["quotes"]} == {
        "Baños Pro": "accepted",
        "Reformas Ya": "rejected",
    }


def test_business_rule_violations_are_409(client, job):
    client.post(f"/jobs/{job['id']}/cancel")
    r = client.post(f"/jobs/{job['id']}/quotes", json={"professional": "Tarde", "amount_eur": "10"})
    assert r.status_code == 409 and "cancelled" in r.json()["detail"]


def test_validation_and_not_found(client):
    assert client.post("/jobs", json={"title": "x"}).status_code == 422
    assert client.get("/jobs/00000000-0000-0000-0000-000000000000").status_code == 404


def test_filters(client, job):
    client.post("/jobs", json={"title": "Pintar", "description": "Piso de 80 m2", "province": "Valencia"})
    assert len(client.get("/jobs", params={"province": "madrid"}).json()) == 1
    assert len(client.get("/jobs", params={"status": "open"}).json()) == 2
