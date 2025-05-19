from fastapi import Request, HTTPException, Depends
from app.core.session_state import session_store

def get_current_user(request: Request):
    user_id = request.headers.get("x-user-id")
    if not user_id or int(user_id) not in session_store:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return int(user_id)
