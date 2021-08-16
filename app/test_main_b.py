from fastapi.testclient import TestClient
from .app import app, Base, get_db


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

wallet_data = [
    {"id":1, "user":"Ahmed", "points": 10, "description": "test description"},
    {"id":2, "user":"Omar", "points": 20, "description": "test description"}
    ]

def test_create_wallet_view():
    for i in wallet_data:
        response = client.post(
            '/wallet',
            json=i
        )

        assert response.status_code == 201, response.text
        data = response.json()
        assert data == i
    
def test_get_wallet_view():
    for idx, val in enumerate(wallet_data):
        response = client.get(f"/wallet/{idx+1}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == val

def test_get_all_wallets_view():
    response = client.get("/wallets")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == wallet_data


    

def test_add_to_wallet_view():
    response = client.put("/wallet/add/1?points=5")
    assert response.status_code == 201, response.text

    response = client.get(f"/wallet/1")
    data = response.json()
    assert data["points"] == 15.0

def test_withdraw_from_wallet_view():
    response = client.put("/wallet/withdraw/2?points=5")
    assert response.status_code == 201, response.text

    response = client.get(f"/wallet/1")
    data = response.json()
    assert data["points"] == 15.0

    response = client.put("/wallet/withdraw/2?points=100")
    assert response.status_code == 400, response.text

    response = client.get(f"/wallet/1")
    data = response.json()
    assert data["points"] == 15.0


def test_delete_wallet_view():
    response = client.delete("/wallet/2")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {"message": "wallet deleted successfully!"}

    response = client.delete("/wallet/2")
    assert response.status_code == 404, response.text
    data = response.json()
    assert data == {"detail":"Wallet not Found"}