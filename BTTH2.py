from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Hệ thống Quản lý Học viên (Phong cách Cổ điển)")


class StudentModel(BaseModel):
    code: str
    name: str
    email: str
    age: int


students = [
    {"id": 1, "code": "SV001", "name": "Nguyen Van A", "email": "a@gmail.com", "age": 20},
    {"id": 2, "code": "SV002", "name": "Tran Thi B", "email": "b@gmail.com", "age": 22},
    {"id": 3, "code": "SV003", "name": "Le Van C", "email": "c@gmail.com", "age": 18}
]


@app.get("/students")
def get_students(
    keyword: Optional[str] = None, 
    min_age: Optional[int] = None, 
    max_age: Optional[int] = None
):
    filtered_students = []
    
    for s in students:
        match_keyword = True
        match_min_age = True
        match_max_age = True
        
        
        if keyword is not None:
            keyword_lower = keyword.lower()
            in_name = keyword_lower in s["name"].lower()
            in_code = keyword_lower in s["code"].lower()
            in_email = keyword_lower in s["email"].lower()
            
            
            if not in_name and not in_code and not in_email:
                match_keyword = False
                
       
        if min_age is not None:
            if s["age"] < min_age:
                match_min_age = False
                

        if max_age is not None:
            if s["age"] > max_age:
                match_max_age = False
                
        if match_keyword and match_min_age and match_max_age:
            filtered_students.append(s)
            
    return filtered_students


@app.post("/students", status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentModel):
    
    
    if payload.name.strip() == "":
        raise HTTPException(status_code=400, detail="Tên học viên không được để trống")
        
    
    if payload.email.strip() == "":
        raise HTTPException(status_code=400, detail="Email học viên không được để trống")
        
    
    if payload.age <= 0:
        raise HTTPException(status_code=400, detail="Tuổi phải lớn hơn 0")
        
    #
    for s in students:
        if s["code"].lower() == payload.code.lower():
            raise HTTPException(status_code=400, detail="Mã học viên đã tồn tại")
            
    
    new_id = 1
    if students:
        max_id = students[0]["id"]
        for s in students:
            if s["id"] > max_id:
                max_id = s["id"]
        new_id = max_id + 1
        
    
    new_student = {
        "id": new_id,
        "code": payload.code.upper(), 
        "name": payload.name,
        "email": payload.email,
        "age": payload.age
    }
    students.append(new_student)
    return {"message": "Thêm học viên thành công", "data": new_student}


@app.get("/students/{student_id}")
def get_student_detail(student_id: int):
    target_student = None
    for s in students:
        if s["id"] == student_id:
            target_student = s
            break
            
    if target_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
        
    return target_student



@app.put("/students/{student_id}")
def update_student(course_id: int, payload: StudentModel): 
   
    target_student = None
    for s in students:
        if s["id"] == course_id: 
            target_student = s
            break
            
    if target_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # Bước 2: Kiểm tra các điều kiện ràng buộc dữ liệu mới
    if payload.name.strip() == "":
        raise HTTPException(status_code=400, detail="Tên học viên không được để trống")
        
    if payload.email.strip() == "":
        raise HTTPException(status_code=400, detail="Email học viên không được để trống")
        
    if payload.age <= 0:
        raise HTTPException(status_code=400, detail="Tuổi phải lớn hơn 0")
        
    # Bước 3: Kiểm tra trùng code (Quét danh sách nhưng loại trừ chính nó)
    for s in students:
        if s["code"].lower() == payload.code.lower() and s["id"] != course_id:
            raise HTTPException(status_code=400, detail="Mã học viên đã được sử dụng bởi học viên khác")
            
    target_student["code"] = payload.code.upper()
    target_student["name"] = payload.name
    target_student["email"] = payload.email
    target_student["age"] = payload.age
    
    return {"message": "Cập nhật thông tin học viên thành công", "data": target_student}


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    target_index = -1
    for index in range(len(students)):
        if students[index]["id"] == student_id:
            target_index = index
            break
            
    if target_index == -1:
        raise HTTPException(status_code=404, detail="Student not found")
        
    deleted_student = students.pop(target_index)
    return {"message": "Xóa học viên thành công", "data": deleted_student}