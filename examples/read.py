from bloomfilter.base import BaseModel


class UserReadModel(BaseModel):
    PREFIX = "bf:user_read"
    BF_SIZE = 1_000_000


if __name__ == "__main__":
    users = UserReadModel(redis={"host": "127.0.0.1", "port": 6379, "db": 0})
    users.add("alice")
    print(users.contains("alice"))
