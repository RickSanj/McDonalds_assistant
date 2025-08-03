from mcdonalds_proj.manager import Manager
from mcdonalds_proj.order import Order
from mcdonalds_proj.menu import Menu
from mcdonalds_proj.llm import LLM

from dotenv import load_dotenv

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

    menu = Menu()
    manager = Manager()
    llm = LLM()
    order = Order(menu)

    manager.start_taking_order()

    while order.finished is False:
        while manager.message_queue.empty() is False:
            manager_msg = manager.message_queue.get()
            print(manager_msg.text)

            user_msg = input("User: ")

            llm_response = llm.process(user_msg, manager_msg, order)
            print(llm_response)
            print("LLM print:")
            for i in llm_response.items:
                print('---- ', i.name, i.type, i.size,
                      i.quantity, i.modifiers_to_add, i.modifiers_to_remove)
                if i.children:
                    for j in i.children:
                        print('-------- ', j.name, j.type,
                              j.modifiers_to_add, j.modifiers_to_remove)

            manager.update_order(order, llm_response)
            manager.validate(order, menu)
            print(manager.get_errors())
            print(order.summary())

            while manager.issue_queue.empty() is False:
                manager_msg = manager.issue_queue.get()
                print(manager_msg.text)

                user_msg = input("User: ")

                llm_response = llm.process(user_msg, manager_msg, order)

                print("LLM print:")
                for i in llm_response.items:
                    print('---- ', i.name, i.type, i.size,
                        i.quantity, i.modifiers_to_add, i.modifiers_to_remove)
                    if i.children:
                        for j in i.children:
                            print('-------- ', j.name, j.type,
                                j.modifiers_to_add, j.modifiers_to_remove)

                manager.update_order(order, llm_response)
                manager.validate(order, menu)
                print(manager.get_errors())
                print(order.summary())

            manager.apply_business_rules(order, menu)

        if order.finished is False:
            manager.last_call()


    manager.finish_taking_order(order)
    manager_msg = manager.message_queue.get()
    print(manager_msg.text)
    return 0


if __name__ == "__main__":
    main()
