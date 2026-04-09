from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from .core.config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_HOURS

# password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    # bcrypt has a 72-byte limit, truncate if necessary
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    
    # Use passlib for proper bcrypt hashing with fallback
    try:
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Bcrypt hashing failed: {e}")
        # Fallback to SHA256 if bcrypt fails
        import hashlib
        sha256_hash = hashlib.sha256(password.encode()).hexdigest()
        print(f"Using SHA256 fallback: {sha256_hash[:30]}...")
        return sha256_hash

def verify_password(plain_password, hashed_password):
    print("Password verification debug:")
    print("Input password:", plain_password)
    print("Stored hash:", hashed_password[:50] + "..." if len(hashed_password) > 50 else hashed_password)
    
    # First try direct comparison (for existing plain text passwords)
    if plain_password == hashed_password:
        print("Direct comparison succeeded - plain text password")
        return True
    
    # Then try bcrypt verification
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        print(f"Bcrypt verification result: {result}")
        return result
    except Exception as e:
        print(f"Bcrypt verification failed: {e}")
        
        # Fallback to SHA256 verification
        try:
            import hashlib
            sha256_hash = hashlib.sha256(plain_password.encode()).hexdigest()
            print(f"SHA256 hash: {sha256_hash[:50]}...")
            print(f"SHA256 matches: {sha256_hash == hashed_password}")
            return sha256_hash == hashed_password
        except Exception as e2:
            print(f"SHA256 verification failed: {e2}")
            return False

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

# token reader
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return email

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")