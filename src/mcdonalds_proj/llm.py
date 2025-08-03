"""
This module is responsible for all actions related to LLM.
"""

from openai import OpenAI
import instructor
from mcdonalds_proj.order import OrderState
from mcdonalds_proj.manager import ManagerMessage
from mcdonalds_proj.order import Order

class LLM:
    """
    Class to replesent LLM object
    """
    def __init__(self) -> None:
        self.model = 'gpt-4.1-mini'
        self.max_retries = 5
        self.client = instructor.from_openai(OpenAI())

    def process(self, user_msg: str, manager_msg: ManagerMessage, order: Order) -> OrderState:
        if manager_msg.flag == "dessert_offered":
            return self.process_general_question(user_msg, manager_msg, order)
        if manager_msg.flag == "general":
            return self.process_general_question(user_msg, manager_msg, order)
        if manager_msg.flag == "clarify":
            return self.process_general_question(user_msg, manager_msg, order)

    def process_general_question(self, user_msg: str, manager_msg: ManagerMessage, order: Order) -> OrderState:
        system_prompt = f"""
        You are an AI assistant responsible for taking food orders at McDonald's. 
        Your task is to extract the customer's intent from natural language input
        and convert it into structured data representing their order. 
        Depending on the context you should update the order or start over.

        --- GUIDELINES ---

        1. GENERAL ORDER STRUCTURE  
        - Each order consists of one or more 'OrderItem' entries.
        - Each OrderItem includes: 'type', 'name', 'size', 'quantity', 'modifiers', and optionally, 'children' for nested items.
        - OrderItem types include: 'burgers', 'drinks', 'desserts' ('ice cream' as subcategory of desserts), 'fries', 'combos', 'deals', 'ingredients', 'sauces'.

        2. 'order_finished' FLAG  
        - Only when asked 'Would you like anything else?' If the customer indicates they don't want anything else (e.g., "that's all", "no, thanks"), set 'order_finished = True'. 
        - 

        3. TYPE & NAME DETECTION  
        - First, identify the correct 'type' of each item.
        - Then, extract the specific 'name'. If the user gives only a general reference (e.g., "a burger", "some fries"), use a placeholder name "None".

        4. COMBO RULES  
        - A combo (e.g., "Big Mac Meal") includes three sub items:
            - a burger (inferred from combo name e.g., "Big Mac),
            - one drink (if not mentioned, use name="None"),
            - one fries item (default is "French Fries" if unspecified),
            - optionally a sauce to the modifiers_to_add.
        - If the user lists drink/fries/sauce ingredient separately and they logically match a combo, assign them as children of the combo.
        - For modifiers (e.g., "no ice", "add Ranch"), assign them to the correct nested item.
        - If 'Sauce was offered' is in modifiers_to_remove, keep it there and do not remove it. 
        - User may specify multiple sub items in the same message

        5. DEALS  
        - A deal includes two burgers.
        - There are two types of deals that include different types of burgers. See the menu.
        - If the user asks for a "deal" without naming it or only 1 burger is named, assign 'name = None'.

        6. INGREDIENT MODIFIERS  
        - Modifiers include both removals (from default_ingredients) and additions (from possible_ingredients).
        - Sauces are treated as optional modifiers for combos and fries - modifiers_to_add.
        - If the user modifies only part of a multi-quantity item (e.g., "remove onion from 2 of 5 burgers"), split into two separate OrderItems with respective quantities and modifiers.

        7. QUANTITY RULES  
        - Items with different customizations must be represented as individual OrderItems with quantity = 1.
        - Never group differently customized items under one entry.

        8. ITEM TRANSFORMATIONS
        - If the user wants to transform one item to another allow that (e.g. 'French Fries' to 'Potato Dips').
        - If the user orders a burger and asks to "make it a combo", convert that burger into a combo. Same about deals.
        - Preserve all modifiers when converting it into another item.

        9. DESSERTS & ICE CREAM  
        - User may use general reference to dessert as dessert or as ice cream. See virtual in menu.
        - If user did not specify name of the ice cream, replace type of the item to 'ice cream'

        10. INVALID ENTRIES  
        - Ingredients cannot be ordered standalone. Ignore if attempted.
    
        --- CONTEXT ---
        - Current order state: {order.list}
        - Assistant's message: {manager_msg.text}
        - Menu: {str(order.menu.menu)}
        """

        response = self.client.chat.completions.create(
            model=self.model,
            max_retries=self.max_retries,
            messages=[{
                'role': 'developer',
                'content': system_prompt
            },
                {"role": "user",
                 "content": user_msg}
            ],
            response_model=OrderState
        )
        return response
