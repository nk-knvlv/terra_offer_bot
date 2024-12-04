class CategoryController:
    def __init__(self, category_model):
        self.category_model = category_model

    def get_categories(self, category_id=None):
        if not category_id:
            return self.category_model.get_parent_categories()
        return self.category_model.get_parent_categories(category_id)
