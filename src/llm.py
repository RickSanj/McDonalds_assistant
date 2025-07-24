from order import OrderState
from menu import get_menu
from openai import OpenAI
from manager import ManagerMessage
from order import Order
import instructor


class LLM:
    def __init__(self) -> None:
        self.model = 'gpt-4.1-mini'
        self.max_retries = 5
        self.client = instructor.from_openai(OpenAI())

    def process(self, user_msg: str, manager_msg: ManagerMessage, order: Order) -> OrderState:
        if manager_msg.flag == "dessert_offered":
            return self.process_dessert_offered(user_msg, manager_msg, order)
        if manager_msg.flag == "general":
            return self.process_general_question(user_msg, manager_msg, order)

    def process_general_question(self, user_msg: str, manager_msg: ManagerMessage, order: Order) -> OrderState:
        system_prompt = f"""
        You are an AI assistant responsible for taking food orders at McDonald's. 
        Your task is to extract the customer's intent from natural language input and convert it into structured data representing their order.

        Guidelines:
        - A combo meal can include one drink and one fries item.
        - Customers may refer to specific menu items or just general types (e.g., "a burger" vs. "Big Mac").
        - If the customer says they don't want anything else, mark `order_finished` as True and do not modify the existing order.
        - If the user ordered a combo, try to assign any separately mentioned drinks or fries into the combo, when appropriate.

        Context:
        - Current order state: {order.list}
        - Assistant's message: {manager_msg.text}
        - Menu: {get_menu()}
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

        Context:
        - Current order state: {order.list}
        - Assistant's message: {manager_msg.text}
        - Menu: {get_menu()}
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

    def specify_item(self, system_msg: str, user_msg: str) -> str:
        return "To implement"

    def specify_item_size(self, system_msg: str, user_msg: str) -> str:
        return "To implement"
