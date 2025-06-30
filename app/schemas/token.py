from pydantic import BaseModel

# Schema para a resposta do token no /login
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema para os dados contidos dentro do token JWT
class TokenData(BaseModel):
    phone: str | None = None