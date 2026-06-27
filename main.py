from fastapi import FastAPI, HTTPException, Depends
from jose import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext


app = FastAPI()

#JWT Config
SECRET_KEY = "mysecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#Password Hashing setup
pwd_contaxt = CryptContext(schemes=["bcrypt"], deprecated = "auto")

#OauthSetup
oauth2_schema = OAuth2PasswordBearer(tokenUrl = "login")

#Dummy User DB
fake_users_db = {
    "admin": {
        "username" : "admin",
        "hashed_password" : pwd_contaxt.hash("1234")
    }
}


#Hash Password
def hash_password(password:str):
    return pwd_contaxt.hash(password)

#Verify Password
def verify_password(plain_password, hased_password):
    return pwd_contaxt.verify(plain_password, hased_password)

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
    
#Login API (OAuth2 Form) 
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password,user['hashed_password']):
        raise HTTPException(
            status_code = 400,
            detail = "invalid credentials"
        )
    access_token = create_token({"sub":form_data.username})
    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }
#Token varify
def verify_token(token:str = Depends(oauth2_schema)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code = 401,
                detail = "invalid authentication"
            )
        return username
    except jwt.JWTError:
        raise HTTPException (
            status_code = 401,
            detail = "invalid authentication"
        )

#Protected Route
@app.get("/protected")
def protected_route(username: str = Depends(verify_token)):
    return {
        "message": f"Hello {username}, you have access to protected data!",
        "user": username
    }  

#10:35 