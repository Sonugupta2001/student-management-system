from fastapi import APIRouter, HTTPException, Response
from app.database.db import students_collection
from app.schemas.student_schema import Student, StudentUpdate
from bson import ObjectId
from typing import Optional
from fastapi import Query
from bson import ObjectId


#---------------------------------------------------------------------------------------------------------#

def serialize_mongo_document(document):
    return {
        "id": str(document["_id"]),
        "name": document.get("name"),
        "age": document.get("age"),
        "address": document.get("address", {})
    }

#---------------------------------------------------------------------------------------------------------#


router = APIRouter()


@router.post("/students", status_code=201)
async def create_student(student: Student):
    student_dict = student.dict()
    
    result = await students_collection.insert_one(student_dict)
    return {"id": str(result.inserted_id)}




@router.get("/students")
async def list_students(
    country: Optional[str] = Query(None, description="Filter by country"),
    age: Optional[int] = Query(None, description="Filter by minimum age")
):
    query = {}
    if country:
        query["address.country"] = country
    if age is not None:
        query["age"] = {"$gte": age}

    students_cursor = students_collection.find(query)
    students = []
    async for student in students_cursor:
        if "name" in student and "age" in student and "address" in student:
            if "city" in student["address"] and "country" in student["address"]:
                students.append({
                    "name": student["name"],
                    "age": student["age"]
                })

    return {"data": students}




@router.get("/students/{id}")
async def fetch_student(id: str):
    try:
        student_data = await students_collection.find_one({"_id": ObjectId(id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if not student_data:
        raise HTTPException(status_code=404, detail="Student not found")


    if "name" not in student_data or "age" not in student_data or "address" not in student_data:
        raise HTTPException(status_code=500, detail="Student data is incomplete")

    address = student_data["address"]
    if "city" not in address or "country" not in address:
        raise HTTPException(status_code=500, detail="Student address is incomplete")

    return {
        "name": student_data["name"],
        "age": student_data["age"],
        "address": {
            "city": address["city"],
            "country": address["country"]
        }
    }




@router.patch("/students/{id}")
async def update_student(id: str, student_update: StudentUpdate, response: Response):
    update_data = student_update.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    try:
        result = await students_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Student not found or no change")
        
        response.status_code = 204
        return {}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to update student")




@router.delete("/students/{student_id}", status_code=200)
async def delete_student(student_id: str):
    student_data = await students_collection.find_one({"_id": ObjectId(student_id)})
    if not student_data:
        raise HTTPException(status_code=404, detail="Student not found")

    delete_result = await students_collection.delete_one({"_id": ObjectId(student_id)})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=400, detail="Failed to delete the student")

    return {}
