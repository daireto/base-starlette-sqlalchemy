"""This module provides the ``DocstringParser`` class
to parse a docstring.
"""

import re
from collections.abc import Callable
from dataclasses import asdict, dataclass
from enum import Enum, auto
from typing import Any, Literal, overload


class DocstringSection(Enum):
    PARAMETERS = auto()
    QUERY = auto()
    RESPONSES = auto()


@dataclass
class DocstringParsedDescription:
    short_description: str
    long_description: str


@dataclass
class DocstringParsedElement(DocstringParsedDescription):
    type_hint: str


@dataclass
class DocstringParsedParam(DocstringParsedElement):
    name: str
    optional: bool
    default: str | None


@dataclass
class DocstringParsedResponse(DocstringParsedElement):
    status_code: str


@dataclass
class Docstring:
    description: DocstringParsedDescription
    parameters: list[DocstringParsedParam]
    query: list[DocstringParsedParam]
    responses: list[DocstringParsedResponse]

    def to_dict(self) -> dict[str, Any]:
        """Returns docstring as dict."""
        return asdict(self)

    def get_full_description(self) -> str:
        """Returns the full description."""
        return (
            f'{self.description.short_description}\n\n'
            F'{self.description.long_description}'
        )

    def get_parameters_as_dict(self) -> dict[str, dict[str, Any]]:
        """Returns parameters as dict."""
        return {param.name: asdict(param) for param in self.parameters}

    def get_query_as_dict(self) -> dict[str, dict[str, Any]]:
        """Returns query parameters as dict."""
        return {param.name: asdict(param) for param in self.query}


class EndpointDocstringParser:
    """Parses the docstring of an endpoint into its sections.

    Docstring format should be as follows::

        def func(param1, param2, ..., query_param1, query_param2, ...):
            '''
            Endpoint description.

            Long description of endpoint:
                - Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                - Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                - Lorem ipsum dolor sit amet, consectetur adipiscing elit.

            More lorem ipsum.
            And so many more...

            ### Parameters:
                param1 : str
                    Description of param1.

                    Long description of param1.
                    Long description of param1.

                    Long description of param1.
                param2 : str
                    Description of param2.

                    Long description of param2.

            ### Query:
                skip : int | None
                    Description of skip.

                    Long description of skip.
                    Long description of skip.

                    Long description of skip.
                limit : int
                    Description of limit.

                    Long description of limit.

            ### Responses:
                200 : PingResponse
                    Ping response.

                    Long description of response.
                400 : ErrorResponse
                    Error response.

                    Long description of response.
            ...

            '''
    """

    __SECTION_NAMES = {
        DocstringSection.PARAMETERS.value: 'Parameters',
        DocstringSection.QUERY.value: 'Query',
        DocstringSection.RESPONSES.value: 'Responses',
    }
    """Section names."""

    __SECTION_REGEX = r'### {section}:?\n(.*?)(?=#{3}|\Z)'
    """Section regex."""

    __PARAM_REGEX = (
        r'(\w+) : ([\w|,=\"\'\[\]\<\> ]+)\n\s+([^\n]+)\n(.+?)(?=\w+ : \w+|\Z)'
    )
    """Parameter regex."""

    __RESPONSE_REGEX = r'(\d{3}) : ([\w|,=\"\'\[\]\<\> ]+)\n\s+([^\n]+)\n(.+?)(?=\w+ : \w+|\Z)'
    """Response regex."""

    __PARAM_DEFAULT_REGEX = r'(?:, *default *[= ] *([^\n]+))'
    """Parameter default regex."""

    def __init__(self, func_or_docstring: str | Callable) -> None:
        """Initializes the parser.

        Parameters
        ----------
        func_or_docstring : str | Callable
            Function or docstring.
        """
        if isinstance(func_or_docstring, str):
            self.docstring = func_or_docstring
        else:
            self.docstring = func_or_docstring.__doc__ or ''
        self._compile_patterns()

    def parse(self) -> Docstring:
        """Parses the docstring.

        Returns
        -------
        Docstring
            Parsed docstring.
        """
        return Docstring(
            description=self.parse_description(),
            parameters=self.parse_section(DocstringSection.PARAMETERS),
            query=self.parse_section(DocstringSection.QUERY),
            responses=self.parse_section(DocstringSection.RESPONSES),
        )

    def _compile_patterns(self) -> None:
        """Compiles the regex patterns."""
        self._section_patterns = {
            k: self._compile_section_pattern(v)
            for k, v in self.__SECTION_NAMES.items()
        }
        self._param_pattern = re.compile(self.__PARAM_REGEX, re.DOTALL)
        self._response_pattern = re.compile(self.__RESPONSE_REGEX, re.DOTALL)

    def _compile_section_pattern(self, section: str) -> re.Pattern:
        """Compiles a section regex.

        Parameters
        ----------
        section : str
            Section name.

        Returns
        -------
        re.Pattern
            Compiled regex.
        """
        return re.compile(
            self.__SECTION_REGEX.replace('{section}', section), re.DOTALL
        )

    def parse_description(self) -> DocstringParsedDescription:
        """Parses the description section.

        Returns
        -------
        DocstringParsedDescription
            Description.
        """
        first_section_end = self.docstring.find('###')
        full_description = (
            self.docstring[:first_section_end].strip()
            if first_section_end != -1
            else self.docstring.strip()
        )
        splitted = full_description.split('\n')
        return DocstringParsedDescription(
            short_description=splitted[0].strip(),
            long_description='\n'.join(splitted[1:]).strip(),
        )

    @overload
    def parse_section(
        self,
        section: Literal[DocstringSection.PARAMETERS, DocstringSection.QUERY],
    ) -> list[DocstringParsedParam]: ...

    @overload
    def parse_section(
        self, section: Literal[DocstringSection.RESPONSES]
    ) -> list[DocstringParsedResponse]: ...

    def parse_section(
        self, section: DocstringSection
    ) -> list[DocstringParsedParam] | list[DocstringParsedResponse]:
        """Parses a docstring section,

        Sections are delimited by ### markers and have the following format:

        .. code-block:: python
            ### {section}:
            param1 : str
                Short description of param1.

                Long description of param1...
            param2 : int
                Short description of param2.

                Long description of param2...
            ...

        Parameters
        ----------
        section : DocstringSection
            Section.

        Returns
        -------
        List[DocstringParsedParam]
            List of parameters.
        List[DocstringParsedResponse]
            List of responses.
        """
        match = self._section_patterns[section.value].search(self.docstring)
        if not match:
            return []

        section_text = match.group(1)
        if (
            section == DocstringSection.PARAMETERS
            or section == DocstringSection.QUERY
        ):
            return self.parse_params(section_text)
        elif section == DocstringSection.RESPONSES:
            return self.parse_responses(section_text)
        else:
            return []

    def parse_params(self, param_section: str) -> list[DocstringParsedParam]:
        """Parses parameter or query sections.

        Parameters
        ----------
        param_section : str
            Parameters or query section.

        Returns
        -------
        List[DocstringParsedParam]
            List of parameters.
        """
        if not param_section:
            return []

        matches = re.findall(self._param_pattern, param_section)
        params = []
        for name, param_type, short_desc, long_desc in matches:
            type_hint = (
                param_type.split(',')[0] if ',' in param_type else param_type
            )
            params.append(
                DocstringParsedParam(
                    name=name,
                    type_hint=type_hint,
                    optional='none' in param_type.lower(),
                    default=self._extract_param_default(param_type),
                    short_description=short_desc.strip(),
                    long_description=long_desc.strip(),
                )
            )

        return params

    def _extract_param_default(self, param_type: str) -> str | None:
        """Extracts the default value of a parameter.

        Parameters
        ----------
        param_type : str
            Parameter type.

        Returns
        -------
        str | None
            Default value.
        """
        match = re.search(self.__PARAM_DEFAULT_REGEX, param_type)
        if not match:
            return None

        value = match.group(1)
        if not value:
            return None

        if value.startswith("'") or value.startswith('"'):
            value = value[1:]
        if value.endswith("'") or value.endswith('"'):
            value = value[:-1]

        return None if value.lower() == 'none' else value

    def parse_responses(
        self, responses_section: str
    ) -> list[DocstringParsedResponse]:
        """Parses the responses section.

        Parameters
        ----------
        responses_section : str
            Responses section.

        Returns
        -------
        List[DocstringParsedResponse]
            List of responses.
        """
        if not responses_section:
            return []

        matches = re.findall(self._response_pattern, responses_section)
        responses = []
        for status_code, response_type, short_desc, long_desc in matches:
            responses.append(
                DocstringParsedResponse(
                    status_code=status_code,
                    type_hint=response_type,
                    short_description=short_desc.strip(),
                    long_description=long_desc.strip(),
                )
            )

        return responses
