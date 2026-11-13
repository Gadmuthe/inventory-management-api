from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import ProductDB, UserDB
from schemas import UserCreate, ProductCreate, ProductUpdate, ProductOut
from auth import hash_password, verify_password, create_access_token, get_current_user

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Inventory Management API", version="1.0.0")

origins = [x.strip() for x in __import__("os").getenv(
    "CORS_ORIGINS", "http://localhost:5173"
).split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(UserDB).filter(UserDB.username == payload.username).first():
        raise HTTPException(status_code=409, detail="Username already exists")
    user = UserDB(username=payload.username, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {"access_token": create_access_token(user.username), "token_type": "bearer"}

@app.get("/products", response_model=list[ProductOut])
def get_products(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(ProductDB).order_by(ProductDB.id.desc()).all()

@app.post("/products", response_model=ProductOut, status_code=201)
def add_product(payload: ProductCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    product = ProductDB(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in payload.model_dump().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}
