# Sample Python Program
# A simple demonstration of Python basics

def greet(name):
    """Return a greeting message."""
    return f"Hello, {name}! Welcome to Python programming."


def calculate_sum(numbers):
    """Calculate the sum of a list of numbers."""
    return sum(numbers)


def is_even(number):
    """Check if a number is even."""
    return number % 2 == 0


def main():
    # Greeting example
    print(greet("World"))
    
    # List operations
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print(f"Numbers: {numbers}")
    print(f"Sum: {calculate_sum(numbers)}")
    
    # Filter even numbers
    even_numbers = [n for n in numbers if is_even(n)]
    print(f"Even numbers: {even_numbers}")
    
    # Dictionary example
    person = {
        "name": "Alice",
        "age": 25,
        "city": "New York"
    }
    print(f"\nPerson info: {person}")
    
    # Loop through dictionary
    print("\nDetails:")
    for key, value in person.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
