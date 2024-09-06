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


class FontNotRegisteredError(_CustomException):
    def __init__(self, font: str):
        super().__init__(
            f"Font '{font}' is not registered. Please register the font using 'register_font_path()' before using it."
        )
