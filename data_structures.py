class AssignmentGroup:
    def __init__(self, name="no_name", description="no description"):
        self.name = name
        self.description = description
        self.assignments = []

class Assignment:
    def __init__(self, name="no_name", description="no description", background_url=""):
        self.name = name
        self.description = description
        self.background_url = background_url
        self.exercises = []

class Exercise():

    def __init__(self, name="no_name", description="no description", instructions_url=""):
        self.name = name
        self.description = description
        self.instructions_url = instructions_url