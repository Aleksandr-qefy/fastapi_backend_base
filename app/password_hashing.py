import bcrypt


def hash_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return str(hashed_password, 'utf-8')


def verify_password(hashed_password, input_password):
    # Verify if the input password matches the hashed password
    return bcrypt.checkpw(input_password.encode('utf-8'), bytes(hashed_password, 'utf-8'))
