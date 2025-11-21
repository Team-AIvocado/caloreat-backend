from fastapi import APIRouter, Depends, HTTPException,status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.schemas.user import UserRead, UserCreate, UserUpdate
from app.db.database import get_db
from app.db.models.user import User
from app.services.user import UserService
from app.db.crud.user import UserCrud
from app.core.auth import oauth2_scheme
from app.core.auth import set_auth_cookies

from app.services.user import UserService
from app.db.crud.user import UserCrud

from typing import Annotated , List


router = APIRouter(prefix="/users", tags=["User"])

# signup
@router.post("/signup", response_model= UserRead)
async def signup(user:UserCreate,db:AsyncSession=Depends(get_db)) -> User:
    db_user = await UserService.register_user(db,user.username, user.email, user.password)
    return db_user

# #회원정보조회
# @router.get("/name/{user_id}", response_model=UserRead)
# async def get_name(user_id:int, db:AsyncSession=Depends(get_db)) ->User:
#     user = await UserCrud.get_id(user_id,db)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail="없는 회원")
#     return user   
# # # delete_user
# @router.delete("/delete/{user_id}")
# async def delete_user(user_id:int,                      
#                       db:AsyncSession=Depends(get_db)):    
#     result = await UserCrud.delete_user_by_id(user_id,db)
#     return {"msg":"회원삭제","deleted":result}
# # user update
# # @router.put("/update/{user_id}")
# # async def update_user_by_id(user:UserUpdate,
# #                             user_id:int,                             
# #                             db:AsyncSession=Depends(get_db)):
# #     result = await UserCrud.update_user_by_id(user,user_id,db)    
# #     return result


# # # login
# # @router.post("/login", response_model=UserLogin)
# # async def login(user:UserLogin, response:Response,db:AsyncSession=Depends(get_db)) -> AuthResponse:
# #     result = await UserService.login(user,db)
# #     verified_staff, access_token, refresh_token = result    
# #     set_auth_cookies(response, access_token, refresh_token)
# #     return AuthResponse(verified_staff=verified_staff ,access_token=access_token, refresh_token=refresh_token)

# # logout
# async def logout(request:Request,response:Response):    
#     response.delete_cookie(key="access_token")
#     response.delete_cookie(key="refresh_token")
#     return True




