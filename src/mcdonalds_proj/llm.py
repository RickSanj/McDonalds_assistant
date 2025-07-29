from mcdonalds_proj.order import OrderState
from mcdonalds_proj.menu import Menu
from openai import OpenAI
from mcdonalds_proj.manager import ManagerMessage
from mcdonalds_proj.order import Order
import instructor


class LLM:
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
        Your task is to extract the customer's intent from natural language input\
        and convert it into structured data representing their order.

        Guidelines:
        - Your first task is to identify the type of the OrderItem from the provided menu. Types include 'burgers',
        'drinks', 'desserts', 'fries', 'combos', 'deals', 'ingredients'
        - Your second task is to identify the name of the OrderItem. Customers may refer to specific menu items
        or just general types (e.g., "a burger" vs. "Big Mac"). If it is a general type it will be marked as 
        'virtual: true' in the menu and will have to be clarified later on.
        - A deal includes two burgers. There are two types of deals, if user did not specify which deal
        mark name as "None". If the user ordered two burgers without asking for a double deal,
        automatically make it a double deal. If user did not specify name of the burger or orders only one,
        mark the name of burgers as None and type 'burgers'.
        - A combo meal includes one burger (inferred from the combo's name), one drink, and one fries item.
        By default, the fries are "French Fries" unless the user specifies a different side.
        If no drink is mentioned, assign a placeholder drink with the name "None".
        When the user orders a combo and also mentions drinks or fries separately, attempt to assign those
        to the combo if they fit.
        - If user did not specify the exact name of the dessert from the menu, assign a placeholder dessert with the name "None".
        - If the customer says they don't want anything else, mark `order_finished` as True and 
        do not modify the existing order.
        - If some units of a multi-quantity item have different modifiers, split them into separate OrderItems with the exact quantity and customizations.
        Never apply partial modifiers within a single OrderItem with quantity > 1.
        For combos or items with different child items or modifiers per unit, create separate OrderItems of quantity 1 for each variation.
        Do not combine differently customized units under one entry.


    
        Context:
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

    def process_dessert_offered(self, user_msg: str, manager_msg: ManagerMessage, order: Order) -> OrderState:
        system_prompt = f"""
        You are an AI assistant taking food orders at McDonald's.
        Your task is to analyze the customer's response and update the structured order data accordingly.
        Rules:
        - If user wants a dessert but does not specify a name, just add a dessert where name is None and type 'desserts'.
        Context:
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

    def process_clarify_question(self, user_msg: str, manager_msg: ManagerMessage, order: Order) -> OrderState:
        system_prompt = f"""
        You are an AI assistant taking food orders at McDonald's.
        Your task is to respond to clarification questions from the customer in a way that helps them complete their order,
        while also updating the structured order data if new details are revealed.

        Guidelines:
        - If the customer's message includes additional information about their order, update the order accordingly.
        - If it's only a clarification without changes to the order, maintain the current state.
        - Clarifications may involve menu details, portion sizes, combo details, or ingredient specifics.
        - Usually sizes are small, medium and large

        Context:
        - Current order state: {order.list}
        - System message to clarify: {manager_msg.text}
        - Menu: {str(order.menu.menu)}
        """

        response = self.client.chat.completions.create(
            model=self.model,
            max_retries=self.max_retries,
            messages=[
                {'role': 'developer', 'content': system_prompt},
                {"role": "user", "content": user_msg}
            ],
            response_model=OrderState
        )
        return response
