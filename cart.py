from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import database, models, schemas, auth_utils

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("/", response_model=List[schemas.CartOut])
def get_cart(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth_utils.get_current_user)):
    return db.query(models.Cart).filter(models.Cart.user_id == current_user.id).all()

@router.post("/add", response_model=schemas.CartOut)
def add_to_cart(cart_item: schemas.CartBase, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth_utils.get_current_user)):
    # Check if product exists
    product = db.query(models.Product).filter(models.Product.id == cart_item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if item already in cart
    existing_item = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id,
        models.Cart.product_id == cart_item.product_id
    ).first()
    
    if existing_item:
        existing_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        new_item = models.Cart(
            user_id=current_user.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

@router.delete("/{cart_id}")
def remove_from_cart(cart_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth_utils.get_current_user)):
    item = db.query(models.Cart).filter(models.Cart.id == cart_id, models.Cart.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    db.delete(item)
    db.commit()
    return {"detail": "Item removed from cart"}

@router.put("/{cart_id}")
def update_cart_quantity(cart_id: int, quantity: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth_utils.get_current_user)):
    item = db.query(models.Cart).filter(models.Cart.id == cart_id, models.Cart.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item
