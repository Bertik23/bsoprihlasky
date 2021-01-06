class Dummy:
    def __init__(self, **kwargs):
        for i in kwargs:
            setattr(self, i, kwargs[i])