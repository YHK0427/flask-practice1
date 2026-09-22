from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")



@app.route("/profile")
def profile():
    hobbies = ["숙면", "배구", "산책"]
    return render_template("profile.html", hobbies = hobbies)






if __name__ == "__main__":
    app.run(debug=True)
