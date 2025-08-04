"""
This module is responsible for all actions related to manager.
"""
from queue import Queue
from mcdonalds_proj.order import Order, OrderItem, ChildrenItem, IngredientsItem
from mcdonalds_proj.menu import Menu

# todo business logic


class ManagerMessage():
    def __init__(self, text: str, flag: str) -> None:
        """
        Args:
            text (str): text of the manager's message. It can be question
            flag (str): flag tells the llm how exactly to process user message
        """
        self.text = text
        self.flag = flag


class Manager:
    def __init__(self):
        self.message_queue = Queue()
        self.issue_queue = Queue()
        self.errors = []
        self.combos_sauce_offered = []

    def start_taking_order(self) -> str:
        msg = ManagerMessage(
            "System: Welcome to McDonald's! What can I get you started with?", "general")
        self.message_queue.put(msg)

    def finish_taking_order(self, order: Order) -> str:
        if not order.list:
            msg = "No items in order."
        else:
            text = "System:\n"
            text += f"{order.summary()}\n"
            text += f"Your order total is ${order.calculate_total()}"
            msg = ManagerMessage(text, "finished")
        self.message_queue.put(msg)

    def last_call(self) -> str:
        msg = ManagerMessage(
            "System: Would you like anything else?", "general")
        self.message_queue.put(msg)

    def offer_dessert(self):
        msg = ManagerMessage(
            "System: Would you like something for dessert?", "dessert_offered")
        self.message_queue.put(msg)

    def offer_sause(self, item: OrderItem):
        msg = ManagerMessage(
            f"System: Would you like a sause for your {item.name}?", "general")
        self.message_queue.put(msg)

    def offer_to_turn_into_combo(self, item: OrderItem):
        msg = ManagerMessage(
            f"System: Would you like to turn your {item.name} into a combo {item.name} Meal?", "general")
        self.message_queue.put(msg)

    def update_order(self, order, llm_response):
        order.issue_queue = Queue()
        order.list = llm_response.items
        order.finished = llm_response.order_finished
        order.summary()

    def apply_business_rules(self, order: Order, menu: Menu):
        small_burger_count = 0
        big_burger_count = 0
        burger_count = 0
        combo_count = 0
        small_deal_items = []
        big_deal_items = []

        # If the user has ordered a combo, offer to add a dipping sauce for extra charge, for every combo.
        if order.list == []:
            self.errors.append("The order cannot be empty.")
            self.last_call()

        for item in order.list:
            if item.type == 'combos':
                combo_count += 1
                # Flag meaning that no sauce was offered
                if len(item.modifiers_to_add) < 1:
                    self.offer_sause(item)
                    item.modifiers_to_add.append('Flag')
                    return

            if item.type == 'burgers':
                burger_count += 1
                # If the user has ordered a burger, offer to turn it into a combo, for every burger ordered.
                if item.name not in ["Big Tasty", 'Hamburger', 'Royal Cheeseburger']:
                    if "Flag" not in [mod.name for mod in item.modifiers_to_add]:     
                        self.offer_to_turn_into_combo(item)
                        item.modifiers_to_add.append(IngredientsItem(name='Flag'))
                        return
                if item.name in menu.menu['deals']['Small Double Deal']:
                    small_burger_count += item.quantity
                    small_deal_items.append(item)
                if item.name in menu.menu['deals']['Big Double Deal']:
                    big_burger_count += item.quantity
                    big_deal_items.append(item)

            if item.type == 'desserts':
                order.dessert_offered = True

       # Turn two small burgers into Small Double Deal
        while small_burger_count >= 2:
            item1 = small_deal_items[0]

            if item1.quantity >= 2:
                # Use two of the same item
                while item1.quantity >= 2:
                    child1 = ChildrenItem(
                        name=item1.name,
                        type=item1.type,
                        modifiers_to_add=item1.modifiers_to_add[:],
                        modifiers_to_remove=item1.modifiers_to_remove[:]
                    )
                    child2 = ChildrenItem(
                        name=item1.name,
                        type=item1.type,
                        modifiers_to_add=item1.modifiers_to_add[:],
                        modifiers_to_remove=item1.modifiers_to_remove[:]
                    )
                    small_deal = OrderItem(
                        name='Small Double Deal',
                        type='deals',
                        quantity=1,
                        children=[child1, child2]
                    )
                    order.list.append(small_deal)
                    item1.quantity -= 2
                    small_burger_count -= 2
                if item1.quantity == 0:
                    order.list.remove(item1)
            elif len(small_deal_items) >= 2:
                # Use two different items
                item2 = small_deal_items[1]
                child1 = ChildrenItem(
                    name=item1.name,
                    type=item1.type,
                    modifiers_to_add=item1.modifiers_to_add[:],
                    modifiers_to_remove=item1.modifiers_to_remove[:]
                )
                child2 = ChildrenItem(
                    name=item2.name,
                    type=item2.type,
                    modifiers_to_add=item2.modifiers_to_add[:],
                    modifiers_to_remove=item2.modifiers_to_remove[:]
                )
                small_deal = OrderItem(
                    name='Small Double Deal',
                    type='deals',
                    quantity=1,
                    children=[child1, child2]
                )
                item2.quantity -= 1
                if item2.quantity == 0:
                    order.list.remove(item2)
                    small_deal_items.remove(item2)
                order.list.append(small_deal)
                order.list.remove(item1)
                small_deal_items.remove(item1)
                small_deal_items.remove(item2)
                small_burger_count -= 2
            else:
                break


        # turn two big burgers into Big Double Deal
        while big_burger_count >= 2:
            item1 = big_deal_items[0]

            if item1.quantity >= 2:
                # Use two of the same item
                while item1.quantity >= 2:
                    child1 = ChildrenItem(
                        name=item1.name,
                        type=item1.type,
                        modifiers_to_add=item1.modifiers_to_add[:],
                        modifiers_to_remove=item1.modifiers_to_remove[:]
                    )
                    child2 = ChildrenItem(
                        name=item1.name,
                        type=item1.type,
                        modifiers_to_add=item1.modifiers_to_add[:],
                        modifiers_to_remove=item1.modifiers_to_remove[:]
                    )
                    big_deal = OrderItem(
                        name='Big Double Deal',
                        type='deals',
                        quantity=1,
                        children=[child1, child2]
                    )
                    order.list.append(big_deal)
                    item1.quantity -= 2
                    big_burger_count -= 2
                if item1.quantity == 0:
                    order.list.remove(item1)
            elif len(big_deal_items) >= 2:
                # Use two different items
                item2 = big_deal_items[1]
                child1 = ChildrenItem(
                    name=item1.name,
                    type=item1.type,
                    modifiers_to_add=item1.modifiers_to_add[:],
                    modifiers_to_remove=item1.modifiers_to_remove[:]
                )
                child2 = ChildrenItem(
                    name=item2.name,
                    type=item2.type,
                    modifiers_to_add=item2.modifiers_to_add[:],
                    modifiers_to_remove=item2.modifiers_to_remove[:]
                )
                big_deal = OrderItem(
                    name='Big Double Deal',
                    type='deals',
                    quantity=1,
                    children=[child1, child2]
                )
                item2.quantity -= 1
                if item2.quantity == 0:
                    order.list.remove(item2)
                    big_deal_items.remove(item2)
                order.list.append(big_deal)
                order.list.remove(item1)
                big_deal_items.remove(item1)
                big_deal_items.remove(item2)
                big_burger_count -= 2
            else:
                break

        # If the user has order any burger or a combo, offer to add a dessert, but only once per order.
        if (burger_count > 0 or combo_count > 0) and order.dessert_offered is False:
            self.offer_dessert()
            order.dessert_offered = True

    def get_errors(self) -> str:
        txt = ''
        for i in self.errors:
            txt += i
            txt += '\n'

        self.errors = []
        return txt[:-1]

    def validate(self, order: Order, menu: Menu):
        if not order.list:
            self.errors.append(
                "System: No items were ordered. Try again.")
        else:
            for item in order.list:
                # Item type validation failed, no such type
                if item.type not in ['burgers', 'drinks', 'fries', 'desserts', 'ice cream', 'sauces', 'combos', 'deals', 'ingredients']:
                    err = f"Error: [{item.type}] is not in the menu."
                    self.errors.append(err)
                    order.list.remove(item)
                if item.type in ['burgers', 'drinks', 'fries', 'desserts', 'ice cream', 'sauces']:
                    if self.validate_item(item, menu):
                        break
                if item.type == 'combos':
                    if self.validate_combo(item, menu):
                        break
                if item.type == 'deals':
                    if self.validate_deal(item, menu):
                        break
                if item.type == 'ingredients':
                    self.errors.append(
                        f"Ingredients cannot be ordered standalone. Item {item.name} was removed")
                    order.list.remove(item)
                    break

    def validate_item(self, item: OrderItem, menu: Menu) -> bool:
        if item.name is None or item.name == 'None':
            self.handle_missing_name(item)
            return True
        if self.validate_name_in_menu(item, menu):
            return True
        self.validate_quantity(item)
        if self.validate_size(item, menu):
            return True
        self.validate_modifiers(item, menu)
        return False

    def validate_name_in_menu(self, item: OrderItem, menu: Menu) -> bool:
        if item.type == 'ice cream':
            names_in_menu = menu.menu['virtual'][item.type]
        else:
            names_in_menu = list(menu.menu[item.type])
        if item.name not in names_in_menu:
            msg = ManagerMessage(
                f"System: There is no {item.name} in the {item.type} menu. \
                Available options are: {names_in_menu}. Which one would you like?", "clarify")
            self.issue_queue.put(msg)
            return True
        return False

    def validate_combo(self, item: OrderItem, menu: Menu) -> bool:
        if self.validate_item(item, menu):
            return True
        if not item.children:
            item.children = [
                ChildrenItem(type='burgers', name=item.name[:-5]),
                ChildrenItem(type='drinks'),
                ChildrenItem(type='fries', name='French Fries')]
        for child in item.children:
            if child.type == 'burgers':
                availablle_item = item.name[:-5]
                if child.name != availablle_item:
                    err = f"{child.name} has to be {availablle_item} in the {item.name}.\
                     Was: {child.name}, Now: {availablle_item}"
                    self.errors.append(err)
                    child.name = availablle_item
                if self.validate_item(child, menu):
                    return True
            if child.type == 'drinks':
                availablle_items = list(
                    menu.menu["combos"][item.name]["drinks"])
                if child.name not in availablle_items:
                    if child.name is None or child.name == 'None':
                        self.handle_missing_name(child, item)
                        return True
                    msg = ManagerMessage(
                        f"System: {child.name} is not allowed in {item.name}.\
                         Drink has to be in the list {availablle_items}.\
                         Which one would you like?", "clarify")
                    self.issue_queue.put(msg)
                    return True
                if self.validate_item(child, menu):
                    return True
            if child.type == 'fries':
                availablle_items = list(
                    menu.menu["combos"][item.name]["fries"])
                if child.name not in availablle_items:
                    if child.name is None or child.name == 'None':
                        self.handle_missing_name(child, item)
                        return True
                    msg = ManagerMessage(
                        f"System: {child.name} is not allowed in {item.name}.\
                         Fries item has to be in the list {availablle_items}?", "clarify")
                    self.issue_queue.put(msg)
                    return True
                if self.validate_item(child, menu):
                    return True
        return False

    def validate_deal(self, item: OrderItem, menu: Menu):
        if self.validate_item(item, menu):
            return True
        # Validate Children Items
        if not item.children:
            item.children = [
                ChildrenItem(type='burgers'),
                ChildrenItem(type='burgers')]
        if len(item.children) != 2:
            item.children = item.children[:2]
            item.children.append(ChildrenItem(type='burgers'))

        for child in item.children:
            if child.type == 'burgers':
                availablle_items = list(
                    menu.menu["deals"][item.name])
                if child.name not in availablle_items:
                    if child.name is None or child.name == 'None':
                        self.handle_missing_name(child, item)
                        return True
                    msg = ManagerMessage(
                        f"System: {child.name} is not allowed in {item.name}.\
                         Both burgers have to be in the list {availablle_items}?", "clarify")
                    self.issue_queue.put(msg)
                    return True
                if self.validate_item(child, menu):
                    return True
            # No drinks or Fries in the deal
            if child.type == 'drinks':
                if child.name | child.size | child.modifiers:
                    err = f"Deals cannot contain drinks. {child.name} was removed."
                    self.errors.append(err)
                    child.name = None
                    child.modifiers = None
            if child.type == 'fries':
                if child.name | child.size | child.modifiers:
                    err = f"Deals cannot contain fries. {child.name} was removed."
                    self.errors.append(err)
                    child.name = None
                    child.modifiers = None
        return False

    def validate_quantity(self, item):
        if isinstance(item, OrderItem):
            if item.quantity < 1:
                self.errors.append(
                    f"{item.name}'s quantity must be > 0. \
                    Was: {item.quantity} , Now: {max(1, abs(item.quantity))}")
                item.quantity = max(1, abs(item.quantity))
        elif isinstance(item, IngredientsItem):
            if item.quantity < 1:
                self.errors.append(
                    f"Ingredient {item.name}'s quantity must be > 0.\
                     Was: {item.quantity} , Now: {max(1, abs(item.quantity))}")
                item.quantity = max(1, abs(item.quantity))
        return

    def validate_size(self, item, menu: Menu) -> bool:
        if isinstance(item, ChildrenItem):
            return False
        if item.type in ['burgers', 'desserts', 'ice cream', 'deals', 'ingredients', 'sauces']:
            if item.size:
                self.errors.append(
                    f"{item.type} does not support sizes. {item.size} was removed.")
                item.size = None
        else:
            if item.size is None:
                self.handle_missing_size(item.name)
                return True
            if item.type in ['fries', 'drinks', "combos"]:
                available_sizes = list(
                    menu.menu[item.type][item.name]['size_price'].keys())
                if item.size not in available_sizes:
                    self.issue_queue.put(
                        f"Wrong size of {item.name}. Available sizes: {available_sizes}.\
                         Which one would you like?")
        return False

    def validate_modifiers(self, item, menu: Menu):
        if item.type in ['desserts', 'ice cream', 'deals', 'ingredients', 'virtual', 'sauces']:
            if len(item.modifiers_to_add) > 0:
                for mod in item.modifiers_to_add:
                    self.errors.append(
                        f"You cannot add {mod.name} to {item.name}. {mod.name} was removed.")
            if len(item.modifiers_to_remove) > 0:
                for mod in item.modifiers_to_remove:
                    self.errors.append(
                        f"You cannot remove {mod.name} from {item.name}.")
            item.modifiers_to_add = []
            item.modifiers_to_remove = []
        elif item.type == 'combos':
            for mod in item.modifiers_to_add:
                possible_ingredients = list(menu.menu['sauces'])
                if mod.name not in possible_ingredients and mod.name != "Flag":
                    self.errors.append(
                        f"You cannot add {mod.name} for {item.name}. '{mod.name}' was removed.")
                    item.modifiers_to_add.remove(mod)
                mod.quantity = 1

        else:
            possible_ingredients = menu.menu[item.type][item.name]['possible_ingredients']
            default_ingredients = menu.menu[item.type][item.name]['default_ingredients']

            for mod in item.modifiers_to_add:
                if mod.name not in possible_ingredients and mod.name != 'Flag':
                    self.errors.append(
                        f"You cannot add {mod.name} for {item.name}. '{mod}' was removed.")
                    item.modifiers_to_add.remove(mod)

            for mod in item.modifiers_to_remove:
                if mod.name not in default_ingredients:
                    self.errors.append(
                        f"You cannot remove {mod.name} for {item.name}")
                    item.modifiers_to_remove.remove(mod)

    def handle_missing_name(self, item, parent=None) -> None:
        if item.type in ['fries', 'ice cream']:
            name = item.type
        else:
            name = item.type[:-1]
        if parent:
            if parent.type == 'deals':
                msg = ManagerMessage(
                    f"System: What two {name}s for your {parent.name}?", "clarify")
            if parent.type == 'combos':
                msg = ManagerMessage(
                    f"System: What kind of {name} for your {parent.name}?", "clarify")
        else:
            msg = ManagerMessage(
                f"System: What kind of {name}?", "clarify")
        self.issue_queue.put(msg)

    def handle_missing_size(self, name) -> None:
        msg = ManagerMessage(
            f"System: What size of {name}?", "clarify")
        self.issue_queue.put(msg)
