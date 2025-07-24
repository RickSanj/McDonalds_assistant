from manager import Manager
from order import Order
from llm import LLM
from dotenv import load_dotenv
from datetime import datetime

import logging
import json


def main():
    # logging.basicConfig(filename=f"./logs/{datetime.now()}.log",
    #                     format='%(asctime)s %(message)s',
    #                     filemode='w')
    # logger = logging.getLogger()
    # logger.setLevel(logging.critical)

    # logger.debug("Harmless debug Message")
    # logger.info("Just an information")
    # logger.warning("Its a Warning")
    # logger.error("Did you try to divide by zero")
    # logger.critical("Internet is down")

    load_dotenv()

    manager = Manager()
    llm = LLM()
    order = Order()

    # print("Test3", flush=True)
    manager.start_taking_order()

    while order.finished is False:
        while manager.message_queue.empty() is False:
            manager_msg = manager.message_queue.get()
            print(manager_msg.text)

            user_msg = input("User: ")

            llm_response = llm.process(user_msg, manager_msg, order)

            manager.update_order(order, llm_response)
            errors = manager.validate(order)
            if errors:
                print(errors)
            while manager.issue_queue.empty() is False:
                manager_msg = manager.issue_queue.get()
                print(manager_msg.text)

                user_msg = input("User: ")

                llm_response = llm.process(user_msg, manager_msg, order)

                manager.update_order(order, llm_response)
                errors = manager.validate(order)
                if errors:
                    print(errors)

            manager.apply_business_rules(order)

        if order.finished is False:
            manager.last_call()


    manager.finish_taking_order(order)
    manager_msg = manager.message_queue.get()
    print(manager_msg.text)
    return 0


if __name__ == "__main__":
    main()
