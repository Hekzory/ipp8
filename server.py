import grpc
from concurrent import futures
import users_pb2
import users_pb2_grpc
import time

# Simple in-memory user database
USERS = {
    "admin": {
        "id": 1,
        "password": "admin123",
        "full_name": "Administrator",
        "email": "admin@example.com",
    },
    "user": {
        "id": 2,
        "password": "user123",
        "full_name": "Regular User",
        "email": "user@example.com",
    },
}


class UserService(users_pb2_grpc.UserServiceServicer):
    def Login(self, request, context):
        username = request.username
        password = request.password

        if username in USERS and USERS[username]["password"] == password:
            user = users_pb2.User(
                id=USERS[username]["id"],
                username=username,
                full_name=USERS[username]["full_name"],
                email=USERS[username]["email"],
            )
            return users_pb2.LoginResponse(success=True, user=user)

        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        context.set_details("Invalid credentials")
        return users_pb2.LoginResponse(success=False)

    def UpdateUser(self, request, context):
        user_id = request.id
        user = next((u for u in USERS.values() if u["id"] == user_id), None)

        if user:
            username = next(k for k, v in USERS.items() if v["id"] == user_id)
            USERS[username]["full_name"] = request.full_name
            USERS[username]["email"] = request.email

            return users_pb2.User(
                id=user_id,
                username=username,
                full_name=request.full_name,
                email=request.email,
            )

        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("User not found")
        return users_pb2.User()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    users_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Server started on port 50051")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve()
