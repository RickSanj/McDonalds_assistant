import json
from order import Order, OrderItem
from queue import Queue


class ValidationError(Exception):
    """
    Custom exception raised for specific errors when validatig user's order.
    """

    def __init__(self, message, _type):
        self.message = message
        self._type = _type
        super().__init__(self.message)


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
            text += f"Your order total is ${order.calculate_total()}."
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
        if order.dessert_offered is False:
            self.offer_dessert()
            order.dessert_offered = True

    def validate(self, order: Order):
        errors = []
        if not order.list:
            errors.append(ValidationError(
                "System: No items were ordered. Try again.", ""))
        for item in order.list:
            if item.type == 'combo':
                if item.name is None:
                    msg = ManagerMessage(
                        f"System: Which kind of {item.type}?", "clarify")
                    self.issue_queue.put(msg)
                for child in item.children:
                    if child.type == 'burgers':
                        if child.name is None:
                            msg = ManagerMessage(
                                f"System: What kind of burger for your {item.name} [combo]?", "clarify")
                            self.issue_queue.put(msg)
                        if child.modifiers:
                            # todo
                            pass
                    if child.type == 'drinks':
                        if child.name is None:
                            msg = ManagerMessage(
                                f"System: What kind of drink for your {item.name} [combo]?", "clarify")
                            self.issue_queue.put(msg)
                        if child.size is None:
                            msg = ManagerMessage(
                                f"System: What size of {child.name} for your {item.name} [combo]?", "clarify")
                            self.issue_queue.put(msg)
                        if child.modifiers:
                            # todo
                            pass
                    if child.type == 'fries':
                        if child.name is None:
                            child.name = 'French Fries'
                        if child.size is None:
                            msg = ManagerMessage(
                                f"System: What size of {child.name} for your {item.name} [combo]?", "clarify")
                            self.issue_queue.put(msg)
                        if child.modifiers:
                            # todo
                            pass
            elif item.type == 'burgers':
                if child.name is None:
                    msg = ManagerMessage(
                        f"System: What kind of burger", "clarify")
                    self.issue_queue.put(msg)
                if child.modifiers:
                    # todo
                    pass
            elif item.type == 'drinks':
                if item.name is None:
                    msg = ManagerMessage(
                        f"System: What kind of drink?", "clarify")
                    self.issue_queue.put(msg)
                if item.size is None:
                    msg = ManagerMessage(
                        f"System: What size of {item.name}?", "clarify")
                    self.issue_queue.put(msg)
                if item.modifiers:
                    # todo
                    pass
            elif item.type == 'fries':
                if item.name is None:
                    msg = ManagerMessage(
                        f"System: What kind of fries?", "clarify")
                    self.issue_queue.put(msg)
                if item.size is None:
                    msg = ManagerMessage(
                        f"System: What size of {item.name}?", "clarify")
                    self.issue_queue.put(msg)
                if item.modifiers:
                    # todo
                    pass
            elif item.type == 'desserts':
                order.dessert_offered = True
                if item.name is None:
                    msg = ManagerMessage(
                        f"System: What kind of dessert?", "clarify")
                    self.issue_queue.put(msg)
                if item.modifiers:
                    # todo
                    pass
            elif item.type == 'deals':
                # order.dessert_offered = True
                if item.name is None:
                    msg = ManagerMessage(
                        f"System: What kind of deal?", "clarify")
                    self.issue_queue.put(msg)
                for child in item.children:
                    if child.type == 'burgers':
                        if child.name is None:
                            msg = ManagerMessage(
                                f"System: Which two burgers for your {item.name} [deal]?", "clarify")
                            self.issue_queue.put(msg)
                        if child.modifiers:
                            # todo
                            pass
                    if child.type == 'drinks':
                        if child.name | child.size | child.modifiers:
                            err = ValidationError(
                                f"Deals cannot contain drinks. {child.name} was removed.", "clarify")
                            errors.append(err)
                            child.name = None
                            child.size = None
                            child.modifiers = None
                    if child.type == 'fries':
                        if child.name | child.size | child.modifiers:
                            err = ValidationError(
                                f"Deals cannot contain fries. {child.name} was removed.", "clarify")
                            errors.append(err)
                            child.name = None
                            child.size = None
                            child.modifiers = None

        # for i in order.list:
        #     validate_menu_item(i)
        #     validate_structure(i)
        #     validate_combo(i)
        #     validate_standalone_item(i)
        return errors


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
    if item.quantity <= 0:
        err = f"Error: quantity of {item.name} has to be more than 0."
        errors.append(err)

    # item.name
    # item.type
    # if item.modifiers:

    # if item.children:
    #     res += "      With:\n"
    #     for child in item.children:
    #         res += f"        * [{child.type}]: {child.name} {child.size} {child.modifiers}\n"
    return


def validate_structure(item: OrderItem):
    """Non-empty order: order.items should not be empty.
Combos or double_deals must have children(children field).
Each OrderItem with type = "combo" should contain:
Exactly 1 burge
Exactly 1 drink
Exactly 1 fries
Prevent nested combos(e.g., a combo inside a combo).

    Args:
        order (Order): _description_
    """
    pass


def validate_value(item: OrderItem):
    """Ensure each field is within allowed options.
Examples:
type is one of: "burger", "drink", "dessert", "fries", "combo", "double_deal"
size is either None or one of: "small", "medium", "large"
quantity is a positive integer (≥ 1)
modifiers are strings and match known modifiers (if you have a controlled list)

    Args:
        oredr (Order): _description_
    """
    pass


def validate_standalone_item(item: OrderItem):
    pass


def validate_combo(order: Order):
    pass
