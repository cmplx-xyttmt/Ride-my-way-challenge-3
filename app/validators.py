import re


class Validate:
    """This class contains code for validating user input"""

    @staticmethod
    def validate_username(username):
        """Just checks if the username is at least 5 characters"""
        if len(username) < 5:
            return [False,
                    "Username should be at least 5 characters"]
        return [True]

    @staticmethod
    def validate_password(password):
        """Checks if password is at least characters"""
        if len(password) < 5:
            return [False,
                    'Password should be at least 5 characters']

        return [True]

    @staticmethod
    def validate_email(email):
        """Checks if email is in correct format"""
        regex = "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if re.match(regex, email, re.IGNORECASE):
            return [True]
        else:
            return [False, 'Email in wrong format']

    @staticmethod
    def validate_int(value):
        """Makes sure the value supplied is an integer"""
        try:
            int(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_date(date):
        """Checks if date is in correct format"""
        pass
