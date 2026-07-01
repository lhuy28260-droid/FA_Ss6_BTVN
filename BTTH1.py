from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Hệ thống Quản lý Khóa học (Phong cách Cổ điển)")

class CourseModel(BaseModel):
    code: str
    name: str
    duration: int
    fee: int

courses = [
    {"id": 1, "code": "PY101", "name": "Python Basic", "duration": 30, "fee": 3000000},
    {"id": 2, "code": "API101", "name": "FastAPI Basic", "duration": 24, "fee": 2500000},
    {"id": 3, "code": "JV101", "name": "Java Basic", "duration": 40, "fee": 4000000}
]


@app.get("/courses")
def get_courses(keyword: Optional[str] = None, min_fee: Optional[int] = None, max_fee: Optional[int] = None):
    filtered_courses = []
    
    for c in courses:
        match_keyword = True
        match_min_fee = True
        match_max_fee = True
        
        
        if keyword is not None:
            keyword_lower = keyword.lower()
            in_name = keyword_lower in c["name"].lower()
            in_code = keyword_lower in c["code"].lower()
            if not in_name and not in_code:
                match_keyword = False
                
        
        if min_fee is not None:
            if c["fee"] < min_fee:
                match_min_fee = False
                
        
        if max_fee is not None:
            if c["fee"] > max_fee:
                match_max_fee = False
                
        
        if match_keyword and match_min_fee and match_max_fee:
            filtered_courses.append(c)
            
    return filtered_courses



@app.post("/courses", status_code=status.HTTP_201_CREATED)
def create_course(payload: CourseModel):
    
    if payload.name.strip() == "":
        raise HTTPException(status_code=400, detail="Tên khóa học không được để trống")
        
    
    if payload.duration <= 0:
        raise HTTPException(status_code=400, detail="Thời lượng phải lớn hơn 0")
        
    
    if payload.fee < 0:
        raise HTTPException(status_code=400, detail="Học phí không được nhỏ hơn 0")
        
    
    for c in courses:
        if c["code"].lower() == payload.code.lower():
            raise HTTPException(status_code=400, detail="Mã khóa học đã tồn tại")
            
    
    new_id = 1
    if courses:
        max_id = courses[0]["id"]
        for c in courses:
            if c["id"] > max_id:
                max_id = c["id"]
        new_id = max_id + 1
        
    
    new_course = {
        "id": new_id,
        "code": payload.code.upper(), 
        "name": payload.name,
        "duration": payload.duration,
        "fee": payload.fee
    }
    courses.append(new_course)
    return {"message": "Thêm khóa học thành công", "data": new_course}



@app.get("/courses/{course_id}")
def get_course_detail(course_id: int):
    target_course = None
    for c in courses:
        if c["id"] == course_id:
            target_course = c
            break
            
    if target_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
        
    return target_course


@app.put("/courses/{course_id}")
def update_course(course_id: int, payload: CourseModel):
    
    target_course = None
    for c in courses:
        if c["id"] == course_id:
            target_course = c
            break
            
    if target_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
        
    
    if payload.name.strip() == "":
        raise HTTPException(status_code=400, detail="Tên khóa học không được để trống")
        
    if payload.duration <= 0:
        raise HTTPException(status_code=400, detail="Thời lượng phải lớn hơn 0")
        
    if payload.fee < 0:
        raise HTTPException(status_code=400, detail="Học phí không được nhỏ hơn 0")
        
    
    for c in courses:
        if c["code"].lower() == payload.code.lower() and c["id"] != course_id:
            raise HTTPException(status_code=400, detail="Mã khóa học đã được sử dụng bởi khóa học khác")
            
    
    target_course["code"] = payload.code.upper()
    target_course["name"] = payload.name
    target_course["duration"] = payload.duration
    target_course["fee"] = payload.fee
    
    return {"message": "Cập nhật khóa học thành công", "data": target_course}


@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    target_index = -1
    for index in range(len(courses)):
        if courses[index]["id"] == course_id:
            target_index = index
            break
            
    if target_index == -1:
        raise HTTPException(status_code=404, detail="Course not found")
        
    deleted_course = courses.pop(target_index)
    return {"message": "Xóa khóa học thành công", "data": deleted_course}