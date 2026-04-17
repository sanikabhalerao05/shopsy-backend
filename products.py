from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import database, models, schemas, auth_utils

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[schemas.ProductOut])
def get_products(db: Session = Depends(database.get_db), 
                 min_price: float = None, 
                 max_price: float = None,
                 search: str = None):
    query = db.query(models.Product)
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    if search:
        query = query.filter(models.Product.name.contains(search) | models.Product.description.contains(search))
    return query.all()

@router.post("/", response_model=schemas.ProductOut)
def create_product(product: schemas.ProductCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth_utils.get_admin_user)):
    new_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        image=product.image,
        created_by=current_user.id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth_utils.get_admin_user)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"detail": "Product deleted"}

@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, product_update: schemas.ProductUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth_utils.get_admin_user)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

# Added a detail route for specific product view
@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(database.get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
