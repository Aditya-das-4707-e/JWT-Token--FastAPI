from fastapi import FastAPI, HTTPException, Depends, Header
from jose import jwt
from datetime import datetime, timedelta, timezone
import pytz


app = FastAPI()

SECRET_KEY = "mysecret"
ALGORITHM = "HS256"

# IST = pytz.timezone("Asia/Kolkata")

#Create Token
def create_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({
        "exp":expire
    })
    token = jwt.encode(to_encode,SECRET_KEY, algorithm=ALGORITHM)
    return token
    
#Login API (Token Genrate)
@app.post("/login")
def login(username:str,password:str):
    if username != "aditya" or password != "aditya":
        raise HTTPException(
            status_code = 401,
            detail = "invalid cred"            
        )
    token = create_token({
        "sub":username
    })
    return{
        "access_token":token,
    }

#Token varify
def varify_token(token:str = Header(None)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(
            status_code = 401,
            detail = "invalid token"
        )

#protected Route
@app.get("/secure")
def secure_data(user = Depends(varify_token)):
    return {
        "message" : "this is secure data",
        "user" : user
    }