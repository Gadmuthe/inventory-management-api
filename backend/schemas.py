from pydantic import BaseModel, Field, ConfigDict

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8)

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)
    category: str = Field(min_length=1, max_length=80)

class ProductUpdate(ProductCreate):
    pass

class ProductOut(ProductCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
