from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
import database, models, schemas, auth_utils

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=schemas.OrderOut)
def place_order(order_data: schemas.OrderCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth_utils.get_current_user)):
    # Get all cart items for current user
    cart_items = db.query(models.Cart).filter(models.Cart.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total = 0
    # Calculate total and check stock
    for item in cart_items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product or product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name if product else 'unknown product'}")
        total += product.price * item.quantity
    
    # Create order
    new_order = models.Order(
        user_id=current_user.id, 
        total=total, 
        status="completed", 
        payment_method=order_data.payment_method
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # Create order items and update stock
    for item in cart_items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price
        )
        db.add(order_item)
        product.stock -= item.quantity
        # Remove from cart
        db.delete(item)
    
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/", response_model=List[schemas.OrderOut])
def get_orders(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth_utils.get_current_user)):
    query = db.query(models.Order).options(
        joinedload(models.Order.user),
        joinedload(models.Order.items).joinedload(models.OrderItem.product)
    )
    if current_user.role == "admin":
        return query.join(models.User).filter(models.User.role == 'user').all()
    return query.filter(models.Order.user_id == current_user.id).all()

@router.get("/stats")
def get_order_stats(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth_utils.get_admin_user)):
    total_sales = db.query(models.Order).join(models.User).filter(
        models.Order.status == "completed",
        models.User.role == "user"
    ).all()
    total_amount = sum(order.total for order in total_sales)
    total_orders = len(total_sales)
    total_users = db.query(models.User).filter(models.User.role == "user").count()
    total_products = db.query(models.Product).count()
    
    return {
        "total_amount": total_amount,
        "total_orders": total_orders,
        "total_users": total_users,
        "total_products": total_products
    }
