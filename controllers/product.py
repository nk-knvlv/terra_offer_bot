from models.product import ProductModel


class ProductController:
    def __init__(self, product_model: ProductModel):
        self.product_model = product_model

    def get_all(self):
        return self.product_model.get_all_products()

    def get_products_by_category(self, category):
        return self.product_model.get_products_by_category(category)

