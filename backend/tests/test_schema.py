from app.schemas.product import ProductCreate


def test_valid_product():

    product = ProductCreate(
        name="Laptop",
        sku="LAP001",
        price=50000,
        quantity_in_stock=10
    )

    assert product.name == "Laptop"