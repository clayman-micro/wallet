from aiohttp_openapi import Parameter, ParameterIn


AccessToken = Parameter(
    in_=ParameterIn.header,
    name="X-Access-Token",
    schema={"type": "string"},
    required=True,
)
