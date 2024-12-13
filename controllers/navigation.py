class NavigationController:
    def __init__(self):
        self.start_point = ['view-start']

    @staticmethod
    def get_navigation(context):
        return context.user_data['navigation'] \
            if 'navigation' in context.user_data else False

    @staticmethod
    def get_current_location(context):
        return context.user_data['navigation'][-1]

    @staticmethod
    def get_current_route(context):
        return ''.join(context.user_data['navigation'])

    @staticmethod
    def back(context):
        return context.user_data['navigation'].pop()

    @staticmethod
    def add_location(context, location):
        if len(context.user_data['navigation']) == 0 or context.user_data['navigation'][-1] != location:
            context.user_data['navigation'].append(location)
