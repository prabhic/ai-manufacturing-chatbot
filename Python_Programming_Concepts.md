# Python Programming Concepts

## Table of Contents
1. [Basic Syntax](#basic-syntax)
2. [Data Types](#data-types)
3. [Variables](#variables)
4. [Operators](#operators)
5. [Control Flow](#control-flow)
6. [Functions](#functions)
7. [Object-Oriented Programming](#object-oriented-programming)
8. [Data Structures](#data-structures)
9. [Exception Handling](#exception-handling)
10. [File Handling](#file-handling)
11. [Modules and Packages](#modules-and-packages)
12. [Comprehensions](#comprehensions)
13. [Decorators](#decorators)
14. [Generators](#generators)
15. [Context Managers](#context-managers)

---

## Basic Syntax

### Comments
```python
# Single-line comment

"""
Multi-line comment
or docstring
"""
```

### Indentation
Python uses indentation to define code blocks (4 spaces is standard).

```python
if True:
    print("Indented code block")
```

---

## Data Types

### Numeric Types
- **int**: Integer numbers (e.g., `5`, `-10`, `1000`)
- **float**: Floating-point numbers (e.g., `3.14`, `-0.5`)
- **complex**: Complex numbers (e.g., `3+4j`)

### Sequences
- **str**: String (e.g., `"Hello"`, `'World'`)
- **list**: Mutable ordered collection (e.g., `[1, 2, 3]`)
- **tuple**: Immutable ordered collection (e.g., `(1, 2, 3)`)

### Mappings
- **dict**: Dictionary - key-value pairs (e.g., `{"name": "John", "age": 30}`)

### Sets
- **set**: Unordered collection of unique elements (e.g., `{1, 2, 3}`)
- **frozenset**: Immutable set

### Boolean
- **bool**: `True` or `False`

### None Type
- **NoneType**: `None` (represents absence of value)

---

## Variables

Variables are containers for storing data values.

```python
# Variable assignment
name = "Alice"
age = 25
height = 5.6
is_student = True

# Multiple assignment
x, y, z = 1, 2, 3

# Same value to multiple variables
a = b = c = 0
```

### Variable Naming Rules
- Must start with a letter or underscore
- Can contain letters, numbers, and underscores
- Case-sensitive (`age` and `Age` are different)
- Cannot use reserved keywords

---

## Operators

### Arithmetic Operators
```python
+    # Addition
-    # Subtraction
*    # Multiplication
/    # Division
//   # Floor division
%    # Modulus
**   # Exponentiation
```

### Comparison Operators
```python
==   # Equal to
!=   # Not equal to
>    # Greater than
<    # Less than
>=   # Greater than or equal to
<=   # Less than or equal to
```

### Logical Operators
```python
and  # Logical AND
or   # Logical OR
not  # Logical NOT
```

### Assignment Operators
```python
=    # Assignment
+=   # Add and assign
-=   # Subtract and assign
*=   # Multiply and assign
/=   # Divide and assign
```

### Identity Operators
```python
is       # Identity check
is not   # Negated identity check
```

### Membership Operators
```python
in       # Membership check
not in   # Negated membership check
```

---

## Control Flow

### If-Elif-Else
```python
age = 18

if age < 13:
    print("Child")
elif age < 20:
    print("Teenager")
else:
    print("Adult")
```

### For Loop
```python
# Iterate over a sequence
for i in range(5):
    print(i)

# Iterate over a list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)
```

### While Loop
```python
count = 0
while count < 5:
    print(count)
    count += 1
```

### Break and Continue
```python
# Break - exit loop
for i in range(10):
    if i == 5:
        break
    print(i)

# Continue - skip iteration
for i in range(5):
    if i == 2:
        continue
    print(i)
```

### Pass Statement
```python
# Placeholder for future code
for i in range(5):
    pass  # Do nothing
```

---

## Functions

### Defining Functions
```python
def greet(name):
    """Function to greet a person"""
    return f"Hello, {name}!"

result = greet("Alice")
```

### Default Parameters
```python
def greet(name="Guest"):
    return f"Hello, {name}!"
```

### Variable-Length Arguments
```python
# *args - variable positional arguments
def sum_all(*args):
    return sum(args)

# **kwargs - variable keyword arguments
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")
```

### Lambda Functions
```python
# Anonymous functions
square = lambda x: x ** 2
add = lambda x, y: x + y
```

### Recursion
```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

---

## Object-Oriented Programming

### Classes and Objects
```python
class Dog:
    # Class attribute
    species = "Canis familiaris"
    
    # Constructor
    def __init__(self, name, age):
        # Instance attributes
        self.name = name
        self.age = age
    
    # Instance method
    def bark(self):
        return f"{self.name} says Woof!"
    
    # String representation
    def __str__(self):
        return f"{self.name} is {self.age} years old"

# Creating objects
dog1 = Dog("Buddy", 3)
print(dog1.bark())
```

### Inheritance
```python
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        pass

class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"

class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"
```

### Encapsulation
```python
class BankAccount:
    def __init__(self, balance):
        self.__balance = balance  # Private attribute
    
    def deposit(self, amount):
        self.__balance += amount
    
    def get_balance(self):
        return self.__balance
```

### Polymorphism
```python
# Same method name, different implementations
class Shape:
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius ** 2
```

---

## Data Structures

### Lists
```python
# Creating lists
fruits = ["apple", "banana", "cherry"]

# List methods
fruits.append("orange")      # Add item
fruits.insert(1, "mango")    # Insert at position
fruits.remove("banana")      # Remove item
fruits.pop()                 # Remove last item
fruits.sort()                # Sort list
fruits.reverse()             # Reverse list
```

### Tuples
```python
# Immutable sequence
coordinates = (10, 20)
point = 1, 2, 3  # Parentheses optional

# Tuple unpacking
x, y = coordinates
```

### Dictionaries
```python
# Creating dictionaries
person = {
    "name": "John",
    "age": 30,
    "city": "New York"
}

# Dictionary methods
person["email"] = "john@example.com"  # Add key-value
person.get("name")                    # Get value
person.keys()                         # Get all keys
person.values()                       # Get all values
person.items()                        # Get key-value pairs
person.pop("age")                     # Remove key
```

### Sets
```python
# Unordered collection of unique elements
numbers = {1, 2, 3, 4, 5}

# Set operations
numbers.add(6)           # Add element
numbers.remove(3)        # Remove element
set1 | set2             # Union
set1 & set2             # Intersection
set1 - set2             # Difference
```

---

## Exception Handling

### Try-Except
```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
except Exception as e:
    print(f"An error occurred: {e}")
else:
    print("No errors occurred")
finally:
    print("This always executes")
```

### Raising Exceptions
```python
def validate_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    return age
```

### Custom Exceptions
```python
class CustomError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

raise CustomError("This is a custom error")
```

---

## File Handling

### Reading Files
```python
# Read entire file
with open("file.txt", "r") as file:
    content = file.read()

# Read line by line
with open("file.txt", "r") as file:
    for line in file:
        print(line.strip())

# Read all lines into list
with open("file.txt", "r") as file:
    lines = file.readlines()
```

### Writing Files
```python
# Write mode (overwrites)
with open("file.txt", "w") as file:
    file.write("Hello, World!\n")

# Append mode
with open("file.txt", "a") as file:
    file.write("Appended text\n")
```

### File Modes
- `"r"` - Read (default)
- `"w"` - Write (overwrites)
- `"a"` - Append
- `"x"` - Create (fails if exists)
- `"b"` - Binary mode
- `"t"` - Text mode (default)

---

## Modules and Packages

### Importing Modules
```python
# Import entire module
import math
print(math.sqrt(16))

# Import specific functions
from math import sqrt, pi
print(sqrt(16))

# Import with alias
import numpy as np
import pandas as pd

# Import all (not recommended)
from math import *
```

### Creating Modules
```python
# mymodule.py
def greet(name):
    return f"Hello, {name}!"

PI = 3.14159

# In another file
import mymodule
print(mymodule.greet("Alice"))
print(mymodule.PI)
```

---

## Comprehensions

### List Comprehension
```python
# Basic syntax: [expression for item in iterable if condition]
squares = [x**2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
```

### Dictionary Comprehension
```python
# {key: value for item in iterable}
squares_dict = {x: x**2 for x in range(5)}
```

### Set Comprehension
```python
# {expression for item in iterable}
unique_squares = {x**2 for x in [1, 2, 2, 3, 3, 4]}
```

---

## Decorators

Decorators modify the behavior of functions or classes.

```python
def my_decorator(func):
    def wrapper():
        print("Before function call")
        func()
        print("After function call")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
```

### Decorator with Arguments
```python
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Hello, {name}!")
```

---

## Generators

Generators are functions that yield values one at a time.

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

# Using generator
for num in countdown(5):
    print(num)

# Generator expression
squares_gen = (x**2 for x in range(10))
```

### Benefits
- Memory efficient (lazy evaluation)
- Can represent infinite sequences
- Useful for large datasets

---

## Context Managers

Context managers handle resource management (like files).

```python
# Using 'with' statement
with open("file.txt", "r") as file:
    content = file.read()
# File automatically closed

# Creating custom context manager
class MyContext:
    def __enter__(self):
        print("Entering context")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exiting context")
        return False

with MyContext() as ctx:
    print("Inside context")
```

### Using contextlib
```python
from contextlib import contextmanager

@contextmanager
def my_context():
    print("Setup")
    yield
    print("Teardown")

with my_context():
    print("Inside context")
```

---

## Additional Concepts

### String Methods
```python
text = "Hello, World!"
text.lower()           # Convert to lowercase
text.upper()           # Convert to uppercase
text.strip()           # Remove whitespace
text.split(",")        # Split into list
text.replace("Hello", "Hi")  # Replace substring
text.startswith("Hello")     # Check prefix
text.endswith("!")           # Check suffix
```

### f-Strings (Formatted String Literals)
```python
name = "Alice"
age = 25
print(f"My name is {name} and I am {age} years old")
print(f"Next year I'll be {age + 1}")
```

### Enumerate and Zip
```python
# Enumerate - get index and value
for index, fruit in enumerate(["apple", "banana", "cherry"]):
    print(f"{index}: {fruit}")

# Zip - combine iterables
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]
for name, age in zip(names, ages):
    print(f"{name} is {age} years old")
```

### Map, Filter, Reduce
```python
from functools import reduce

# Map - apply function to each item
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))

# Filter - filter items based on condition
evens = list(filter(lambda x: x % 2 == 0, numbers))

# Reduce - reduce sequence to single value
sum_all = reduce(lambda x, y: x + y, numbers)
```

---

## Best Practices

1. **Follow PEP 8** - Python's style guide
2. **Use meaningful variable names** - `user_name` not `x`
3. **Write docstrings** - Document your functions and classes
4. **Use virtual environments** - Isolate project dependencies
5. **Handle exceptions** - Don't let your program crash unexpectedly
6. **Use list comprehensions** - More Pythonic and efficient
7. **Avoid global variables** - Use function parameters instead
8. **Keep functions small** - Each function should do one thing well
9. **Use context managers** - For resource management
10. **Write tests** - Test your code to ensure it works correctly

---

## Conclusion

This document covers essential Python programming concepts. Practice these concepts regularly to become proficient in Python. Remember, the best way to learn programming is by writing code!
