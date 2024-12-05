class CategoryController:
    def __init__(self, category_model, product_model):
        self.category_model = category_model
        self.product_model = product_model

    def get_category(self, category_id):
        return self.category_model.get(category_id)

    def get_categories(self, category_id=None):
        if not category_id:
            return self.category_model.get_parent_categories()
        return self.category_model.get_category_children(category_id)

    def get_category_products(self, category_id):
        return self.product_model.get_category_products(category_id)

    def get_category_inner(self, category_id=None):
        categories = self.get_categories(category_id)
        products = self.get_category_products(category_id)
        return {
            'categories': categories,
            'products': products
        }
