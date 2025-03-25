def get_bearer_header(access_token: str) -> dict[str, str]:
    return {'Authorization': f'Bearer {access_token}'}
