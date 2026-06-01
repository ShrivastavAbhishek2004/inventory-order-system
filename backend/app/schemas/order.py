from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
    ConfigDict
)


class OrderCreate(BaseModel):

    customer_id: int

    product_id: int

    quantity: int = Field(
        ...,
        gt=0
    )


class OrderResponse(BaseModel):

    id: int

    customer_id: int

    product_id: int

    quantity: int

    total_amount: Decimal

    model_config = ConfigDict(
        from_attributes=True
    )