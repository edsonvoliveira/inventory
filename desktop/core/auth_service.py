class AuthService:
    def authenticate(self, email: str, password: str) -> bool:
        return email == "admin" and password == "123"
