import unittest
from mcdonalds_proj.manager import Manager, ManagerMessage
from mcdonalds_proj.menu import Menu
from mcdonalds_proj.order import OrderState, Order, OrderItem, ChildrenItem, IngredientsItem
from mcdonalds_proj.llm import LLM

class TestValidation(unittest.TestCase):
    def test_llm_output(self):
        manager = Manager()
        menu = Menu()
        order = Order(menu)
        llm = LLM()

        manager_msg = ManagerMessage(
            "System: Welcome to McDonald's! What can I get you started with?", "general")

        text1 = "Give me 2 Cheeseburger Meals, one with Sprite no ice, the other with Apple Juice. Add Ranch to both and one McFlurry with Oreo"
        ans1 = OrderState([OrderItem(name='Big Mac Meal', type='combos', size=None, quantity=1, modifiers_to_add=[], modifiers_to_remove=[], children=[ChildrenItem(name='Big Mac', type='burgers', size=None, modifiers_to_add=[], modifiers_to_remove=[], quantity=1), ChildrenItem(name='Fanta', type='drinks', size='medium', modifiers_to_add=[], modifiers_to_remove=[], quantity=1), ChildrenItem(name='Potato Dips', type='fries', size='large', modifiers_to_add=[IngredientsItem(name='Ketchup', quantity=1)], modifiers_to_remove=[], quantity=1)]), OrderItem(name='Chocolate Chip Cookie', type='desserts', size=None, quantity=1, modifiers_to_add=[], modifiers_to_remove=[], children=None)], order_finished = False)
        llm_response = llm.process(text1, manager_msg, order)
        print(llm_response)
        assert ans1 == llm.process(text1, manager_msg, order)

    def test_validate_empty_order(self):
        err = "System: No items were ordered. Try again."
        manager = Manager()
        menu = Menu()
        order = Order(menu)

        manager.validate(order, menu)

        assert "System: No items were ordered. Try again." in manager.errors
        assert order.list == []


    def test_validate_standalone_ingredient(self):
        manager = Manager()
        menu = Menu()
        order = Order(menu)

        order.list = [
            OrderItem(name="Cheese Slice", type="ingredients", quantity=1)
        ]

        manager.validate(order, menu)
        print(order.list)
        assert order.list == []





if __name__ == '__main__':
    unittest.main()
