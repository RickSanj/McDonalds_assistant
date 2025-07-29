import json
from mcdonalds_proj.order import Order, OrderItem, ChildrenItem
from queue import Queue
from mcdonalds_proj.menu import Menu




class ManagerMessage():
    def __init__(self, text: str, flag: str) -> None:
        """_summary_

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

    def update_order(self, order, llm_response):
        order.issue_queue = Queue()
        order.list = llm_response.items
        order.finished = llm_response.order_finished
        order.summary()

    def apply_business_rules(self, order: Order):
        # turn into deals
        if order.list == []:
            self.errors.append("The order cannot be empty.")
            self.last_call()
        if order.dessert_offered is False:
            self.offer_dessert()
            order.dessert_offered = True

    def get_errors(self) -> str:
        txt = ''
        for i in self.errors:
            txt += i
            txt += '\n'

        self.errors = []
        return txt[:-1]


    def validate(self, order: Order, menu: Menu) -> str:
        if not order.list:
            self.errors.append(
                "System: No items were ordered. Try again.")
        else:
            for item in order.list:
                if item.type == 'combos':
                    if self.validate_combo(item, menu):
                        break
                elif item.type == 'burgers':
                    if self.validate_burger(item, menu):
                        break
                elif item.type == 'drinks':
                    if self.validate_drink(item, menu):
                        break
                elif item.type == 'fries':
                    if self.validate_fries(item, menu):
                        break
                elif item.type == 'desserts':
                    order.dessert_offered = True
                    if self.validate_dessert(item, menu):
                        break
                elif item.type == 'deals':
                    if self.validate_deal(item, menu):
                        break
                elif item.type == 'ingredients':
                    self.errors.append(
                        "Ingredients cannot be ordered standalone.")
                    order.list.remove(item)
                    break
        # return self.get_errors()

    def validate_burger(self, item: OrderItem, menu: Menu) -> bool:
        if item.name is None or item.name == 'None':
            self.handle_missing_name("burger")
            return True
        self.validate_quantity(item)
        if self.validate_size(item, menu):
            return True
        self.validate_modifiers(item, menu)
        return False

    def validate_drink(self, item: OrderItem, menu: Menu) -> bool:
        if item.name is None or item.name == 'None':
            self.handle_missing_name("drink")
            return True
        self.validate_quantity(item)
        if self.validate_size(item, menu):
            return True
        self.validate_modifiers(item, menu)
        return False

    def validate_fries(self, item: OrderItem, menu: Menu):
        if item.name is None or item.name == 'None':
            self.handle_missing_name("fries")
            return True
        self.validate_quantity(item)
        if self.validate_size(item, menu):
            return True
        self.validate_modifiers(item, menu)
        return False

    def validate_dessert(self, item: OrderItem, menu: Menu):
        if item.name is None:
            self.handle_missing_name("dessert")
            return True
        self.validate_quantity(item)
        if self.validate_size(item, menu):
            return True
        self.validate_modifiers(item, menu)
        return False

    def validate_name_in_menu(self, item: OrderItem, menu: Menu) -> bool:
        names_in_menu = list(menu.menu["virtual"][item.name].keys())
        if item.name not in names_in_menu:
            msg = ManagerMessage(
                f"System: There is no such {item.name} in the {item.type} menu?", "clarify")
            self.issue_queue.put(msg)
            return True
        return

    def validate_combo(self, item: OrderItem, menu: Menu) -> bool:
        if item.name is None:
            self.handle_missing_name("combo")
            return True
        if item.name not in list(menu.menu["virtual"][item.type]):
            return True
        self.validate_size(item, menu)
        self.validate_quantity(item)
        if not item.children:
            item.children = [
                ChildrenItem(type='burgers'),
                ChildrenItem(type='drinks'),
                ChildrenItem(type='fries')]
        for child in item.children:
            if child.type == 'burgers':
                availablle_item = item.name[:-5]
                if child.name != availablle_item:
                    err =  f"{child.name} has to be {availablle_item} in the {item.name}. Was: {child.name}, Now: {availablle_item}"
                    self.errors.append(err)
                    child.name = availablle_item
                if self.validate_burger(child, menu):
                    return True
            if child.type == 'drinks':
                availablle_items = list(
                    menu.menu["combos"][item.name]["drinks"])
                if child.name not in availablle_items:
                    if child.name is None or child.name == 'None':
                        self.handle_missing_name("drink", item.name)
                        return True
                    msg = ManagerMessage(
                        f"System: {child.name} is not allowed in {item.name}. Drink has to be in the list {availablle_items}. Which one would you like?", "clarify")
                    self.issue_queue.put(msg)
                    return True
                if self.validate_drink(child, menu):
                    return True
            if child.type == 'fries':
                availablle_items = list(
                    menu.menu["combos"][item.name]["fries"])
                if child.name not in availablle_items:
                    if child.name is None or child.name == 'None':
                        self.handle_missing_name("fries", item.name)
                        return True
                    msg = ManagerMessage(
                        f"System: {child.name} is not allowed in {item.name}. Fries item has to be in the list {availablle_items}?", "clarify")
                    self.issue_queue.put(msg)
                    return True
                if self.validate_fries(child, menu):
                    return True
        return False

    def validate_deal(self, item: OrderItem, menu: Menu):
        if item.name is None or item.name == "None":
            self.handle_missing_name("deal")
            return True
        self.validate_size(item, menu)
        self.validate_quantity(item)
        # Validate Children Items
        if not item.children:
            item.children = [
                ChildrenItem(type='burgers'),
                ChildrenItem(type='burgers')]
        for child in item.children:
            if child.type == 'burgers':
                availablle_items = list(menu.menu["deals"][item.name]["possible_items"])
                if child.name not in availablle_items:
                    if child.name is None or child.name == 'None':
                        self.handle_missing_name("burger", item.name)
                        return True
                    msg = ManagerMessage(
                        f"System: {child.name} is not allowed in {item.name}. Both burgers have to be in the list {availablle_items}?", "clarify")
                    self.issue_queue.put(msg)
                    return True
                if self.validate_burger(child, menu):
                    return True
            # No drinks or Fries in the deal
            if child.type == 'drinks':
                # todo turn child extra drinks and fires into speratate items
                if child.name | child.size | child.modifiers:
                    err = f"Deals cannot contain drinks. {child.name} was removed."
                    self.errors.append(err)
                    child.name = None
                    child.size = None
                    child.modifiers = None
            if child.type == 'fries':
                if child.name | child.size | child.modifiers:
                    err = f"Deals cannot contain fries. {child.name} was removed."
                    self.errors.append(err)
                    child.name = None
                    child.size = None
                    child.modifiers = None
        return False

    def validate_quantity(self, item):
        if isinstance(item, OrderItem):
            if item.quantity < 1:
                self.errors.append(f"{item.name}'s quantity must be > 0. Was: {item.quantity} , Now: {max(1, abs(item.quantity))}")
                item.quantity = max(1, abs(item.quantity))
        elif isinstance(item, ChildrenItem):
            # todo create variable to see if i can transfer extra quantities to separate items in order
            if item.quantity < 1:
                self.errors.append(f"Combos and deals include quantity of exactly 1 'child' type. {item.name}'s quantity was changed from {item.quantity} to 1")
                item.quantity = 1
        return
    
    def validate_size(self, item, menu: Menu) -> bool:
        if item.type in ['combos', 'burgers', 'desserts', 'deals', 'ingredients']:
            item.size = None
        else:
            if item.size is None:
                self.handle_missing_size(item.name)
                return True
            if item.type == 'drinks':
                available_sizes = list(
                    menu.menu["drinks"][item.name]["size_price"].keys())
                if item.size not in available_sizes:
                    self.errors.append(f"Wrong size of {item.name}. Available sizes: {available_sizes}. Was '{item.size}', Now: '{available_sizes[0]}'")
                    item.size = available_sizes[0]
            if item.type == 'fries':
                available_sizes = ['small', 'medium', 'large']
                if item.size not in available_sizes:
                    self.errors.append( f"Wrong size of {item.name}. Available sizes: {available_sizes}. Was '{item.size}', Now: 'medium'")
                    item.size = 'medium'
        return False
    
    def validate_modifiers(self, item, menu: Menu):
        if item.type in ['desserts', 'deals', 'ingredients', 'virtual', 'combos']:
            item.modifiers_to_add = []
            item.modifiers_to_remove = []
        else:
            possible_ingredients = menu.menu[item.type][item.name]['possible_ingredients']
            default_ingredients = menu.menu[item.type][item.name]['default_ingredients']

            for mod in item.modifiers_to_add:
                if mod.name not in possible_ingredients:
                    self.errors.append(
                        f"You cannot add {mod.name} for {item.name}. '{mod}' was removed.")
                    item.modifiers_to_add.remove(mod)

            for mod in item.modifiers_to_remove:
                if mod.name not in default_ingredients:
                    self.errors.append(f"You cannot remove {mod.name} for {item.name}")
                    item.modifiers_to_remove.remove(mod)

    def handle_missing_name(self, name, parent_name=None) -> None:
        msg = ManagerMessage(
            f"System: What kind of {name}?", "clarify")
        if parent_name:
            msg = ManagerMessage(
                f"System: What kind of {name} for you {parent_name}?", "clarify")
        self.issue_queue.put(msg)

    def handle_missing_size(self, name, parent_name=None) -> None:
        msg = ManagerMessage(
            f"System: What size of {name}?", "clarify")
        if parent_name:
            msg = ManagerMessage(
                f"System: What size of {name} for you {parent_name}?", "clarify")
        self.issue_queue.put(msg)


def validate_menu_item(item: OrderItem):
    """Unknown item not from the menu

    Args:
        order (Order): _description_
    """
    errors = []
    if item.type not in ["burgers", "fries", "drinks", "desserts", "deals", "sauces"]:
        err = f"Error: {item.name} of type [{item.type}] is not in the menu."
        errors.append(err)
    if item.name not in []:
        pass
    return


def validate_standalone_item(item: OrderItem):
    pass


def validate_combo(order: Order):
    pass
