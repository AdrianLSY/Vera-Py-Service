import json

# This will raise TypeError
complex_obj = {
    "function": lambda x: x*2,  # Functions aren't JSON serializable
    "complex": complex(1, 2),   # Complex numbers aren't JSON serializable
    "set": {1, 2, 3}            # Sets aren't JSON serializable
}

json.dumps(complex_obj)  #
