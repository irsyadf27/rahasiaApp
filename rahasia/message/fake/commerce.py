#!/usr/bin/python
import random
import string

class Commerce:
    def __init__(self):
        self.list_color = (
            "red", "green", "blue", "yellow", "purple", "mint green", "teal", "white", "black", "orange", "pink", \
            "grey", "maroon", "violet", "turquoise", "tan", "sky blue", "salmon", "plum", "orchid", "olive", "magenta", \
            "lime", "ivory", "indigo", "gold", "fuchsia", "cyan", "azure", "lavender", "silver")

        self.list_department = ( "Books", "Movies", "Music", "Games", "Electronics", "Computers", "Home", "Garden", "Tools", "Grocery", "Health", "Beauty", "Toys", "Kids", "Baby", "Clothing", "Shoes", "Jewelery", "Sports", "Outdoors", "Automotive", "Industrial")

        self.list_product_name = {
            "adjective": ( "Small", "Ergonomic", "Rustic", "Intelligent", "Gorgeous", "Incredible", "Fantastic", "Practical", "Sleek", "Awesome", "Generic", "Handcrafted", "Handmade", "Licensed", "Refined", "Unbranded", "Tasty"),
            "material": ( "Steel", "Wooden", "Concrete", "Plastic", "Cotton", "Granite", "Rubber", "Metal", "Soft", "Fresh", "Frozen"),
            "product": ( "Chair", "Car", "Computer", "Keyboard", "Mouse", "Bike", "Ball", "Gloves", "Pants", "Shirt", "Table", "Shoes", "Hat", "Towels", "Soap", "Tuna", "Chicken", "Fish", "Cheese", "Bacon", "Pizza", "Salad", "Sausages", "Chips")
        }

    def color(self):
        return string.capwords(random.choice(self.list_color))

    def department(self):
        return random.choice(self.list_department)

    def productAdjective(self):
        return random.choice(self.list_product_name['adjective'])

    def productMaterial(self):
        return random.choice(self.list_product_name['material'])

    def product(self):
        return random.choice(self.list_product_name['product'])

    def productName(self):
        return "%s %s %s" % (self.productAdjective(), self.productMaterial(), self.product())

    def productNameWithColor(self):
        return "%s %s" % (self.color(), self.productName())