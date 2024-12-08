from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Enum as SQLAEnum, DateTime
from sqlalchemy.orm import relationship, declarative_base
from models.base import Base


class CategoryModel(Base):
    def __init__(self, db=None, name=None, parent=None):
        if db:
            self.connection = db.connection
        if name:
            self.name = name
        if parent:
            self.parent = parent

    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    # Связь с продуктами
    products = relationship("ProductModel", back_populates="category")
    parent = relationship("CategoryModel", remote_side=[id], back_populates="children")
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    # Связь с дочерними категориями
    children = relationship("CategoryModel", back_populates="parent", cascade="all, delete-orphan")

    # Связь с родительской категорией

    def __repr__(self):
        return f"<CategoryModel(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"

    def get_parent_categories(self):
        return self.connection.query(CategoryModel).filter_by(parent_id=None).all()

    def get_category_children(self, parent_category_id):
        return self.connection.query(CategoryModel).filter_by(parent_id=parent_category_id).all()

    def get(self, category_id):
        return self.connection.query(CategoryModel).filter_by(id=category_id).first()
