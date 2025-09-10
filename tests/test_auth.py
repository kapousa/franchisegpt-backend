from src.services.auth_service import AuthService

def test_token_roundtrip():
    token = AuthService.create_token("user123")
    decoded = AuthService.decode_token(token)
    assert decoded["sub"] == "user123"
