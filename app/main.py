from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
from .routers.file_upload import router as file_upload
from .routers.transactions import router as transactions
from .routers.financial_institutions import router as financial_institutions
from .routers.lifestyle import router as lifestyle
from .routers.utility import router as utility
from .routers.credit_score import router as credit_score
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(file_upload)
app.include_router(financial_institutions)
app.include_router(lifestyle)
app.include_router(utility)
app.include_router(transactions)
app.include_router(credit_score)

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}