import unittest
from unittest.mock import Mock
import math
import sys

from fastcfg import Config
from fastcfg.config.value_wrapper import ValueWrapper


class TestValueWrapper(unittest.TestCase):
    """
    Comprehensive test cases for the ValueWrapper class.
    
    This class tests all magic methods and functionality of ValueWrapper,
    ensuring that wrapped values behave exactly like their underlying values
    while still providing access to AbstractConfigItem methods.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = Config()
        
    def test_factory_method(self):
        """Test the factory method for creating ValueWrapper instances."""
        # Create a config item
        self.config.test_value = 42
        
        # Get the wrapped value
        wrapped = self.config.test_value
        
        # Verify it's a ValueWrapper
        self.assertIsInstance(wrapped, ValueWrapper)
        self.assertEqual(wrapped._item.value, 42)

    def test_unwrap_static_method(self):
        """Test the unwrap static method."""
        # Test unwrapping various types
        self.config.int_val = 42
        self.config.str_val = "hello"
        self.config.list_val = [1, 2, 3]
        self.config.dict_val = {"a": 1, "b": 2}
        
        # Test unwrapping ValueWrapper
        self.assertEqual(ValueWrapper.unwrap(self.config.int_val), 42)
        self.assertEqual(ValueWrapper.unwrap(self.config.str_val), "hello")
        self.assertEqual(ValueWrapper.unwrap(self.config.list_val), [1, 2, 3])
        self.assertEqual(ValueWrapper.unwrap(self.config.dict_val), {"a": 1, "b": 2})
        
        # Test unwrapping nested structures
        self.config.nested = {"inner": [{"deep": 100}]}
        unwrapped = ValueWrapper.unwrap(self.config.nested)
        self.assertEqual(unwrapped, {"inner": [{"deep": 100}]})
        
        # Test unwrapping non-wrapped values
        self.assertEqual(ValueWrapper.unwrap(42), 42)
        self.assertEqual(ValueWrapper.unwrap("hello"), "hello")

    def test_class_property(self):
        """Test that __class__ property returns the underlying value's class."""
        self.config.int_val = 42
        self.config.str_val = "hello"
        self.config.float_val = 3.14
        self.config.list_val = [1, 2, 3]
        
        self.assertIs(self.config.int_val.__class__, int)
        self.assertIs(self.config.str_val.__class__, str)
        self.assertIs(self.config.float_val.__class__, float)
        self.assertIs(self.config.list_val.__class__, list)

    def test_comparison_operators(self):
        """Test all comparison operators."""
        self.config.a = 5
        self.config.b = 10
        
        # Less than
        self.assertTrue(self.config.a < self.config.b)
        self.assertTrue(self.config.a < 10)
        self.assertTrue(3 < self.config.a)
        
        # Less than or equal
        self.assertTrue(self.config.a <= self.config.b)
        self.assertTrue(self.config.a <= 5)
        self.assertTrue(5 <= self.config.a)
        
        # Greater than
        self.assertTrue(self.config.b > self.config.a)
        self.assertTrue(self.config.b > 3)
        self.assertTrue(15 > self.config.b)
        
        # Greater than or equal
        self.assertTrue(self.config.b >= self.config.a)
        self.assertTrue(self.config.b >= 10)
        self.assertTrue(10 >= self.config.b)
        
        # Equal
        self.assertTrue(self.config.a == 5)
        self.assertTrue(5 == self.config.a)
        self.assertFalse(self.config.a == self.config.b)
        
        # Not equal
        self.assertTrue(self.config.a != self.config.b)
        self.assertTrue(self.config.a != 10)
        self.assertTrue(10 != self.config.a)

    def test_arithmetic_operators(self):
        """Test all arithmetic operators."""
        self.config.a = 10
        self.config.b = 3
        
        # Addition
        self.assertEqual(self.config.a + self.config.b, 13)
        self.assertEqual(self.config.a + 5, 15)
        self.assertEqual(5 + self.config.a, 15)
        
        # Subtraction
        self.assertEqual(self.config.a - self.config.b, 7)
        self.assertEqual(self.config.a - 2, 8)
        self.assertEqual(20 - self.config.a, 10)
        
        # Multiplication
        self.assertEqual(self.config.a * self.config.b, 30)
        self.assertEqual(self.config.a * 4, 40)
        self.assertEqual(4 * self.config.a, 40)
        
        # True division
        self.assertEqual(self.config.a / self.config.b, 10/3)
        self.assertEqual(self.config.a / 2, 5.0)
        self.assertEqual(30 / self.config.a, 3.0)
        
        # Floor division
        self.assertEqual(self.config.a // self.config.b, 3)
        self.assertEqual(self.config.a // 3, 3)
        self.assertEqual(30 // self.config.a, 3)
        
        # Modulo
        self.assertEqual(self.config.a % self.config.b, 1)
        self.assertEqual(self.config.a % 3, 1)
        self.assertEqual(13 % self.config.a, 3)
        
        # Power
        self.assertEqual(self.config.a ** self.config.b, 1000)
        self.assertEqual(self.config.a ** 2, 100)
        self.assertEqual(2 ** self.config.a, 1024)

    def test_unary_operators(self):
        """Test unary operators."""
        self.config.positive = 42
        self.config.negative = -42
        self.config.float_val = -3.14
        
        # Negation
        self.assertEqual(-self.config.positive, -42)
        self.assertEqual(-self.config.negative, 42)
        self.assertEqual(-self.config.float_val, 3.14)
        
        # Positive
        self.assertEqual(+self.config.positive, 42)
        self.assertEqual(+self.config.negative, -42)
        self.assertEqual(+self.config.float_val, -3.14)
        
        # Absolute value
        self.assertEqual(abs(self.config.positive), 42)
        self.assertEqual(abs(self.config.negative), 42)
        self.assertEqual(abs(self.config.float_val), 3.14)

    def test_bitwise_operators(self):
        """Test bitwise operators."""
        self.config.a = 5  # 101 in binary
        self.config.b = 3  # 011 in binary
        
        # Bitwise AND
        self.assertEqual(self.config.a & self.config.b, 1)  # 101 & 011 = 001
        self.assertEqual(self.config.a & 2, 0)  # 101 & 010 = 000
        self.assertEqual(7 & self.config.a, 5)  # 111 & 101 = 101
        
        # Bitwise OR
        self.assertEqual(self.config.a | self.config.b, 7)  # 101 | 011 = 111
        self.assertEqual(self.config.a | 2, 7)  # 101 | 010 = 111
        self.assertEqual(2 | self.config.a, 7)  # 010 | 101 = 111
        
        # Bitwise XOR
        self.assertEqual(self.config.a ^ self.config.b, 6)  # 101 ^ 011 = 110
        self.assertEqual(self.config.a ^ 2, 7)  # 101 ^ 010 = 111
        self.assertEqual(2 ^ self.config.a, 7)  # 010 ^ 101 = 111
        
        # Left shift
        self.assertEqual(self.config.a << self.config.b, 40)  # 5 << 3 = 40
        self.assertEqual(self.config.a << 2, 20)  # 5 << 2 = 20
        self.assertEqual(2 << self.config.a, 64)  # 2 << 5 = 64
        
        # Right shift
        self.assertEqual(self.config.a >> self.config.b, 0)  # 5 >> 3 = 0
        self.assertEqual(self.config.a >> 1, 2)  # 5 >> 1 = 2
        self.assertEqual(20 >> self.config.a, 0)  # 20 >> 5 = 0
        
        # Bitwise NOT
        self.assertEqual(~self.config.a, -6)  # ~5 = -6

    def test_container_operations(self):
        """Test container operations."""
        self.config.list_val = [1, 2, 3, 4, 5]
        self.config.dict_val = {"a": 1, "b": 2, "c": 3}
        self.config.str_val = "hello"
        
        # Length
        self.assertEqual(len(self.config.list_val), 5)
        self.assertEqual(len(self.config.dict_val), 3)
        self.assertEqual(len(self.config.str_val), 5)
        
        # Get item
        self.assertEqual(self.config.list_val[0], 1)
        self.assertEqual(self.config.list_val[-1], 5)
        self.assertEqual(self.config.dict_val["a"], 1)
        self.assertEqual(self.config.str_val[1], "e")
        
        # Set item
        self.config.list_val[0] = 100
        self.assertEqual(self.config.list_val[0], 100)
        
        self.config.dict_val["d"] = 4
        self.assertEqual(self.config.dict_val["d"], 4)
        
        # Delete item
        del self.config.list_val[0]
        self.assertEqual(len(self.config.list_val), 4)
        self.assertEqual(self.config.list_val[0], 2)
        
        del self.config.dict_val["a"]
        self.assertNotIn("a", self.config.dict_val)
        
        # Contains
        self.assertIn(3, self.config.list_val)
        self.assertNotIn(100, self.config.list_val)
        self.assertIn("b", self.config.dict_val)
        self.assertNotIn("x", self.config.dict_val)
        self.assertIn("e", self.config.str_val)
        self.assertNotIn("z", self.config.str_val)
        
        # Iteration
        list_items = list(self.config.list_val)
        self.assertEqual(list_items, [2, 3, 4, 5])
        
        dict_items = list(self.config.dict_val)
        self.assertEqual(set(dict_items), {"b", "c", "d"})
        
        str_chars = list(self.config.str_val)
        self.assertEqual(str_chars, ["h", "e", "l", "l", "o"])
        
        # Reversed
        reversed_list = list(reversed(self.config.list_val))
        self.assertEqual(reversed_list, [5, 4, 3, 2])

    def test_string_representations(self):
        """Test string representation methods."""
        self.config.int_val = 42
        self.config.str_val = "hello"
        self.config.float_val = 3.14
        self.config.list_val = [1, 2, 3]
        
        # String representation
        self.assertEqual(str(self.config.int_val), "42")
        self.assertEqual(str(self.config.str_val), "hello")
        self.assertEqual(str(self.config.float_val), "3.14")
        self.assertEqual(str(self.config.list_val), "[1, 2, 3]")
        
        # Repr representation
        self.assertEqual(repr(self.config.int_val), "42")
        self.assertEqual(repr(self.config.str_val), "'hello'")
        self.assertEqual(repr(self.config.float_val), "3.14")
        self.assertEqual(repr(self.config.list_val), "[1, 2, 3]")
        
        # Format
        self.assertEqual(format(self.config.int_val, "05d"), "00042")
        self.assertEqual(format(self.config.float_val, ".1f"), "3.1")
        
        # Bytes (for strings) - use encode method instead of bytes constructor
        self.assertEqual(self.config.str_val.encode('utf-8'), b"hello")

    def test_type_conversions(self):
        """Test type conversion methods."""
        self.config.int_val = 42
        self.config.float_val = 3.14
        self.config.str_val = "123"
        self.config.bool_val = True
        self.config.complex_val = 3 + 4j
        
        # Integer conversion
        self.assertEqual(int(self.config.float_val), 3)
        self.assertEqual(int(self.config.str_val), 123)
        
        # Float conversion
        self.assertEqual(float(self.config.int_val), 42.0)
        self.assertEqual(float(self.config.str_val), 123.0)
        
        # Complex conversion
        self.assertEqual(complex(self.config.int_val), 42+0j)
        self.assertEqual(complex(self.config.float_val), 3.14+0j)
        
        # Boolean conversion
        self.assertTrue(bool(self.config.int_val))
        self.assertTrue(bool(self.config.str_val))
        
        # Index conversion
        self.assertEqual(self.config.int_val.__index__(), 42)
        
        # Round
        self.assertEqual(round(self.config.float_val), 3)
        self.assertEqual(round(self.config.float_val, 1), 3.1)
        
        # Truncate
        self.assertEqual(math.trunc(self.config.float_val), 3)
        
        # Floor
        self.assertEqual(math.floor(self.config.float_val), 3)
        
        # Ceiling
        self.assertEqual(math.ceil(self.config.float_val), 4)

    def test_hash_support(self):
        """Test hash support."""
        self.config.int_val = 42
        self.config.str_val = "hello"
        self.config.tuple_val = (1, 2, 3)
        
        # Hash should work for immutable types
        self.assertEqual(hash(self.config.int_val), hash(42))
        self.assertEqual(hash(self.config.str_val), hash("hello"))
        self.assertEqual(hash(self.config.tuple_val), hash((1, 2, 3)))
        
        # Hash should work in sets and as dict keys
        test_set = {self.config.int_val, self.config.str_val}
        self.assertIn(42, test_set)
        self.assertIn("hello", test_set)
        
        test_dict = {self.config.int_val: "value1", self.config.str_val: "value2"}
        self.assertEqual(test_dict[42], "value1")
        self.assertEqual(test_dict["hello"], "value2")

    def test_attribute_access(self):
        """Test attribute access delegation."""
        self.config.str_val = "hello"
        self.config.list_val = [1, 2, 3]
        self.config.dict_val = {"nested": {"deep": 100}}
        self.config.int_val = 42  # Define int_val for the test
        
        # Test string methods
        self.assertEqual(self.config.str_val.upper(), "HELLO")
        self.assertEqual(self.config.str_val.capitalize(), "Hello")
        self.assertEqual(len(self.config.str_val), 5)
        
        # Test list methods
        self.assertEqual(self.config.list_val.count(2), 1)
        self.assertEqual(self.config.list_val.index(2), 1)
        
        # Test dict access
        self.assertEqual(self.config.dict_val["nested"]["deep"], 100)
        
        # Test AbstractConfigItem methods (should be accessible)
        self.assertIsNotNone(self.config.int_val.add_validator)
        self.assertIsNotNone(self.config.int_val.validate)

    def test_wrapper_interaction(self):
        """Test interaction between multiple ValueWrapper instances."""
        self.config.a = 10
        self.config.b = 5
        self.config.c = 2
        
        # Test operations between wrapped values
        result = self.config.a + self.config.b * self.config.c
        self.assertEqual(result, 20)  # 10 + (5 * 2) = 20
        
        # Test comparison between wrapped values
        self.assertTrue(self.config.a > self.config.b)
        self.assertTrue(self.config.b < self.config.a)
        self.assertTrue(self.config.a >= self.config.b)
        self.assertTrue(self.config.b <= self.config.a)
        
        # Test mixed operations with regular values
        result = self.config.a + 5
        self.assertEqual(result, 15)
        
        result = 5 + self.config.a
        self.assertEqual(result, 15)

    def test_error_handling(self):
        """Test error handling for invalid operations."""
        self.config.str_val = "hello"
        self.config.int_val = 42
        
        # Test that string multiplication with int works
        self.assertEqual(self.config.str_val * 3, "hellohellohello")
        
        # Test invalid attribute access
        with self.assertRaises(AttributeError):
            _ = self.config.int_val.nonexistent_method()

    def test_mutable_operations(self):
        """Test operations on mutable objects."""
        self.config.list_val = [1, 2, 3]
        self.config.dict_val = {"a": 1, "b": 2}
        
        # Test list operations
        self.config.list_val.append(4)
        self.assertEqual(self.config.list_val, [1, 2, 3, 4])
        
        self.config.list_val.extend([5, 6])
        self.assertEqual(self.config.list_val, [1, 2, 3, 4, 5, 6])
        
        self.config.list_val.insert(0, 0)
        self.assertEqual(self.config.list_val, [0, 1, 2, 3, 4, 5, 6])
        
        # Test dict operations
        self.config.dict_val.update({"c": 3, "d": 4})
        self.assertEqual(self.config.dict_val, {"a": 1, "b": 2, "c": 3, "d": 4})
        
        # Test that changes persist
        self.assertEqual(self.config.list_val[0], 0)
        self.assertEqual(self.config.dict_val["c"], 3)

    def test_float_specific_operations(self):
        """Test float-specific operations."""
        self.config.float_val = 3.14159
        
        # Test float methods
        self.assertEqual(self.config.float_val.is_integer(), False)
        self.assertEqual(self.config.float_val.hex(), "0x1.921f9f01b866ep+1")
        
        # Test with integer float
        self.config.int_float = 42.0
        self.assertEqual(self.config.int_float.is_integer(), True)

    def test_string_specific_operations(self):
        """Test string-specific operations."""
        self.config.str_val = "Hello World"
        
        # Test string methods
        self.assertEqual(self.config.str_val.lower(), "hello world")
        self.assertEqual(self.config.str_val.upper(), "HELLO WORLD")
        self.assertEqual(self.config.str_val.split(), ["Hello", "World"])
        self.assertEqual(self.config.str_val.replace("World", "Python"), "Hello Python")
        self.assertEqual(self.config.str_val.startswith("Hello"), True)
        self.assertEqual(self.config.str_val.endswith("World"), True)

    def test_list_specific_operations(self):
        """Test list-specific operations."""
        self.config.list_val = [3, 1, 4, 1, 5]
        
        # Test list methods
        self.config.list_val.sort()
        self.assertEqual(self.config.list_val, [1, 1, 3, 4, 5])
        
        self.config.list_val.reverse()
        self.assertEqual(self.config.list_val, [5, 4, 3, 1, 1])
        
        self.assertEqual(self.config.list_val.count(1), 2)
        self.assertEqual(self.config.list_val.index(3), 2)

    def test_dict_specific_operations(self):
        """Test dict-specific operations."""
        self.config.dict_val = {"a": 1, "b": 2, "c": 3}
        
        # Test dict methods
        self.assertEqual(list(self.config.dict_val.keys()), ["a", "b", "c"])
        self.assertEqual(list(self.config.dict_val.values()), [1, 2, 3])
        self.assertEqual(list(self.config.dict_val.items()), [("a", 1), ("b", 2), ("c", 3)])
        
        # Test get method
        self.assertEqual(self.config.dict_val.get("a"), 1)
        self.assertEqual(self.config.dict_val.get("d", "default"), "default")
        
        # Test pop method
        value = self.config.dict_val.pop("a")
        self.assertEqual(value, 1)
        self.assertNotIn("a", self.config.dict_val)

    def test_complex_mathematical_operations(self):
        """Test complex mathematical operations."""
        self.config.a = 10
        self.config.b = 3
        self.config.c = 2.5
        
        # Test complex expressions
        result = (self.config.a ** self.config.b) / self.config.c
        expected = (10 ** 3) / 2.5
        self.assertEqual(result, expected)
        
        # Test with math functions
        import math
        result = math.sqrt(self.config.a ** 2 + self.config.b ** 2)
        expected = math.sqrt(10 ** 2 + 3 ** 2)
        self.assertEqual(result, expected)
        
        # Test trigonometric functions
        result = math.sin(self.config.c) + math.cos(self.config.c)
        expected = math.sin(2.5) + math.cos(2.5)
        self.assertEqual(result, expected)

    def test_boolean_operations(self):
        """Test boolean operations."""
        self.config.true_val = True
        self.config.false_val = False
        self.config.int_val = 42
        self.config.zero_val = 0
        
        # Test boolean operations
        self.assertTrue(self.config.true_val and self.config.int_val)
        self.assertFalse(self.config.false_val and self.config.int_val)
        self.assertTrue(self.config.false_val or self.config.int_val)
        self.assertFalse(self.config.false_val or self.config.zero_val)
        self.assertTrue(not self.config.false_val)
        self.assertFalse(not self.config.true_val)
        
        # Test boolean conversion
        self.assertTrue(bool(self.config.int_val))
        self.assertFalse(bool(self.config.zero_val))
        self.assertTrue(bool(self.config.true_val))
        self.assertFalse(bool(self.config.false_val))


if __name__ == '__main__':
    unittest.main() 