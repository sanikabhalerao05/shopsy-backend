import sys
import os

# Add the current directory to sys.path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
import models, database, auth_utils
from datetime import date

def seed_data():
    db = database.SessionLocal()
    
    # 1. Create Admin User (if not exists)
    admin_email = "admin@shopsyhub.com"
    admin = db.query(models.User).filter(models.User.email == admin_email).first()
    if not admin:
        hashed_password = auth_utils.get_password_hash("password123")
        admin = models.User(
            name="Admin User",
            email=admin_email,
            password=hashed_password,
            address="123 Shopping Square, Mumbai",
            contact="9876543210",
            dob=date(1990, 1, 1),
            role="admin",
            status="active"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("Admin user created for ShopsyHub.")

    # 2. Seed Products (Total 12)
    products = [
        {
            "name": "Nebula Elite X1",
            "description": "A high-performance luxury laptop with an ultraviolet backlit keyboard and carbon fiber chassis.",
            "price": 185000.00,
            "stock": 10,
            "image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800"
        },
        {
            "name": "Obsidian Chronograph",
            "description": "A matte-black mechanical watch with sapphire glass and Swiss movement the pinnacle of precision.",
            "price": 65000.00,
            "stock": 5,
            "image": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800"
        },
        {
            "name": "Vortex Soundscapes",
            "description": "Active noise-cancelling headphones featuring spatial audio and a premium leather finish.",
            "price": 32000.00,
            "stock": 20,
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800"
        },
        {
            "name": "Zenith 5G Pro",
            "description": "Next-gen smartphone with an aerospace-grade titanium frame and a liquid-retina display.",
            "price": 112000.00,
            "stock": 15,
            "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800"
        },
        {
            "name": "Titanium Coffee Master",
            "description": "An automated espresso machine that brings artisanal coffee culture to your modern kitchen.",
            "price": 48000.00,
            "stock": 8,
            "image": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800"
        },
        {
            "name": "Artisan Leather Tote",
            "description": "Handcrafted from full-grain Italian leather, designed for the sophisticated traveler.",
            "price": 18500.00,
            "stock": 12,
            "image": "https://images.unsplash.com/photo-1544816155-12df9643f363?w=800"
        },
        {
            "name": "Echo Wave Projector",
            "description": "A 4K smart cinema projector that transforms any wall into a high-fidelity home theater.",
            "price": 74000.00,
            "stock": 6,
            "image": "https://images.unsplash.com/photo-1535016120720-40c646be44da?w=800"
        },
        {
            "name": "Silk Route Pashmina",
            "description": "Woven by master artisans, this rare silk-blend wrap defines timeless elegance.",
            "price": 12000.00,
            "stock": 25,
            "image": "https://images.unsplash.com/photo-1606760227091-3dd870d97f1d?w=800"
        },
        {
            "name": "Nordic Air Purifier",
            "description": "A glassmorphism-inspired air filtration system that combines health with high-end decor.",
            "price": 15500.00,
            "stock": 30,
            "image": "https://images.unsplash.com/photo-1585771724684-252ad5058631?w=800"
        },
        {
            "name": "Stellar Fountain Pen",
            "description": "A limited edition writing instrument with customized nibs and shimmering ultraviolet ink.",
            "price": 7800.00,
            "stock": 40,
            "image": "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=800"
        },
        {
            "name": "Apex Gaming Throne",
            "description": "Engineered for maximum endurance with ergonomic support and premium breathable textiles.",
            "price": 28000.00,
            "stock": 10,
            "image": "https://images.unsplash.com/photo-1598550476439-6847785fce66?w=800"
        },
        {
            "name": "Ultraviolet Lumina",
            "description": "Architectural smart lighting that syncs with your environment for a curated aesthetic.",
            "price": 9500.00,
            "stock": 50,
            "image": "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=800"
        }
    ]

    for p in products:
        # Check if product already exists to avoid duplicates if re-running
        existing = db.query(models.Product).filter(models.Product.name == p["name"]).first()
        if not existing:
            new_prod = models.Product(**p, created_by=admin.id)
            db.add(new_prod)
    
    db.commit()
    print(f"ShopsyHub: Seeded {len(products)} premium products.")
    db.close()

if __name__ == "__main__":
    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=database.engine)
    seed_data()
