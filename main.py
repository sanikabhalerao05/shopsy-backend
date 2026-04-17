from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import models, database, os
from routes import auth, users, products, cart, orders

# Create tables
models.Base.metadata.create_all(bind=database.engine)

# Create uploads directory if it doesn't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")
if not os.path.exists("uploads/profile_photos"):
    os.makedirs("uploads/profile_photos")

app = FastAPI(title="ShopsyHub API Engine", version="1.0.0")

# Mount uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to ShopsyHub E-Commerce API"}
