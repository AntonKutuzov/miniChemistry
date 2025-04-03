"""
This class is defined to handle simple operations on small text files.
NOTE: the files should not be large, because the program loads all the content of a file at once and then treats it as
a list.
Primary purpose of this class then is to keep lists that the code will use separately, and away from the real code. This
makes it easier to edit the lists as they might need to be updated.
The class has a couple of tests (private methods that returns True/False or raise exception) that are used in many other
methods, and one private method that is called to run these tests (see the class).
The class implements simple operations on files as well as lists (because the content of the file is treated just as
a list of strings).

NOTE: before working with the file, it is necessary to call .bind() method to either create a file or to connect to it.
"""


from pathlib import Path
from typing import List, Any

from miniChemistry.MiniChemistryException import NotSupposedToHappen

from miniChemistry.Utilities.UtilityExceptions import UnknownFileTest, FileNotBound, TextNotPresentInFile, \
    IndexOutOfRange, SplitterInText


class File:
    # ==================================================================================================== MAGIC METHODS
    
    def __init__(self, caller: str = __file__, splitter: str = '\n') -> None:
        """
        Introduces several important variables for the File class as well as derives the path of the new text file.
        The _caller, _caller_name and _caller_path are the properties of the __file__. Hence, the path is then used to
        derive the path of the .txt file.

        The _file variables is left as None and is assigned a text file in the .bind() method.

        The _tests dict stores private methods that are used as checks (tests) for public methods. The implementation
        is done in this way to allow multiple testing by one command.

        :param caller: The __file__ variable of the .py file next to which the .txt file has to be formed. If left
        unfilled, the .txt file will be formed next to the .py file with implementation of this class!
        :param splitter: The string that is used to separate several items in the file. New line symbol is used by default.
        """


        self._caller = Path(caller)

        self._caller_name = self._caller.name
        self._caller_path = self._caller.resolve()
        self._caller_dir = self._caller_path.parent
        self._file = None

        self._splitter = splitter
        self._splitter_check = True

        self._tests = {
            "file bound": self._file_bound_test,
            "in file present": self._in_file_present_test,
            "splitter test": self._no_splitter_test
        }

    def __iter__(self):
        return self._get_items().__iter__()

    def __getitem__(self, item):
        return self.read_index(item)

    def __str__(self):
        return self._file.read_text()


    # =================================================================================================== METHOD TESTING
    def _test_for(self, tests: List[str], **kwargs: Any) -> bool:
        """
        The function uses self._tests dict to call the respective private methods all of which return either True, False
        or raise an exception (by default). Some methods (tests) might need additional arguments, so each receives
        a **kwargs argument. In some methods this argument is not used and is added only to avoid errors in this method.

        Currently, the File class has two tests:
        _file_bound_test – checks that the instance of File is actually linked to a text file (_file is not None)
        _in_file_present_test – checks that the given string ("text" parameter) is present in the bound .txt file
        (see important note in the method's definition)

        :param tests: strings that are keys to the _tests dict, each string indicating a separate test
        :param kwargs: keyword parameters that any of the tests might need. Parameters for different tests can be passed
        together for this function.
        :return: returns True if all tests were passed, or False if raise_exception parameter was set to False. Otherwise
        raises an exception.
        """

        results = list()
        for test in tests:
            try:
                res = self._tests[test](**kwargs)  # we are calling a lambda function!
            except KeyError:
                raise UnknownFileTest(test_name=test, variables=locals())
            results.append(res)
        return all(results)

    
    def _file_bound_test(self, *, raise_exception: bool = True, **kwargs: Any) -> bool:
        """
        The kwargs argument is needed here, because all the tests are called by a single function _test_for(), and
        since the tests have different arguments, all of them are made keyword arguments. Now if one tests needs an
        argument and another does not, the other will just ignore it, but the argument will be passed to it anyway.
        This makes it possible to run all necessary tests in one line of code (when _test_for() is called in any
        method).
        """

        if self._file is None:
            if raise_exception:
                raise FileNotBound(variables=locals())
            else:
                return False
        return True

    
    def _in_file_present_test(self, *, text, raise_exception: bool = True, **kwargs: Any) -> bool:
        """
        Test that checks whether a given string is present in the bound file.
        NOTE: this test assumes that the file is bound (i.e. .bind() method has already been called). That means, it
        should always come after ._file_bound_test(). Otherwise,

        :param text: string to be checked for presence in the file
        :param raise_exception: True if the exception has to be risen if the test returns False
        :param kwargs: is left here to account for keyword arguments required for other tests
        :return: True if the test is passed, False if the test is failed AND raise_exception parameter was set to True
        Otherwise, returns False.
        """

        present = text in self._get_items()

        if present:
            return True
        elif raise_exception:
            raise TextNotPresentInFile(text=text, file_name=self._file.name, variables=locals())
        else:
            return False


    
    def _no_splitter_test(self, text: str, raise_exception: bool = True, **kwargs: Any) -> bool:
        if not self._splitter_check:
            return True

        if self.splitter in text:
            if raise_exception:
                raise SplitterInText(text=text, splitter=self.splitter, variables=locals())
            else:
                return False
        else:
            return True


    # ============================================================================================ OTHER PRIVATE METHODS
    def _get_items(self) -> List[str]:
        """
        The method returns a list of strings, consisting of strings present in the file. The text of the file is split
        by passing self.splitter into list's split() function.

        :return: a list of strings composed of all strings written into the file
        """

        self._test_for(['file bound'])
        content = self._file.read_text()
        content = content.strip(self.splitter)
        items = content.split(self.splitter)

        if items == ['']:
            return list()
        else:
            return items


    # =================================================================================================== PUBLIC METHODS
    
    def bind(self, file_name: str) -> None:
        """
        Assigns a variable self._file a value of type Path. The path for the file is composed from the caller's path,
        plus the name of the file. In the case the file does not exist, it will be created, in the case the file exists,
        it will be assigned to the self._file variable.
        NOTE: include the file extension in the file name. Not testfile, but testfile.txt!

        :param file_name: name of the file, including extension (.txt)
        :return:
        """

        file_path = Path(self._caller_dir / file_name)
        if not file_path.exists():
            self._file = file_path
            self._file.touch()
        if file_path.exists():
            self._file = file_path
        else:  # technically should never be called
            raise NotSupposedToHappen(variables=locals())

    
    def read_index(self, index: int) -> str:
        """
        Returns a string located in the file at a certain position (index)

        :param index: position of the string to be returned
        :return: the string at the position equal to index
        """

        self._test_for(['file bound'])
        items = self._get_items()

        try:
            return items[index]
        except IndexError:
            raise IndexOutOfRange(index=str(index), file_name=self._file.name, variables=locals())

    def read_all(self) -> List[str]:
        """Just a public implementation of self._get_items(). Includes a test for whether a file is bound."""

        self._test_for(['file bound'])
        return self._get_items()

    
    def write(self, text: str, add_splitter: bool = True) -> None:
        """
        Writes (overwrites!) a given string (parameter "text") to the existing (bound) file. The
        add_splitter argument has to be set False in several cases (for example, in the erase_index method,
        but usually this should be True.
        NOTE: if add_splitter is set to False and then append() method is called, the two texts will be considered
        as one.

        :param text: string to be written into the file
        :param add_splitter: True is the splitter has to be added after the text. True by default
        :return:
        """
        self._test_for(['file bound', 'splitter test'], text=text)
        to_write = text + (self.splitter if add_splitter else '')
        self._file.write_text(to_write)

    
    def append(self, text: str, add_splitter: bool = True) -> None:
        """
        Appends a given string (parameter "text") to the existing (bound) file.

        :param text: string to be appended to the file
        :param add_splitter: True is the splitter has to be added after the text. True by default
        :return:
        """

        self._test_for(['file bound', 'splitter test'], text=text)
        with self._file.open("a") as file:
            to_append = text + (self.splitter if add_splitter else '')
            file.write(to_append)

    
    def find(self, text: str) -> bool:
        """
        Checks if a given string is present in the file. Works also for sequences, connected by self.splitter.

        :param text: string for which the file is checked
        :return:
        """

        self._test_for(['file bound', 'in file present', 'splitter test'], text=text)
        return text in self._file.read_text()

    
    def index(self, text: str) -> int:
        """
        Searches for the position of the string given in the "text" parameter. Returns the smallest index (first
        occurrence). For all occurrences, use self.positions().
        NOTE: unlike .find(), this method does not support search for sequences of strings connected with self.splitter

        :param text: string which position must be found
        :return: position of the first occurrence of the string in the file
        """

        self._test_for(['file bound', 'in file present', 'splitter test'], text=text)
        items = self._get_items()
        index = items.index(text)
        return index

    
    def positions(self, text: str) -> List[int]:
        """
        Searches for ALL occurrences of the string passed as the "text" parameter. Returns a list of the indices (ints).
        NOTE: unlike .find(), this method does not support search for sequences of strings connected with self.splitter

        :param text: string which positions (all) must be found
        :return: A list of positions where the string was found
        """

        self._test_for(['file bound', 'in file present', 'splitter test'], text=text)
        items = self._get_items()
        indices = list()
        current_index = 0

        for item in items:
            if item == text:
                indices.append(current_index)
            current_index += 1

        return indices

    
    def erase_text(self, text: str) -> None:
        """
        Removes a string passed as a "text" parameter from the file. Does not support string sequences, connected by
        self.splitter. This method removes ALL occurrences of the string from the file.

        :param text: string that has to be removed from the file
        :return:
        """

        self._test_for(['file bound', 'in file present', 'splitter test'], text=text)
        items = self._get_items()

        while text in items:
            items.remove(text)

        self.erase_all()
        if items:
            for item in items:
                self.append(item)
        # self.write(new_string)  # write_text rewrites the file completely

    
    def erase_index(self, index: int) -> str:
        """
        Erases a string located at a certain position.

        :param index: position where the string must be erased
        :return: erased string
        """

        self._test_for(['file bound'])
        items = self._get_items()
        try:
            popped = items.pop(index)
            self.erase_all()
            if items:
                for item in items:
                    self.append(item)

            return popped
        except IndexError:
            raise IndexOutOfRange(index=str(index), file_name=self._file.name, variables=locals())

    def erase_all(self) -> None:
        """Just erases all the text from the file"""
        self._file.write_text('')

    def delete(self) -> None:
        """Deletes the file"""
        self._test_for(['file bound'])
        self._file.unlink()
        self._file = None


    # ======================================================================================================= PROPERTIES
    @property
    def splitter(self) -> str:
        return self._splitter

    @property
    def splitter_check(self) -> bool:
        return self._splitter_check

    @splitter_check.setter
    
    def splitter_check(self, value: bool) -> None:
        self._splitter_check = value

    @property
    def is_empty(self) -> bool:
        return len(self._get_items()) == 0

    @property
    def caller(self) -> Path:
        return self._caller

    @property
    def caller_directory(self) -> Path:
        return self._caller_dir

    @property
    def caller_name(self) -> str:
        return self._caller_name

    @property
    def name(self) -> str:
        return self._file.name

    @property
    def path(self) -> Path:
        return self._file
