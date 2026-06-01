from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict
)


class CustomerBase(BaseModel):

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=255
    )

    email: EmailStr

    phone_number: str = Field(
        ...,
        min_length=5,
        max_length=50
    )


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):

    full_name: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None


class CustomerResponse(CustomerBase):

    id: int

    model_config = ConfigDict(
        from_attributes=True
    )