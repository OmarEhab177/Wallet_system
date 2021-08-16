from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Column, Float, String, Integer
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND


app = FastAPI()

#SqlAlchemy Setup
SQLALCHEMY_DATABASE_URL = 'sqlite+pysqlite:///./db.sqlite3:app.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define a Place database SQLAlchemy model 

class DBWallet(Base):
    __tablename__ = "wallet"
    
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(50))
    points = Column(Float)
    description = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

class Wallet(BaseModel):
    id : int
    user : str
    points : float
    description : Optional[str] =None

    class Config:
        orm_mode = True


def create_wallet(db:Session, wallet:Wallet):
    db_wallet = DBWallet(**wallet.dict())
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)

    return db_wallet

def get_wallet(db: Session, wallet_id:int):
    wallet = db.query(DBWallet).where(DBWallet.id == wallet_id).first()
    if wallet == None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Wallet not Found")
    return wallet


def get_all_wallets(db:Session):
    return db.query(DBWallet).all()


def add_to_wallet(db:Session, wallet_id:int, points:float):
    wallet = db.query(DBWallet).where(DBWallet.id == wallet_id).first()
    if wallet == None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Wallet not Found")
    wallet.points += points
    db.commit()
    db.refresh(wallet)
    return wallet

def withdraw_from_wallet(db:Session, wallet_id:int, points:float):
    wallet = db.query(DBWallet).where(DBWallet.id == wallet_id).first()
    if wallet == None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Wallet not Found")
    print("############:", wallet.points)
    print("points: ", points)
    if points > wallet.points:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="There is not enough points")
    wallet.points -= points
    db.commit()
    db.refresh(wallet)
    return wallet

def delete_wallet(db: Session, wallet_id:int):
    wallet = db.query(DBWallet).where(DBWallet.id == wallet_id).first()
    if wallet == None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Wallet not Found")
    db.delete(wallet)
    db.commit()
    return {"message": "wallet deleted successfully!"}



@app.post('/wallet', response_model=Wallet, description="Create new wallet", tags=["Wallet"], status_code=201)
async def create_wallet_view(wallet:Wallet, db:Session = Depends(get_db)):
    db_wallet = create_wallet(db, wallet)
    return db_wallet

@app.get("/wallet/{wallet_id}", description="Retrieve wallet by id", tags=["Wallet"], status_code=200)
async def get_wallet_view(wallet_id: int, db:Session = Depends(get_db)):
    return get_wallet(db, wallet_id)

@app.get("/wallets", response_model=List[Wallet], description="Retrieve all wallets", tags=["Wallet"], status_code=200)
async def get_all_wallets_view(db:Session = Depends(get_db)):
    return get_all_wallets(db)

@app.put("/wallet/add/{wallet_id}", response_model=Wallet, description="Add points to wallet", tags=["Wallet"], status_code=201)
async def add_to_wallet_view(wallet_id:int, points:float, db:Session = Depends(get_db)):
    return add_to_wallet(db, wallet_id, points)

@app.put("/wallet/withdraw/{wallet_id}", response_model=Wallet, description="Withdraw points from wallet", tags=["Wallet"], status_code=201)
async def withdraw_from_wallet_view(wallet_id:int, points:float, db:Session = Depends(get_db)):
    return withdraw_from_wallet(db, wallet_id, points)

@app.delete("/wallet/{wallet_id}", description="Delete Wallet", tags=["Wallet"], status_code=200)
async def delete_wallet_view(wallet_id:int, db:Session = Depends(get_db)):
    return delete_wallet(db, wallet_id)


@app.get('/', description="Home Page", tags=["Root"], status_code=200)
async def root():
    return {"message": "Welcome There, How can i help you?"}



# @app.put('/wallet/{id}', description="add points to wallet" ,tags=["Payment"])


# @app.post('/payment', description="Payment Page", tags=["Payment"])
# async def create_wallet(wallet: Wallet):
#     return wallet
    
