from typing import List, Optional
from pydantic import BaseModel, Field


class IngredientsItem(BaseModel):
    """
    Item for Ingredients
    """
    name: Optional[str] = Field(
        None,
        description="""Name of the Ingredient from the menu"""
    )
    quantity: int = Field(
        1,
        description="Quantity of the item. Default is 1."
    )


class ChildrenItem(BaseModel):
    """
    SubItem of OrderItem
    """
    name: Optional[str] = Field(
        None,
        description="""Name of the item from the menu. If name if not mentioned, make a placeholder
        with the name 'None'."""
    )
    type: str = Field(
        ...,
        description="Type of the item from the menu. E.g. 'fries', 'drinks', 'burgers'."
    )
    modifiers_to_add: List[IngredientsItem] = Field(
        default_factory=list,
        description="""Modifications of the item from the menu to add from possible_ingredients.
        For deals: []. E.g. 'Cheese Slice', 'Mayo', 'Ice', 'Ranch'."""
    )
    modifiers_to_remove: List[IngredientsItem] = Field(
        default_factory=list,
        description="""Modifications of the item from the menu to remove from default_ingredients.
        For deals and combos: []. E.g. 'Pickles' for 'burgers', 'Ice' for 'drinks'"""
    )


class OrderItem(BaseModel):
    """
    Item of the order
    """
    name: Optional[str] = Field(
        None,
        description="Name of the item from the menu. Put None if there is no name."
    )
    type: str = Field(
        ...,
        description="""Type of the item from the menu like: 'burgers', 'drinks', 'ice cream', 'desserts',
         'fries', 'combos', 'deals', 'sauces', 'ingredients'."""
    )
    size: Optional[str] = Field(
        None,
        description="""Only applicable to fries, drinks, combos. See the menu.
         Usually sizes are small, medium and large"""
    )
    quantity: int = Field(
        1,
        description="Quantity of the item. Default is 1."
    )
    modifiers_to_add: List[IngredientsItem] = Field(
        default_factory=list,
        description="""Add sauses for combo here. Modifications of the item from the menu to add from possible_ingredients.
        If not applicable: []. Example: 'Cheese Slice', 'Mayo' for 'fries', 'Ice' for drinks"""
    )
    modifiers_to_remove: List[IngredientsItem] = Field(
        default_factory=list,
        description="""Modifications of the item from the menu to remove from default_ingredients.
        If not applicable: []. Example: 'Onion', 'Pickles' for 'burgers', 'Ice' for drinks or 'Flag: Sauce was offered' for combo"""
    )
    children: Optional[List["ChildrenItem"]] = Field(
        None,
        description="""Optional nested items for combos or double deals. 
        For example, a combo contains burger, drink, and fries. A deal contains two burgers."""
    )


class OrderState(BaseModel):
    """
    General state of the order for LLM to return
    """
    items: List[OrderItem] = Field(
        default_factory=list,
        description="A list of all items currently included in the customer's order."
    )
    order_finished: bool = Field(
        False,
        description="""Set to True if the customer has indicated that
        they don't want to add anything else to the order."""
    )


class Order():
    """
    The class to represent Order details like items ordered and various flags for business rules
    with functions to summarise order
    """

    def __init__(self, menu) -> None:
        self.list = []
        self.finished = False
        self.upsell_offered = False
        self.dessert_offered = False
        self.double_deal_suggested = False
        self.menu = menu

    def summary(self) -> str:
        """summarizes order in an ordered format

        Returns:
            str: order in an ordered format
        """
        res = "=== Your order ===\n"
        for item in self.list:
            res += f"  - {item.quantity} x {item.name} {item.size} [{item.type}]\n"
            if item.modifiers_to_add:
                res += f"      Modifiers: {item.modifiers_to_add}\n"
            if item.modifiers_to_remove:
                res += f"      Modifiers: {item.modifiers_to_remove}\n"
            if item.children:
                res += "      With:\n"
                for child in item.children:
                    res += f"        * [{child.type}]: {child.name} {child.modifiers_to_add}, {child.modifiers_to_remove}\n"
        res += "==================\n"
        return res

    def calculate_total(self) -> float:
        """calculates total price of the order

        Returns:
            float: total price of the order in $
        """
        total = 0.0
        for item in self.list:
            if item.type == 'combos':
                total += item.quantity * \
                    self.menu.menu["combos"][item.name]["size_price"][item.size]
                for mod in item.modifiers_to_add:
                    if mod.name != "Flag: Sauce was offered":
                        total += self.menu.menu["sauces"][mod.name]
                for child in item.children:
                    for mod in child.modifiers_to_add:
                        total += self.calculate_modifications(child)
            if item.type == 'drinks':
                total += item.quantity * \
                    self.menu.menu["drinks"][item.name]["size_price"][item.size]
            if item.type == 'burgers':
                total += item.quantity * \
                    self.menu.menu["burgers"][item.name]["price"]
                total += self.calculate_modifications(item)
            if item.type == 'fries':
                total += item.quantity * \
                    self.menu.menu["fries"][item.name]["size_price"][item.size]
                total += self.calculate_modifications(item)
            if item.type in ['desserts', 'ice cream']:
                total += item.quantity * \
                    self.menu.menu["desserts"][item.name]["price"]
            if item.type == 'deals':
                deal_sum = 0
                for child in item.children:
                    deal_sum += self.menu.menu["burgers"][child.name]["price"]
                    total += self.calculate_modifications(child)
                total += deal_sum * 0.8
            if item.type == 'sauces':
                total += item.quantity * \
                    self.menu.menu["sauces"][item.name]
        return total

    def calculate_modifications(self, item) -> float:
        """calculate total of modifications added to the order

        Args:
            item (_type_): _description_

        Returns:
            float: _description_
        """
        total = 0
        available_mods = self.menu.menu["ingredients"].keys()
        for modidfier in item.modifiers_to_add:
            if modidfier.name in available_mods:
                total += modidfier.quantity * \
                    self.menu.menu["ingredients"][modidfier.name]
        return total


