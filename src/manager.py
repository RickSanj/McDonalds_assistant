import json
from order import Order, OrderItem
from queue import Queue


class ManagerMessage():
    def __init__(self, text: str, flag: str) -> None:
        """_summary_

        Args:
            text (str): text of the manager's message. It can be question
            flag (str): "start" - manager greets user
                            "end" - manager prints order and total
                            "offer" - manager offers dessert
                            "clarify" - manager clarifies an item in the order
        """
        self.text = text
        self.flag = flag


class Manager:
    def __init__(self):
        self.message_queue = Queue()
        self.dessert_offered = False

    def start_taking_order(self) -> str:
        msg = ManagerMessage(
            "System: Welcome to McDonald's! What can I get you started with?", "general")
        self.message_queue.put(msg)

    def finish_taking_order(self, order: Order) -> str:
        msg = ManagerMessage(
            f"System: {order.summary()}. \n \
               Your order total is ${order.calculate_total()}.", "finished")
        self.message_queue.put(msg)

    def last_call(self) -> str:
        msg = ManagerMessage(
            "System: Would you like anything else?", "general")
        self.message_queue.put(msg)


    def update_order(self, order, llm_response):
        order.list = llm_response.items
        order.finished = llm_response.order_finished
        order.summary()


    def offer_dessert(self):
        msg = ManagerMessage(
            "System: Would you like something for dessert?", "dessert_offered")
        self.message_queue.put(msg)

    def apply_business_rules(self, order: Order):
        ### turn into deals
        if self.dessert_offered is False:
            self.offer_dessert()
            self.dessert_offered = True

    def validate(self, order: Order):
        errors = []
        for i in order.list:
            validate_menu_item(i)
            validate_structure(i)
            validate_combo(i)
            validate_standalone_item(i)
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
