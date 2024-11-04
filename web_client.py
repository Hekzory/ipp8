from flask import Flask, render_template, request, redirect, url_for, flash, session
import grpc
import users_pb2
import users_pb2_grpc

app = Flask(__name__)
app.secret_key = "your-secret-key"


def get_grpc_stub():
    channel = grpc.insecure_channel("localhost:50051")
    return users_pb2_grpc.UserServiceStub(channel)


@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("profile"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        stub = get_grpc_stub()
        try:
            response = stub.Login(
                users_pb2.LoginRequest(username=username, password=password)
            )

            if response.success:
                session["user"] = {
                    "id": response.user.id,
                    "username": response.user.username,
                    "full_name": response.user.full_name,
                    "email": response.user.email,
                }
                return redirect(url_for("profile"))
            else:
                flash("Invalid credentials")
        except grpc.RpcError as e:
            flash("Error during login")

    return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        stub = get_grpc_stub()
        try:
            response = stub.UpdateUser(
                users_pb2.UpdateUserRequest(
                    id=session["user"]["id"],
                    full_name=request.form["full_name"],
                    email=request.form["email"],
                )
            )

            session["user"]["full_name"] = response.full_name
            session["user"]["email"] = response.email
            flash("Profile updated successfully")
        except grpc.RpcError as e:
            flash("Error updating profile")

    return render_template("profile.html", user=session["user"])


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
