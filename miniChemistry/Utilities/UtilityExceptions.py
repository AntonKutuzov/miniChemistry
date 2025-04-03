from miniChemistry.MiniChemistryException import MiniChemistryException


class UtilityException(MiniChemistryException):
    pass

class FileException(UtilityException):
    pass


class KeywordNotAllowed(UtilityException):
    def __init__(self, *keywords: str, variables: dict, func_name: str):
        """
        :param keywords: all the keywords that the keywords_check function marked as not allowed
        :param variables: locals() from where the initial function was called
        :param func_name: function from where the keywords_check was called (so that it is easier for us to find an error)
        """
        self._message = f'\nThe keyword(s) "{', '.join(list(keywords))}" is (are) not allowed for the function "{func_name}".'
        self.description = (f'Check for typos in the keyword you wanted to pass to the function. You can always check \n'
                            f'the allowed keywords in the documentation of the miniChemistry module.')
        super().__init__(variables)


class TypeHintNotFound(UtilityException):
    def __init__(self, func_name: str, hint_type: str, variables: dict):
        if hint_type not in {'return', 'parameter'}:
            raise Exception('The hint type for the TypeHintNotFound exception should be either "return" or "parameter".')

        self._message = f'\nThe {hint_type} type hint for the function called "{func_name}" is not found.'
        self.description = ''
        super().__init__(variables)


class UnknownFileTest(FileException):
    def __init__(self, test_name: str, variables: dict):
        self._message = f'\nThe File class does not have a test called "{test_name}".'
        self.description = (f'\nIf you implemented a new test, check that you have also added it to the _tests dict\n'
                            f'so that the class sees it.')
        super().__init__(variables)

    


class FileNotBound(FileException):
    def __init__(self, variables: dict):
        self._message = f'\nThe text file you are trying to access is not bound (created or linked to).'
        self.description = f'\nCheck that you called .bind() method with the expected file name.'
        super().__init__(variables)

    


class TextNotPresentInFile(FileException):
    def __init__(self, text: str, file_name: str, variables: dict):
        self._message = f'\nThe text "{text}" is not found in the file called "{file_name}".'
        self.description = ''
        super().__init__(variables)

    


class FileAlreadyBound(FileException):
    def __init__(self, file_name: str, variables: dict):
        self._message = f'\nThe file called "{file_name}" is already bound.'
        self.description = (f'\nIf you want to re-bind the file, call .delete() method first. NOTE: this method will\n'
                            f'permanently delete the file and all its content. If this is not what you wanted,\n'
                            f'create another instance of File.')
        super().__init__(variables)

    


class IndexOutOfRange(FileException):
    def __init__(self, index: str, file_name: str, variables: dict):
        self._message = f'\nThere is no a string at a position {index} in the file called "{file_name}".'
        self.description = ''
        super().__init__(variables)

    


class SplitterInText(FileException):
    def __init__(self, text: str, splitter: str, variables: dict):
        self._message = f'\nA splitter "{splitter}" was found in text "{text}".'
        self.description = (f'\nYou must avoid embedding splitters in the text, because the class will treat your\n'
                            f'text as two separate strings. For example if the splitter is a comma ",", then the\n'
                            f'string "a, b, c" will be treated as three different string "a", " b", and " c".\n'
                            f'If you want to append/write/erase to/from the file strings containing splitters,'
                            f'then set the File.slitter_check attribute to False.')
        super().__init__(variables)

    
