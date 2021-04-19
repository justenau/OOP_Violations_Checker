import abc
from abc import abstractmethod


class InformalParserInterface:
    __attr__ = "This is an interface test"

    def load_data_source(self, path: str, file_name: str) -> str:
        """Load in the file for extracting text."""
        pass

    def extract_text(self, full_file_name: str) -> dict:
        """Extract text from the currently loaded file."""
        pass

    def close_data_source(self, path: str, file_name: str) -> str:
        pass


class TestInterface:
    def test_method(self):
        pass

    def another_method(self):
        raise NotImplementedError()


class AnotherTestInterface:
    @abstractmethod
    def another_method(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def decorated_method(self):
        pass


class PdfParser(InformalParserInterface):
    """Extract text from a PDF"""
    def load_data_source(self, path: str, file_name: str) -> str:
        """Overrides InformalParserInterface.load_data_source()"""
        return 'Loaded'

    def extract_text(self, full_file_path: str) -> dict:
        """Overrides InformalParserInterface.extract_text()"""
        return dict('Extracted')

    def close_data_source(self, path: str, file_name: str) -> str:
        """Overrides InformalParserInterface.extract_text()"""
        return 'Closed'


class SpecificParser(InformalParserInterface):
    def load_data_source(self, path: str, file_name: str) -> str:
        """Overrides InformalParserInterface.load_data_source()"""
        return 'Loaded'

    def extract_text(self, full_file_path: str) -> dict:
        """Overrides InformalParserInterface.extract_text()"""
        return dict('Extracted')


class UnfinishedParser(InformalParserInterface):
    def load_data_source(self, path: str, file_name: str) -> str:
        """Overrides InformalParserInterface.load_data_source()"""
        return 'Loaded'

    def extract_text(self, full_file_path: str) -> dict:
        raise NotImplementedError()

    def close_data_source(self, path: str, file_name: str) -> str:
        pass


class EmptyClass(InformalParserInterface):
    __attr__ = None


class EmptyBaseClass:
    __attr__ = None


class ClassWithTwoInterfaces(TestInterface, AnotherTestInterface):
    def test_method(self):
        return "Implemented"

    def decorated_method(self):
        return "Also implemented"
