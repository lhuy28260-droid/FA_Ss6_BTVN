from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Hệ thống Quản lý và Đặt lịch Phòng học")

class RoomModel(BaseModel):
    code: str
    name: str
    capacity: int
    status: str

class BookingModel(BaseModel):
    room_id: int
    class_name: str
    student_count: int
    date: str
    slot: str


rooms = [
    {"id": 1, "code": "R101", "name": "Room 101", "capacity": 30, "status": "AVAILABLE"},
    {"id": 2, "code": "R102", "name": "Room 102", "capacity": 20, "status": "AVAILABLE"},
    {"id": 3, "code": "R103", "name": "Room 103", "capacity": 40, "status": "MAINTENANCE"}
]

room_bookings = [
    {
        "id": 1,
        "room_id": 1,
        "class_name": "Python Basic",
        "student_count": 25,
        "date": "2026-07-01",
        "slot": "MORNING"
    }
]


@app.get("/rooms")
def get_rooms(
    keyword: Optional[str] = None, 
    status: Optional[str] = None, 
    min_capacity: Optional[int] = None
):
    filtered_rooms = []
    
    for r in rooms:
        match_keyword = True
        match_status = True
        match_capacity = True
        
        
        if keyword is not None:
            keyword_lower = keyword.lower()
            in_code = keyword_lower in r["code"].lower()
            in_name = keyword_lower in r["name"].lower()
            if not in_code and not in_name:
                match_keyword = False
                
        
        if status is not None:
            if r["status"].upper() != status.upper():
                match_status = False
                

        if min_capacity is not None:
            if r["capacity"] < min_capacity:
                match_capacity = False
                

        if match_keyword and match_status and match_capacity:
            filtered_rooms.append(r)
            
    return filtered_rooms


@app.post("/rooms", status_code=status.HTTP_201_CREATED)
def create_room(payload: RoomModel):
    # --- MỤC 6: RÀNG BUỘC PHÒNG HỌC ---
    if payload.name.strip() == "":
        raise HTTPException(status_code=400, detail="Tên phòng học không được để trống")
        
    if payload.capacity <= 0:
        raise HTTPException(status_code=400, detail="Sức chứa phải lớn hơn 0")
        
    valid_statuses = ["AVAILABLE", "IN_USE", "MAINTENANCE"]
    if payload.status.upper() not in valid_statuses:
        raise HTTPException(status_code=400, detail="Trạng thái phòng không hợp lệ")
        
    for r in rooms:
        if r["code"].lower() == payload.code.lower():
            raise HTTPException(status_code=400, detail="Mã phòng học đã tồn tại")
            
    new_id = 1
    if rooms:
        max_id = rooms[0]["id"]
        for r in rooms:
            if r["id"] > max_id:
                max_id = r["id"]
        new_id = max_id + 1
        
    new_room = {
        "id": new_id,
        "code": payload.code.upper(),
        "name": payload.name,
        "capacity": payload.capacity,
        "status": payload.status.upper()
    }
    rooms.append(new_room)
    return {"message": "Thêm phòng học thành công", "data": new_room}


@app.get("/rooms/{room_id}")
def get_room_detail(room_id: int):
    target_room = None
    for r in rooms:
        if r["id"] == room_id:
            target_room = r
            break
            
    if target_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
        
    return target_room


@app.put("/rooms/{room_id}")
def update_room(room_id: int, payload: RoomModel):
    target_room = None
    for r in rooms:
        if r["id"] == room_id:
            target_room = r
            break
            
    if target_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
        
    # Validate dữ liệu
    if payload.name.strip() == "":
        raise HTTPException(status_code=400, detail="Tên phòng học không được để trống")
        
    if payload.capacity <= 0:
        raise HTTPException(status_code=400, detail="Sức chứa phải lớn hơn 0")
        
    valid_statuses = ["AVAILABLE", "IN_USE", "MAINTENANCE"]
    if payload.status.upper() not in valid_statuses:
        raise HTTPException(status_code=400, detail="Trạng thái phòng không hợp lệ")
        
    for r in rooms:
        if r["code"].lower() == payload.code.lower() and r["id"] != room_id:
            raise HTTPException(status_code=400, detail="Mã phòng học đã được sử dụng bởi phòng khác")
            
    target_room["code"] = payload.code.upper()
    target_room["name"] = payload.name
    target_room["capacity"] = payload.capacity
    target_room["status"] = payload.status.upper()
    
    return {"message": "Cập nhật phòng học thành công", "data": target_room}


@app.delete("/rooms/{room_id}")
def delete_room(room_id: int):
    target_index = -1
    for index in range(len(rooms)):
        if rooms[index]["id"] == room_id:
            target_index = index
            break
            
    if target_index == -1:
        raise HTTPException(status_code=404, detail="Room not found")
        
    deleted_room = rooms.pop(target_index)
    return {"message": "Xóa phòng học thành công", "data": deleted_room}



@app.get("/room-bookings")
def get_room_bookings():
    return room_bookings


@app.post("/room-bookings", status_code=status.HTTP_201_CREATED)
def create_booking(payload: BookingModel):
    
    
    target_room = None
    for r in rooms:
        if r["id"] == payload.room_id:
            target_room = r
            break
            
    if target_room is None:
        raise HTTPException(status_code=400, detail="Phòng học (room_id) không tồn tại trên hệ thống")
        
    if target_room["status"] != "AVAILABLE":
        raise HTTPException(status_code=400, detail="Phòng học đang bận hoặc đang bảo trì, không thể đặt lịch")
        
    if payload.student_count <= 0:
        raise HTTPException(status_code=400, detail="Số lượng học viên phải lớn hơn 0")
        
    if payload.student_count > target_room["capacity"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Số học viên ({payload.student_count}) vượt quá sức chứa của phòng ({target_room['capacity']})"
        )
        
    valid_slots = ["MORNING", "AFTERNOON", "EVENING"]
    if payload.slot.upper() not in valid_slots:
        raise HTTPException(status_code=400, detail="Ca học (slot) không hợp lệ")
        
    for b in room_bookings:
        if b["room_id"] == payload.room_id and b["date"] == payload.date and b["slot"].upper() == payload.slot.upper():
            raise HTTPException(
                status_code=400, 
                detail="Phòng học này đã có lớp đặt vào ca và ngày này rồi"
            )
            
    new_booking_id = 1
    if room_bookings:
        max_id = room_bookings[0]["id"]
        for b in room_bookings:
            if b["id"] > max_id:
                max_id = b["id"]
        new_booking_id = max_id + 1
        
    new_booking = {
        "id": new_booking_id,
        "room_id": payload.room_id,
        "class_name": payload.class_name,
        "student_count": payload.student_count,
        "date": payload.date,
        "slot": payload.slot.upper()
    }
    room_bookings.append(new_booking)
    return {"message": "Đặt lịch phòng học thành công", "data": new_booking}