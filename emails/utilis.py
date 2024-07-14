def generate_error(index, email, error_detail):
        """
        Generate a detailed error dictionary for the given contact.
        """
        return {
            'index': index,
            'email': email,
            'errors': error_detail
        }