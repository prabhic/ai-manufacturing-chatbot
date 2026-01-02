"""
Python Programming Concepts - Comprehensive Guide
This file demonstrates various Python programming concepts with examples
"""

# ====================
# 1. DATA TYPES
# ====================

# Basic data types
integer_example = 42
float_example = 3.14159
string_example = "Hello, Python!"
boolean_example = True
none_example = None

# Complex data types
list_example = [1, 2, 3, 4, 5]
tuple_example = (10, 20, 30)
set_example = {1, 2, 3, 4, 5}
dict_example = {"name": "John", "age": 30, "city": "NYC"}


# ====================
# 2. CONTROL STRUCTURES
# ====================

def demonstrate_control_structures():
    """Examples of if-else, loops, and control flow"""
    
    # If-Elif-Else
    age = 18
    if age < 13:
        print("Child")
    elif age < 20:
        print("Teenager")
    else:
        print("Adult")
    
    # For loop
    for i in range(5):
        print(f"Iteration: {i}")
    
    # While loop
    count = 0
    while count < 3:
        print(f"Count: {count}")
        count += 1
    
    # Break and continue
    for num in range(10):
        if num == 3:
            continue  # Skip 3
        if num == 7:
            break  # Stop at 7
        print(num)


# ====================
# 3. FUNCTIONS
# ====================

def simple_function():
    """Basic function with no parameters"""
    return "Hello from function!"


def function_with_params(name, age):
    """Function with required parameters"""
    return f"{name} is {age} years old"


def function_with_defaults(name, greeting="Hello"):
    """Function with default parameters"""
    return f"{greeting}, {name}!"


def function_with_args(*args):
    """Function with variable arguments"""
    return sum(args)


def function_with_kwargs(**kwargs):
    """Function with keyword arguments"""
    return kwargs


def lambda_examples():
    """Lambda (anonymous) functions"""
    square = lambda x: x ** 2
    add = lambda x, y: x + y
    
    return square(5), add(3, 7)


# ====================
# 4. OBJECT-ORIENTED PROGRAMMING
# ====================

class Animal:
    """Base class demonstrating OOP concepts"""
    
    def __init__(self, name, species):
        self.name = name
        self.species = species
    
    def speak(self):
        return f"{self.name} makes a sound"
    
    def __str__(self):
        return f"{self.name} ({self.species})"


class Dog(Animal):
    """Inherited class demonstrating inheritance"""
    
    def __init__(self, name, breed):
        super().__init__(name, "Dog")
        self.breed = breed
    
    def speak(self):
        return f"{self.name} barks!"
    
    def fetch(self):
        return f"{self.name} is fetching the ball"


class Cat(Animal):
    """Another inherited class"""
    
    def __init__(self, name, color):
        super().__init__(name, "Cat")
        self.color = color
    
    def speak(self):
        return f"{self.name} meows!"


# ====================
# 5. LIST COMPREHENSIONS
# ====================

def list_comprehension_examples():
    """Various list comprehension patterns"""
    
    # Basic list comprehension
    squares = [x**2 for x in range(10)]
    
    # With condition
    even_squares = [x**2 for x in range(10) if x % 2 == 0]
    
    # Nested comprehension
    matrix = [[i*j for j in range(1, 4)] for i in range(1, 4)]
    
    # Dictionary comprehension
    square_dict = {x: x**2 for x in range(5)}
    
    # Set comprehension
    unique_squares = {x**2 for x in range(-5, 6)}
    
    return squares, even_squares, matrix, square_dict, unique_squares


# ====================
# 6. EXCEPTION HANDLING
# ====================

def exception_handling_examples():
    """Demonstrating try-except blocks"""
    
    # Basic exception handling
    try:
        result = 10 / 0
    except ZeroDivisionError:
        print("Cannot divide by zero!")
    
    # Multiple exceptions
    try:
        value = int("abc")
    except (ValueError, TypeError) as e:
        print(f"Error: {e}")
    
    # Try-except-else-finally
    try:
        file_content = "Sample data"
    except Exception as e:
        print(f"Error: {e}")
    else:
        print("Operation successful")
    finally:
        print("Cleanup operations")


# ====================
# 7. FILE OPERATIONS
# ====================

def file_operations_examples():
    """Working with files"""
    
    # Writing to a file
    with open("sample.txt", "w") as file:
        file.write("Hello, World!\n")
        file.write("Python File Operations\n")
    
    # Reading from a file
    with open("sample.txt", "r") as file:
        content = file.read()
        print(content)
    
    # Reading line by line
    with open("sample.txt", "r") as file:
        for line in file:
            print(line.strip())
    
    # Appending to a file
    with open("sample.txt", "a") as file:
        file.write("Appended line\n")


# ====================
# 8. DECORATORS
# ====================

def timer_decorator(func):
    """Decorator to measure function execution time"""
    import time
    
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    
    return wrapper


@timer_decorator
def slow_function():
    """Function decorated with timer"""
    import time
    time.sleep(0.1)
    return "Done!"


# ====================
# 9. GENERATORS
# ====================

def simple_generator():
    """Basic generator function"""
    yield 1
    yield 2
    yield 3


def fibonacci_generator(n):
    """Generator for Fibonacci sequence"""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


def generator_expression_example():
    """Generator expressions (memory efficient)"""
    # Generator expression
    squares_gen = (x**2 for x in range(1000000))
    
    # Use only what you need
    first_five = [next(squares_gen) for _ in range(5)]
    return first_five


# ====================
# 10. CONTEXT MANAGERS
# ====================

class CustomContextManager:
    """Custom context manager using __enter__ and __exit__"""
    
    def __init__(self, name):
        self.name = name
    
    def __enter__(self):
        print(f"Entering {self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Exiting {self.name}")
        return False


# ====================
# 11. ADVANCED DATA STRUCTURES
# ====================

from collections import namedtuple, defaultdict, Counter, deque

def advanced_collections_examples():
    """Using specialized collection types"""
    
    # Named tuple
    Point = namedtuple('Point', ['x', 'y'])
    p = Point(10, 20)
    
    # Default dict
    word_count = defaultdict(int)
    for word in ['apple', 'banana', 'apple']:
        word_count[word] += 1
    
    # Counter
    letters = Counter('mississippi')
    
    # Deque (double-ended queue)
    dq = deque([1, 2, 3])
    dq.append(4)
    dq.appendleft(0)
    
    return p, dict(word_count), letters, list(dq)


# ====================
# 12. FUNCTIONAL PROGRAMMING
# ====================

def functional_programming_examples():
    """Map, filter, reduce examples"""
    from functools import reduce
    
    numbers = [1, 2, 3, 4, 5]
    
    # Map: apply function to all elements
    squared = list(map(lambda x: x**2, numbers))
    
    # Filter: select elements based on condition
    evens = list(filter(lambda x: x % 2 == 0, numbers))
    
    # Reduce: combine all elements into single value
    product = reduce(lambda x, y: x * y, numbers)
    
    return squared, evens, product


# ====================
# 13. REGULAR EXPRESSIONS
# ====================

import re

def regex_examples():
    """Pattern matching with regular expressions"""
    
    text = "Contact: john@example.com or jane@test.com"
    
    # Find all email addresses
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    
    # Replace pattern
    censored = re.sub(r'\b\w+@\w+\.\w+\b', '[EMAIL]', text)
    
    # Match pattern
    phone = "123-456-7890"
    if re.match(r'\d{3}-\d{3}-\d{4}', phone):
        print("Valid phone number")
    
    return emails, censored


# ====================
# 14. MODULES AND IMPORTS
# ====================

# Standard library imports
import os
import sys
import json
import datetime

# Import specific functions
from math import sqrt, pi
from random import randint, choice

# Import with alias
import numpy as np  # This would work if numpy is installed


# ====================
# 15. MAIN EXECUTION
# ====================

def main():
    """Main function demonstrating all concepts"""
    
    print("=" * 50)
    print("PYTHON PROGRAMMING CONCEPTS")
    print("=" * 50)
    
    print("\n1. Data Types:")
    print(f"Integer: {integer_example}")
    print(f"Float: {float_example}")
    print(f"String: {string_example}")
    print(f"List: {list_example}")
    print(f"Dictionary: {dict_example}")
    
    print("\n2. Control Structures:")
    demonstrate_control_structures()
    
    print("\n3. Functions:")
    print(simple_function())
    print(function_with_params("Alice", 25))
    print(function_with_defaults("Bob"))
    print(f"Sum of args: {function_with_args(1, 2, 3, 4, 5)}")
    
    print("\n4. Object-Oriented Programming:")
    dog = Dog("Buddy", "Golden Retriever")
    cat = Cat("Whiskers", "Orange")
    print(dog.speak())
    print(cat.speak())
    print(dog.fetch())
    
    print("\n5. List Comprehensions:")
    squares, evens, matrix, sq_dict, _ = list_comprehension_examples()
    print(f"Squares: {squares}")
    print(f"Even squares: {evens}")
    
    print("\n6. Exception Handling:")
    exception_handling_examples()
    
    print("\n7. Generators:")
    print(f"Fibonacci: {list(fibonacci_generator(10))}")
    print(f"Generator expression: {generator_expression_example()}")
    
    print("\n8. Advanced Collections:")
    p, wc, letters, dq = advanced_collections_examples()
    print(f"Point: {p}")
    print(f"Word count: {wc}")
    print(f"Letter count: {letters}")
    
    print("\n9. Functional Programming:")
    squared, evens, product = functional_programming_examples()
    print(f"Squared: {squared}")
    print(f"Evens: {evens}")
    print(f"Product: {product}")
    
    print("\n10. Regular Expressions:")
    emails, censored = regex_examples()
    print(f"Emails found: {emails}")
    print(f"Censored text: {censored}")
    
    print("\n" + "=" * 50)
    print("END OF PYTHON CONCEPTS DEMONSTRATION")
    print("=" * 50)


if __name__ == "__main__":
    main()
