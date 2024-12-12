class NavigationController:
    def __init__(self):
        self.navigation = ['start']

    def get_current_location(self):
        return self.navigation[-1]

    def get_current_route(self):
        return self.navigation[-1]

    def back(self):
        return self.navigation.pop()

    def set_start(self):
        self.navigation = ['start']

    def add_location(self, location):
        self.navigation.append(location)
