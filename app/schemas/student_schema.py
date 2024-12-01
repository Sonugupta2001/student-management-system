from pydantic import BaseModel, Field
from typing import Dict

class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

class StudentUpdate(BaseModel):
    name: str = None
    age: int = None
    address: Address = None
