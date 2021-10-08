class MovieNotFound(Exception):
    def __init__(self,id,message="Couldn't find a movie with specified id :"):
        self.id = id
        self.message = message + str(id)
        super().__init__(self.message)