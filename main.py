
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal


# LOAD ENVIRONMENT VARIABLES
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing from .env")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


app = FastAPI(title="Inventory Management API")

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# PRODUCT DATABASE MODEL
class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    category = Column(String, nullable=False)


# USER DATABASE MODEL
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)


Base.metadata.create_all(bind=engine, checkfirst=True)


# PYDANTIC MODELS
class Product(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)
    category: str = Field(min_length=1)


class UserCreate(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=8)


class Token(BaseModel):
    access_token: str
    token_type: str


# DATABASE SESSION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# PASSWORD FUNCTIONS
def get_password_hash(password: str):
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)


# JWT TOKEN
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# CURRENT USER
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise credentials_exception

    except jwt.InvalidTokenError:
        raise credentials_exception

    user = db.query(UserDB).filter(
        UserDB.username == username
    ).first()

    if user is None:
        raise credentials_exception

    return user


# HOME
@app.get("/")
def home():
    return {"message": "Inventory Management API is running"}


# REGISTER
@app.post("/register", status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(UserDB).filter(
        UserDB.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    new_user = UserDB(
        username=user.username,
        hashed_password=get_password_hash(user.password)
    )

    db.add(new_user)
    db.commit()

    return {"message": "User registered successfully"}


# LOGIN
@app.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(UserDB).filter(
        UserDB.username == form_data.username
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(
        data={"sub": user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# CREATE PRODUCT
@app.post("/products", status_code=201)
def create_product(
    product: Product,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):

    new_product = ProductDB(**product.model_dump())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# READ ALL PRODUCTS
@app.get("/products")
def get_products(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):

    return db.query(ProductDB).all()


# READ ONE PRODUCT
@app.get("/products/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):

    product = db.query(ProductDB).filter(
        ProductDB.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


# UPDATE PRODUCT
@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    product: Product,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):

    existing_product = db.query(ProductDB).filter(
        ProductDB.id == product_id
    ).first()

    if existing_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    for key, value in product.model_dump().items():
        setattr(existing_product, key, value)

    db.commit()
    db.refresh(existing_product)

    return existing_product


# DELETE PRODUCT
@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):

    product = db.query(ProductDB).filter(
        ProductDB.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully",
        "product_id": product_id
    }
