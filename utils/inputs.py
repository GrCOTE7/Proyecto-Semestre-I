from enum import Enum

def enum_input(prompt: str, enum_type: Enum) -> Enum:
    """
    Utility function to get user input and convert it to an enum value.

    Parameters:
        - prompt: The message to display to the user.
        - enum_type: The Enum class to convert the input into.
    """
    while True:
        user_input = input(prompt).lower()
        try:
            return enum_type(user_input)
        except ValueError:
            print("Invalid input. Please enter a valid choice.")
