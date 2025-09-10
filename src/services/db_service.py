class DBService:
    def __init__(self):
        # setup DB connection
        pass

    def save_user(self, username: str, password: str):
        print(f"User {username} saved to DB")

    def get_user(self, username: str):
        return {"username": username, "password": "hashedpassword"}
