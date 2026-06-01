from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator
)


class ProductBase(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=255
    )

    sku: str = Field(
        ...,
        min_length=3,
        max_length=100
    )

    price: Decimal = Field(
        ...,
        gt=0
    )

    quantity_in_stock: int = Field(
        ...,
        ge=0
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError(
                "Product name cannot be empty"
            )

        return value


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):

    name: str | None = None
    sku: str | None = None
    price: Decimal | None = None
    quantity_in_stock: int | None = None


class ProductResponse(ProductBase):

    id: int

    model_config = ConfigDict(
        from_attributes=True
    )