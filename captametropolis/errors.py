class _CustomException(Exception):
    def __init__(self, message: str):
        self.__message__ = message
        super().__init__(self.__message__)

    @property
    def message(self):
        return self.__message__


class UtilityNotFoundError(_CustomException):
    def __init__(self, utility: str):
        super().__init__(
            f"Utility '{utility}' not found. Please make sure the utility is installed. For more information view the README.md file."
        )
