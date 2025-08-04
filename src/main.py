from dotenv import load_dotenv
from termcolor import colored

from mcdonalds_proj.manager import Manager
from mcdonalds_proj.order import Order
from mcdonalds_proj.menu import Menu
from mcdonalds_proj.llm import LLM


def main():
    load_dotenv()

    menu = Menu()
    manager = Manager()
    llm = LLM()
    order = Order(menu)

    manager.start_taking_order()

    while order.finished is False:
        while manager.message_queue.empty() is False:
            manager_msg = manager.message_queue.get()
            print(colored(manager_msg.text, 'red'))

            user_msg = input("User: ")

            llm_response = llm.process(user_msg, manager_msg, order)
            # print(llm_response)

            manager.update_order(order, llm_response)
            manager.validate(order, menu)

            print(colored(manager.get_errors(), 'red'))
            # print(order.summary())

            handle_issues(manager, llm, order, menu)

            manager.apply_business_rules(order, menu)

        if order.finished is False:
            manager.last_call()


    manager.finish_taking_order(order)
    manager_msg = manager.message_queue.get()
    print(colored(manager_msg.text, 'red'))
    return 0


def handle_issues(manager: Manager, llm: LLM, order: Order, menu: Menu):
    while manager.issue_queue.empty() is False:
        manager_msg = manager.issue_queue.get()
        print(colored(manager_msg.text, 'red'))

        user_msg = input("User: ")

        llm_response = llm.process(user_msg, manager_msg, order)
        # print(llm_response)

        manager.update_order(order, llm_response)
        manager.validate(order, menu)

        # print(order.summary())
        print(colored(manager.get_errors(), 'red'))

if __name__ == "__main__":
    main()
