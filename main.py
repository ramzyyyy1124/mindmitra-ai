from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import models, schemas, database
from auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
import auth
from jose import jwt
from datetime import timedelta

from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="MindMitra AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Auth Routes ---
@app.post("/api/auth/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = models.User(email=user.email, name=user.name, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Child Routes ---
@app.post("/api/children", response_model=schemas.Child)
def create_child(child: schemas.ChildCreate, db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    # Basic token parsing (in real app, use a dedicated dependency)
    payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    email = payload.get("sub")
    user = db.query(models.User).filter(models.User.email == email).first()
    
    new_child = models.Child(**child.model_dump(), parent_id=user.id)
    db.add(new_child)
    db.commit()
    db.refresh(new_child)
    return new_child

@app.get("/api/children", response_model=list[schemas.Child])
def get_children(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    email = payload.get("sub")
    user = db.query(models.User).filter(models.User.email == email).first()
    
    return db.query(models.Child).filter(models.Child.parent_id == user.id).all()

# --- Activity Log Routes ---
from ml_pipeline import predict_stress
import sys
sys.path.append('.') # Ensure utils can be imported
from utils.recommendations import get_recommendation

@app.post("/api/activity/{child_id}", response_model=schemas.ActivityLog)
def log_activity(child_id: int, activity: schemas.ActivityLogCreate, db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    # Verify child belongs to user
    payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    user = db.query(models.User).filter(models.User.email == payload.get("sub")).first()
    child = db.query(models.Child).filter(models.Child.id == child_id, models.Child.parent_id == user.id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    # Run ML Prediction
    features = {
        "mood": activity.mood,
        "sleep_duration": activity.sleep_duration,
        "screen_time": activity.screen_time,
        "activity_level": activity.activity_level
    }
    score, level, explanation = predict_stress(features)
    recommendation = get_recommendation(level)
    
    # We'll prepend explanation to the recommendation for simplicity, 
    # or you could update the schema to have a dedicated explanation field.
    # For now, let's just log it or add it if needed.
    
    new_activity = models.ActivityLog(
        **activity.model_dump(), 
        child_id=child_id,
        predicted_stress_level=level,
        stress_score=score
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    
    # Return additional data as headers or wrap it, but sticking to schema for now
    # We could extend schema to return recommendations.
    return new_activity

@app.get("/api/activity/{child_id}", response_model=list[schemas.ActivityLog])
def get_activity_logs(child_id: int, db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    user = db.query(models.User).filter(models.User.email == payload.get("sub")).first()
    child = db.query(models.Child).filter(models.Child.id == child_id, models.Child.parent_id == user.id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
        
    return db.query(models.ActivityLog).filter(models.ActivityLog.child_id == child_id).order_by(models.ActivityLog.date.desc()).all()
