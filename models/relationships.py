from sqlalchemy.orm import relationship

# В отдельном файле, например models.py:c
from .product import ProductModel
from .category import CategoryModel
from .cart_product import CartProductModel


CartProductModel.product = relationship("ProductModel")
ProductModel.category = relationship("CategoryModel", back_populates="products")
CategoryModel.products = relationship("ProductModel", back_populates="category")
