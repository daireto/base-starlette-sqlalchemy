"""This module provides the ``StarletteOpenAPI`` class
to generate an OpenAPI spec for a Starlette application.
"""

from inspect import Signature, isclass, signature
from logging import Logger, getLogger
from typing import cast, get_args

from openapi_pydantic import (
    DataType,
    Info,
    MediaType,
    OpenAPI,
    Operation,
    Parameter,
    PathItem,
    Paths,
    Reference,
    RequestBody,
    Response,
    Responses,
    Server,
)
from openapi_pydantic.util import (
    PydanticSchema,
    Schema,
    construct_open_api_with_schema_class,
)
from pydantic import BaseModel
from starlette.applications import Starlette
from starlette.routing import Route
from swagger_ui import api_doc

from .docstring_parser import (
    Docstring,
    DocstringParsedParam,
    EndpointDocstringParser,
)


class StarletteAPISpec:
    """An OpenAPI spec generator for Starlette applications."""

    _app: Starlette
    """Application."""

    _servers: list[str]
    """List of servers."""

    _title: str
    """Title of the API."""

    _version: str
    """Version of the API."""

    _description: str | None
    """Description of the API."""

    _url_prefix: str | None
    """URL prefix of the API docs."""

    _logger: Logger
    """Logger."""

    def __init__(
        self,
        app: Starlette,
        servers: list[str],
        title: str,
        version: str,
        description: str | None = None,
        url_prefix: str | None = '/docs',
        logger: Logger | None = None,
    ) -> None:
        """Creates an OpenAPI spec generator.

        Parameters
        ----------
        app : Starlette
            Application.
        servers : list[str]
            List of servers.
            Example: ``['http://localhost:8000']``
        title : str
            Title of the API.
        version : str
            Version of the API.
        description : str | None, optional
            Description of the API, by default None.
        url_prefix : str | None, optional
            URL prefix of the API docs, by default '/docs'
        """
        self._app = app
        self._servers = servers
        self._title = title
        self._version = version
        self._description = description
        self._url_prefix = url_prefix

        if logger is None:
            self._logger = getLogger(__name__)
        else:
            self._logger = logger

    def mount(self) -> None:
        """Adds the OpenAPI spec endpoint to the application."""
        try:
            self._logger.debug('Generating OpenAPI spec...')
            api_spec = self.generate()
            config = api_spec.model_dump(by_alias=True, exclude_none=True)
            api_doc(
                self._app,
                config=config,
                url_prefix=self._url_prefix,
                title=self._title,
            )
            self._logger.debug(
                'Added OpenAPI spec route "/docs" with methods {"GET"}'
            )
            self._logger.info('OpenAPI spec mounted on "/docs"')
        except Exception as e:
            self._logger.error(f'OpenAPI spec could not be mounted: {e}')

    def generate(self) -> OpenAPI:
        """Generates an OpenAPI spec.

        Returns
        -------
        OpenAPI
            OpenAPI spec.
        """
        return construct_open_api_with_schema_class(
            OpenAPI(
                info=self._get_info(),
                servers=self._get_servers(),
                paths=self._get_paths(),
            )
        )

    def generate_and_save(self, file_name: str) -> None:
        """Generates an OpenAPI spec and saves it to a file.

        Parameters
        ----------
        file_name : str
            Name of the destination file.
        """
        open_api = self.generate()
        with open(file_name, 'w') as f:
            content = open_api.model_dump_json(
                by_alias=True, exclude_none=True, indent=4
            )
            f.write(content)

    def _get_info(self) -> Info:
        """Get the metadata of the OpenAPI spec.

        Returns
        -------
        Info
            Metadata of the OpenAPI spec.
        """
        return Info(
            title=self._title,
            description=self._description,
            version=self._version,
        )

    def _get_servers(self) -> list[Server]:
        """Get the servers of the OpenAPI spec.

        Returns
        -------
        list[Server]
            List of servers.
        """
        return [Server(url=server) for server in self._servers]

    def _get_paths(self) -> Paths:
        """Gets the relative paths to the individual endpoints
        and their operations.

        Returns
        -------
        Paths
            Paths of the OpenAPI spec.
        """
        paths: Paths = {}
        sorted_routes = sorted(
            cast(list[Route], self._app.router.routes),
            key=lambda route: route.path,
        )
        for route in sorted_routes:
            if not isinstance(route, Route):
                continue
            if not route.methods:
                continue
            if not route.include_in_schema:
                continue
            self._logger.debug(f'Adding spec for route: {route}')

            if route.path not in paths:
                paths[route.path] = PathItem()

            docs_parser = EndpointDocstringParser(route.endpoint)
            parsed_docs = docs_parser.parse()
            endpoint_signature = signature(route.endpoint)
            auth_required = getattr(route.endpoint, '__auth_required__', False)
            use_odata = getattr(route.endpoint, '__use_odata__', False)

            for method in route.methods:
                if method in ('HEAD', 'OPTIONS'):
                    continue

                setattr(
                    paths[route.path],
                    method.lower(),
                    Operation(
                        tags=self._get_tags(route.path),
                        summary=parsed_docs.description.short_description,
                        description=parsed_docs.get_full_description(),
                        parameters=self._get_params_schema(
                            parsed_docs,
                            auth_required=auth_required,
                            use_odata=use_odata,
                        ),  # type: ignore
                        requestBody=self._get_request_body_schema(
                            endpoint_signature
                        ),
                        responses=self._get_responses_schema(
                            endpoint_signature,
                            parsed_docs,
                            auth_required=auth_required,
                        ),
                    ),
                )

        return paths

    def _get_tags(self, route_path: str) -> list[str]:
        """Get the tags of the OpenAPI spec.

        Parameters
        ----------
        route_path : str
            Path of the route.

        Returns
        -------
        list[str]
            List of tags.
        """
        if not route_path.startswith('/'):
            route_path = '/' + route_path
        return [route_path.split('/')[1].capitalize()]

    def _get_params_schema(
        self, parsed_docs: Docstring, auth_required: bool = False, use_odata: bool = False
    ) -> list[Parameter]:
        """Get the parameters of the endpoint.

        These are the path parameters, query parameters, and header parameters.

        Parameters
        ----------
        parsed_docs : Docstring
            Parsed docstring of the endpoint.
        auth_required : bool, optional
            Whether the endpoint requires authentication, by default False.
        use_odata : bool, optional
            Whether the endpoint uses OData V4 query, by default False.

        Returns
        -------
        list[Parameter]
            List of parameters of the endpoint.
        """
        auth_parameters = []
        if auth_required:
            auth_parameters.append(
                Parameter(
                    name='Authorization',
                    param_in='header',  # type: ignore
                    description='Bearer access token.',
                    required=True,
                    schema=Schema(type=DataType.STRING),
                    example='``Bearer <access_token>``',
                )
            )

        params = [
            Parameter(
                name=param.name,
                param_in='path',  # type: ignore
                description=param.short_description
                + '\n\n'
                + param.long_description,
                required=not param.optional,
                schema=Schema(type=self._get_param_type(param.type_hint)),
            )
            for param in parsed_docs.parameters
        ]

        query = self._get_query_params(parsed_docs.query, use_odata)

        return auth_parameters + params + query

    def _get_query_params(
        self, query_params: list[DocstringParsedParam], use_odata: bool = False
    ) -> list[Parameter]:
        """Gets a query parameter.

        Parameters
        ----------
        query_params : list[DocstringParsedParam]
            Query parameters.
        use_odata : bool, optional
            Whether the endpoint uses OData V4 query, by default False.

        Returns
        -------
        list[Parameter]
            Query parameters.
        """
        if use_odata:
            parameters = self._get_odata_query_params_spec()
        else:
            parameters = []

        for param in query_params:
            parameters.append(
                Parameter(
                    name=param.name,
                    param_in='query',  # type: ignore
                    description=param.short_description
                    + '\n\n'
                    + param.long_description,
                    required=not param.optional,
                    schema=Schema(type=self._get_param_type(param.type_hint)),
                )
            )

        return parameters

    def _get_odata_query_params_spec(self) -> list[Parameter]:
        """Gets the OData V4 query parameters spec.

        Returns the spec for the following query parameters:

        - ``$count``
        - ``$expand``
        - ``$filter_``
        - ``$format_``
        - ``$orderby``
        - ``$search``
        - ``$select``
        - ``$skip``
        - ``$top``
        - ``$page``

        Returns
        -------
        list[Parameter]
            OData query parameters.
        """
        ODATA_V4_QUERY_DOCS_URL = 'https://github.com/daireto/odata-v4-query'
        ODATA_V4_QUERY_DOCS_MESSAGE = (
            f'\n\nVisit [OData V4 Query docs]({ODATA_V4_QUERY_DOCS_URL}) '
            'for more info.'
        )
        return [
            Parameter(
                name='$count',
                param_in='query',  # type: ignore
                description=(
                    'Retrieves the total count of matching resources.'
                    f'{ODATA_V4_QUERY_DOCS_MESSAGE}'
                ),
                required=False,
                schema=Schema(type=DataType.BOOLEAN, default=False),
            ),
            Parameter(
                name='$expand',
                param_in='query',  # type: ignore
                description=(
                    'Retrieves related resources.'
                    f'{ODATA_V4_QUERY_DOCS_MESSAGE}'
                ),
                required=False,
                schema=Schema(type=DataType.STRING),
            ),
            Parameter(
                name='$filter',
                param_in='query',  # type: ignore
                description=(
                    'Filters results (rows, documents, etc.).'
                    f'{ODATA_V4_QUERY_DOCS_MESSAGE}'
                ),
                required=False,
                schema=Schema(type=DataType.STRING),
            ),
            Parameter(
                name='$format',
                param_in='query',  # type: ignore
                description=(
                    'Returns the results in the specified media format '
                    '(json, xml, csv, tsv).'
                    f'{ODATA_V4_QUERY_DOCS_MESSAGE}'
                ),
                required=False,
                schema=Schema(type=DataType.STRING, default='json'),
            ),
            Parameter(
                name='$orderby',
                param_in='query',  # type: ignore
                description=(
                    'Orders results.'
                    f'{ODATA_V4_QUERY_DOCS_MESSAGE}'
                ),
                required=False,
                schema=Schema(type=DataType.STRING),
            ),
            Parameter(
                name='$search',
                param_in='query',  # type: ignore
                description=(
                    'Returns results based on search criteria.'
                    f'{ODATA_V4_QUERY_DOCS_MESSAGE}'
                ),
                required=False,
                schema=Schema(type=DataType.STRING),
            ),
            Parameter(
                name='$select',
                param_in='query',  # type: ignore
                description=(
                    'Returns only the properties specified in the query.'
                    f'{ODATA_V4_QUERY_DOCS_MESSAGE}'
                ),
                required=False,
                schema=Schema(type=DataType.STRING),
            ),
            Parameter(
                name='$skip',
                param_in='query',  # type: ignore
                description=(
                    'Skips the specified number of results.'
                    f'{ODATA_V4_QUERY_DOCS_MESSAGE}'
                ),
                required=False,
                schema=Schema(type=DataType.INTEGER),
            ),
            Parameter(
                name='$top',
                param_in='query',  # type: ignore
                description=(
                    'Returns the specified number of results if available.'
                    f'{ODATA_V4_QUERY_DOCS_MESSAGE}'
                ),
                required=False,
                schema=Schema(type=DataType.INTEGER),
            ),
            Parameter(
                name='$page',
                param_in='query',  # type: ignore
                description=(
                    'Returns the results of the specified page number '
                    'if available. Computes the skip value from the top value.'
                    f'{ODATA_V4_QUERY_DOCS_MESSAGE}'
                ),
                required=False,
                schema=Schema(type=DataType.INTEGER),
            ),
        ]

    def _get_param_type(self, param_type: str) -> DataType:
        """Gets the ``DataType`` value based on the parameter type.

        Parameters
        ----------
        param_type : str
            Parameter type.
        """
        match param_type:
            case 'str':
                return DataType.STRING
            case 'int':
                return DataType.INTEGER
            case 'float':
                return DataType.NUMBER
            case 'bool':
                return DataType.BOOLEAN
            case _:
                return DataType.OBJECT

    def _get_request_body_schema(
        self, func_signature: Signature
    ) -> RequestBody | None:
        """Get the request body of the endpoint.

        Parameters
        ----------
        func_signature : Signature
            Signature of the endpoint.

        Returns
        -------
        RequestBody | None
            Request body of the endpoint.
        """

        def _get_request_body_annotation():
            for param in func_signature.parameters.values():
                if param.name == 'self':
                    continue

                if issubclass(param.annotation, BaseModel):
                    return param.annotation

        request_body_annotation = _get_request_body_annotation()
        if request_body_annotation:
            return RequestBody(
                content={
                    'application/json': MediaType(
                        schema=PydanticSchema(
                            schema_class=request_body_annotation
                        )
                    ),
                },
                required=True,
            )
        else:
            return None

    def _get_responses_schema(
        self,
        func_signature: Signature,
        parsed_docs: Docstring,
        auth_required: bool = False,
        has_request_body: bool = False,
    ) -> dict[str, Response | Reference]:
        """Get the responses of the endpoint.

        Parameters
        ----------
        func_signature : Signature
            Signature of the endpoint.
        parsed_docs : Docstring
            Parsed docstring of the endpoint.
        auth_required : bool, optional
            Whether the endpoint requires authentication, by default False.
        has_request_body : bool, optional
            Whether the endpoint has a request body, by default False.

        Returns
        -------
        dict[str, Response | Reference]
            Responses of the endpoint.
        """
        annotations_mapper: dict[str, type] = {}
        annotation = func_signature.return_annotation

        try:
            is_paginated = annotation.__name__.startswith('Pagination')
        except Exception:
            is_paginated = False

        if isclass(annotation):
            annotations_mapper[annotation.__name__] = annotation
        else:
            types = get_args(annotation)
            for _type in types:
                if isclass(_type):
                    annotations_mapper[_type.__name__] = _type
                    continue
                args = get_args(_type)
                if not args:
                    continue
                annotations_mapper[args[0].__name__] = args[0]

        responses_schema: Responses = {}
        for response in parsed_docs.responses:
            if response.type_hint.startswith('list['):
                response.type_hint = response.type_hint.replace('list[', '')
                response.type_hint = response.type_hint.replace(']', '')
                response_annotation = annotations_mapper.get(
                    response.type_hint, None
                )
                if response_annotation is None:
                    self._logger.warning(
                        f'{response.type_hint!r} of '
                        f'list[{response.type_hint!r}] is not a valid type'
                    )
                    continue

                if not issubclass(response_annotation, BaseModel):
                    self._logger.warning(
                        f'{response.type_hint!r} of '
                        f'list[{response.type_hint!r}] is not a subclass of '
                        'BaseModel'
                    )
                    continue

                items = PydanticSchema(schema_class=response_annotation)
                schema = Schema(type=DataType.ARRAY, items=items)

                if is_paginated:
                    schema = Schema(
                        type=DataType.OBJECT,
                        properties={
                            'page': Schema(
                                type=DataType.INTEGER,
                                description='Page number.',
                                example=1,
                            ),
                            'skip': Schema(
                                type=DataType.INTEGER,
                                description='Skip.',
                                example=0,
                            ),
                            'limit': Schema(
                                type=DataType.INTEGER,
                                description='Limit.',
                                example=100,
                            ),
                            'count': Schema(
                                type=DataType.INTEGER,
                                description='Total number of items.',
                                example=1,
                            ),
                            'pages': Schema(
                                type=DataType.INTEGER,
                                description='Total number of pages.',
                                example=1,
                            ),
                            'data': schema,
                        },
                    )

                schema = Schema(
                    type=DataType.OBJECT,
                    properties={'data': schema},
                )

            else:
                response_annotation = annotations_mapper.get(
                    response.type_hint, None
                )
                if response_annotation is None:
                    self._logger.warning(
                        f'{response.type_hint!r} is not a valid type'
                    )
                    continue

                if issubclass(response_annotation, BaseModel):
                    schema = Schema(
                        type=DataType.OBJECT,
                        properties={
                            'data': PydanticSchema(
                                schema_class=response_annotation
                            )
                        },
                    )
                else:
                    schema = Schema(type=DataType.OBJECT)

            if response.status_code not in responses_schema:
                responses_schema[response.status_code] = Response(
                    description=response.short_description
                    + '\n\n'
                    + response.long_description,
                    content={
                        'application/json': MediaType(schema=schema),
                    },
                )

        if auth_required:
            self._add_auth_error_responses_schema(responses_schema)

        if has_request_body:
            self._add_request_body_validation_error_response_schema(
                responses_schema
            )

        return responses_schema

    def _add_auth_error_responses_schema(
        self, responses_schema: dict[str, Response | Reference]
    ) -> None:
        """Adds the authentication error responses schema.

        Parameters
        ----------
        responses_schema : dict[str, Response  |  Reference]
            Responses schema.
        """
        responses_schema['401'] = Response(
            description='Unauthenticated response.',
            content={
                'application/json': MediaType(
                    schema=Schema(
                        type=DataType.OBJECT,
                        properties={
                            'message': Schema(
                                type=DataType.STRING,
                                description='Unauthenticated error message.',
                                example='User is not authenticated.',
                            ),
                        },
                    ),
                ),
            },
        )
        responses_schema['403'] = Response(
            description='Forbidden response.',
            content={
                'application/json': MediaType(
                    schema=Schema(
                        type=DataType.OBJECT,
                        properties={
                            'message': Schema(
                                type=DataType.STRING,
                                description='Unauthorized error message.',
                                example='User is not authorized.',
                            ),
                        },
                    ),
                ),
            },
        )

    def _add_request_body_validation_error_response_schema(
        self, responses_schema: dict[str, Response | Reference]
    ) -> None:
        """Adds the request body validation error response schema.

        Parameters
        ----------
        responses_schema : dict[str, Response  |  Reference]
            Responses schema.
        """
        responses_schema['400'] = Response(
            description='Bad request response.',
            content={
                'application/json': MediaType(
                    schema=Schema(
                        type=DataType.OBJECT,
                        properties={
                            'errors': Schema(
                                type=DataType.ARRAY,
                                items=Schema(
                                    type=DataType.OBJECT,
                                    properties={
                                        'type': Schema(
                                            type=DataType.STRING,
                                            description='Error type.',
                                        ),
                                        'loc': Schema(
                                            type=DataType.ARRAY,
                                            items=Schema(
                                                type=DataType.STRING,
                                                description='Error location.',
                                            ),
                                        ),
                                        'msg': Schema(
                                            type=DataType.STRING,
                                            description='Error message.',
                                        ),
                                        'input': Schema(
                                            type=DataType.OBJECT,
                                            description='Error input.',
                                        ),
                                        'ctx': Schema(
                                            type=DataType.OBJECT,
                                            description='Error context.',
                                        ),
                                    },
                                ),
                                description='Validation errors.',
                            ),
                        },
                        description='Bad request errors.',
                    ),
                ),
            },
        )

    def _to_title_case(self, name: str) -> str:
        """Takes names like ``foo_bar`` and returns ``Foo Bar``."""
        name = name.replace('_', ' ')
        return name[0].upper() + name[1:].lower()
