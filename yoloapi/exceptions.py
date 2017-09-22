class UnknownParameterType(BaseException):
    def __init__(self, *args, **kwargs):
        super(UnknownParameterType, self).__init__(*args, **kwargs)
