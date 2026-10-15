import pytest

from shopcart import Cart


def test_empty_cart_total_is_zero():
    assert Cart().total() == 0


def test_add_single_item():
    cart = Cart()
    cart.add_item("MUG")
    assert cart.items == {"MUG": 1}
    assert cart.subtotal() == 1200


def test_add_same_item_twice_increments_quantity():
    cart = Cart()
    cart.add_item("MUG")
    cart.add_item("MUG", 2)
    assert cart.items == {"MUG": 3}


def test_remove_item_decrements_then_deletes():
    cart = Cart()
    cart.add_item("CAP", 2)
    cart.remove_item("CAP")
    assert cart.items == {"CAP": 1}
    cart.remove_item("CAP")
    assert cart.items == {}


def test_unknown_sku_raises():
    with pytest.raises(ValueError):
        Cart().add_item("NOPE")


def test_invalid_code_raises():
    with pytest.raises(ValueError):
        Cart().apply_code("FREESTUFF")


def test_total_includes_tax():
    cart = Cart()
    cart.add_item("TEE")
    assert cart.total() == 2759  # 2000 + 8% tax + 599 cents shipping (subtotal < $50.00)


def test_percent_discount():
    cart = Cart()
    cart.add_item("MUG", 2)
    cart.apply_code("SAVE10")
    assert cart.total() == 2932  # ((2400 - 10%) + 8% tax) + 599 cents shipping (subtotal < $50.00)


def test_fixed_discount_applied_before_tax():
    cart = Cart()
    cart.add_item("TEE")
    cart.add_item("TEE")
    cart.apply_code("TENOFF")
    assert cart.total() == 3839  # ((4000 - 1000) + 8% tax) + 599 cents shipping (subtotal < $50.00)


def test_free_shipping_threshold():
    cart = Cart()
    # 3 TEEs = $60.00 (6000 cents), >= $50.00 threshold -> free shipping
    cart.add_item("TEE", 3)
    assert cart.subtotal() == 6000
    # 6000 + 8% tax = 6480, zero shipping
    assert cart.total() == 6480


def test_shipping_fee_below_threshold():
    cart = Cart()
    # 2 TEEs = $40.00 (4000 cents), < $50.00 threshold -> $5.99 shipping
    cart.add_item("TEE", 2)
    assert cart.subtotal() == 4000
    # (4000 + 8% tax) + 599 shipping = 4320 + 599 = 4919
    assert cart.total() == 4919


def test_empty_cart_shipping():
    cart = Cart()
    assert cart.subtotal() == 0
    assert cart.total() == 0


def test_discount_drops_subtotal_below_threshold_incurs_shipping():
    cart = Cart()
    # 5 TEEs = $100.00 (10000 cents)
    cart.add_item("TEE", 5)
    # Apply SAVE25 (25% off) -> 7500 cents (still >= $50.00, free shipping)
    cart.apply_code("SAVE25")
    assert cart.total() == 8100  # 7500 + 8% tax + 0 shipping

    cart2 = Cart()
    # 3 TEEs = $60.00 (6000 cents)
    cart2.add_item("TEE", 3)
    # Apply SAVE25 (25% off) -> 4500 cents (< $50.00, incurs shipping)
    cart2.apply_code("SAVE25")
    assert cart2.total() == 5459  # (4500 + 8% tax) + 599 shipping

