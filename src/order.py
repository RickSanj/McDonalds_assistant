from typing import List, Optional
from pydantic import BaseModel, Field


class ChildrenItem(BaseModel):
    name: str = Field(
        None,
        description="Name of the item from the menu. In 'fries' or 'drinks' category."
    )
    type: str = Field(
        ...,
        description="Type of the item from the menu. Could be 'fries' or 'drinks' or 'burgers'."
    )
    size: Optional[str] = Field(
        None,
        description="Size of the item from the menu. Possible values: 'small', 'medium', 'large'."
    )
    modifiers: List[str] = Field(
        default_factory=list,
        description="Modifications of the item from the menu. If not applicable: []. Example: 'Ketchup', 'Mayo' for 'fries', 'Ice' for drinks"
    )


class OrderItem(BaseModel):
    name: str = Field(  # Example: Big Mac, Coke, French Fries.")
        None,
        description="Name of the item from the menu."
    )
    type: str = Field(  # Possible values: 'burger', 'drink', 'dessert', 'fries', 'combo', 'double_deal'.")
        ...,
        description="Type of the item from the menu."
    )
    size: Optional[str] = Field(  # Possible values: 'small', 'medium', 'large'.")
        None,
        description="Size of the item if applicable. See the menu. Usually sizes are small, medium and large"
    )
    quantity: int = Field(
        1,
        description="Quantity of the item. Default is 1."
    )
    modifiers: List[str] = Field(  # Example: 'no onions', 'double cheese', 'extra ketchup'."
        default_factory=list,
        description="Modifications of the item from the menu. If not applicable: []."
    )
    children: Optional[List["ChildrenItem"]] = Field(
        None,
        description="Optional nested items for combos or double deals. For example, a combo contains burger, drink, and fries. A deal contains two burgers."
    )


class OrderState(BaseModel):
    items: List[OrderItem] = Field(
        default_factory=list,
        description="A list of all items currently included in the customer's order."
    )
    order_finished: bool = Field(
        False,
        description="Set to True if the customer has indicated they don't want to add anything else to the order."
    )


class Order():
    """
    The class to represent Order details like items ordered and various flags for business rules
    with functions to summarise order and calculate total
    """

    def __init__(self) -> None:
        self.list = None
        self.finished = False
        self.upsell_offered = False
        self.dessert_offered = False
        self.double_deal_suggested = False

    def summary(self) -> str:
        """summarizes order in an ordered format

        Returns:
            str: order in an ordered format
        """
        res = "=== Your order ===\n"
        for item in self.list:
            res += f"  - {item.quantity} x {item.name} [{item.type}]\n"
            if item.modifiers:
                res += f"      Modifiers: {', '.join(item.modifiers)}\n"
            if item.children:
                res += "      With:\n"
                for child in item.children:
                    res += f"        * [{child.type}]: {child.name} {child.size} {child.modifiers}\n"
        res +="==================\n"
        return res

    def calculate_total(self) -> float:
        """calculates total price of the order

        Returns:
            float: total price of the order in $
        """
        total = 0.0
        # for i in self.list:
        #     i
        return total
