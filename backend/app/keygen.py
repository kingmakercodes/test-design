import os

jwt_secret_key= os.urandom(24)
print(jwt_secret_key.hex())


