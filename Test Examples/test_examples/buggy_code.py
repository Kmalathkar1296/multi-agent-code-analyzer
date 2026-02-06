"""
Example Python file with various code issues for testing
This file intentionally contains bugs, security issues, and performance problems
"""

import random
import os

# Security Issue: Hardcoded password
PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdef"

# Logic Error: Mutable default argument
def append_to_list(item, my_list=[]):
    my_list.append(item)
    return my_list

# Performance Issue: String concatenation in loop
def build_string(items):
    result = ""
    for item in items:
        result = result + str(item) + ","
    return result

# Bug: Resource leak - file not properly closed
def read_config():
    f = open('config.txt', 'r')
    data = f.read()
    return data

# Security Issue: SQL Injection vulnerability
def get_user(username):
    query = "SELECT * FROM users WHERE username = '%s'" % username
    # execute query...
    return query

# Performance Issue: Inefficient loop
def process_items(data):
    result = []
    for i in range(len(data)):
        if data[i] % 2 == 0:
            result.append(data[i])
    return result

# Code Smell: Comparison with True/False
def check_status(is_active):
    if is_active == True:
        return "Active"
    elif is_active == False:
        return "Inactive"

# Security Issue: Use of eval
def calculate(expression):
    return eval(expression)

# Bug: Using 'is' for value comparison
def compare_values(a, b):
    if a is 10:
        return True
    return False

# Complexity Issue: High cyclomatic complexity
def complex_function(a, b, c, d, e):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e
                    else:
                        return a + b + c + d
                else:
                    return a + b + c
            else:
                return a + b
        else:
            return a
    else:
        return 0

# Code Smell: Bare except
def risky_operation():
    try:
        # Some operation
        x = 1 / 0
    except:
        pass

# Performance: Using append instead of list comprehension
def square_numbers(numbers):
    result = []
    for num in numbers:
        result.append(num ** 2)
    return result

# Missing docstrings
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price']
    return total

class DataProcessor:
    def __init__(self):
        self.data = []
    
    # No docstring
    def process(self, item):
        self.data.append(item)

# Security: Insecure random for tokens
def generate_token():
    return ''.join(random.choices('0123456789abcdef', k=32))

# Bug: Not validating user input
def get_user_input():
    value = input("Enter value: ")
    return int(value)  # Could crash if not a number

# Wildcard import (if uncommented)
# from os import *

if __name__ == "__main__":
    # Test the buggy code
    print(append_to_list(1))
    print(append_to_list(2))  # Will show [1, 2] due to mutable default
    
    print(build_string([1, 2, 3, 4, 5]))
    
    items = [1, 2, 3, 4, 5]
    print(square_numbers(items))