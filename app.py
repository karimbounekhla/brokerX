import os
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from cs50 import SQL
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter for USD
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLite database
db = SQL("sqlite:///finance.db")

# Index page
@app.route("/")
@login_required
def index():
    # Display stocks owned by user
    stocks = db.execute("SELECT symbol, name, shares FROM users JOIN inventory WHERE users.id=inventory.id AND users.id=:id", id=session['user_id'])
    cash = db.execute("SELECT cash FROM users WHERE id=:id", id=session['user_id'])
    sum = 0
    for i in stocks:
        temp = lookup(i['symbol'])
        price = temp['price']
        i.update({'price':price})
        sum = sum + i['shares']*price
    return render_template("index.html", entry=stocks, cash=cash, sum=sum)

# Buy stock page
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        if not request.form.get("symbol") or not request.form.get("shares"):
            return apology("Must input symbol and number of shares")
        elif not lookup(request.form.get("symbol")):
            return apology("Invalid Symbol")
        elif not request.form.get("shares").isdigit() or int(request.form.get("shares")) < 1:
            return apology("Please enter valid number of shares")

        amt = int(request.form.get("shares"))
        stock = lookup(request.form.get("symbol"))
        latest = stock['price']
        compname = stock['name']

        cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session['user_id'])

        if amt * latest > int(cash[0]['cash']):
            return apology("You do not have enough cash")

        buy = db.execute("INSERT INTO transactions ('id', 'symbol', 'shares', 'price', 'debit') VALUES (:id, :symbol, :shares, :price, 'Debit')", id=session['user_id'], symbol=request.form.get("symbol"), shares=amt, price=latest)

        inv = db.execute("SELECT symbol FROM inventory WHERE id = :id AND symbol=:symbol", id=session['user_id'], symbol=request.form.get("symbol"))
        if not inv:
            inv = db.execute("INSERT INTO inventory ('id', 'symbol', 'name', 'shares') VALUES (:id, :symbol, :name, :shares)", id=session['user_id'], symbol=request.form.get("symbol"), name=compname, shares=amt)
        else:
            inv = db.execute("UPDATE inventory SET shares = shares + :amt WHERE id=:id AND symbol=:symbol", id=session['user_id'], amt=amt, symbol=request.form.get("symbol"))

        moneyleft = int(cash[0]['cash']) - (amt * latest)

        update = db.execute("UPDATE users SET cash = :moneyleft WHERE id = :id", moneyleft=moneyleft, id=session['user_id'])

        return redirect(url_for('index'))

    else:
        return render_template("buy.html")

# Adding cash
@app.route("/cash", methods=["GET", "POST"])
@login_required
def cash():

    if request.method == "POST":
        amt = int(request.form.get('dollars'))
        if amt < 0:
            return apology("Enter a positive integer")

        added_cash = db.execute("UPDATE users SET cash = cash + :cash WHERE id=:id", cash=amt, id=session['user_id'])
        added_trans = db.execute("INSERT INTO transactions ('id', 'symbol', 'shares', 'price', 'debit') VALUES (:id, 'CASH', 1, :cash, 'Credit')", id=session['user_id'], cash=amt)

        return redirect(url_for('index'))

    else:
        return render_template('cash.html')


# Checking if user exists
@app.route("/check", methods=["GET"])
def check():
    q = request.args.get("username")
    exist = db.execute("SELECT username FROM users WHERE username=:username", username=q)

    if len(q) > 1 and len(exist) == 0:
        return jsonify(True)
    else:
        return jsonify(False)


# Display transaction history
@app.route("/history")
@login_required
def history():
    output = db.execute("SELECT symbol, shares, price, date, debit FROM transactions WHERE id=:id", id=session['user_id'])
    return render_template("history.html", output=output)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# Use lookup() helper function to query stock using API
@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Please input a symbol")

        stock = lookup(request.form.get("symbol"))
        if not stock:
            return apology("Symbol does not exist")

        return render_template("quoted.html", name=request.form.get("symbol"), price=stock["price"])

    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register User."""

    if request.method == "POST":

        name = request.form.get("username").lower()

        exist = db.execute("SELECT username FROM users WHERE username = :username", username = name)

        if not request.form.get("username"):
            return apology("Username not entered")
        elif not request.form.get("password") or request.form.get("password") != request.form.get("confirmation"):
            return apology("Password not entered / not matching")
        elif len(exist) == 1:
            return apology("Username already exists")

        register = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                        username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))

        return redirect(url_for('index'))

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
        if not request.form.get("symbol") or not request.form.get("shares"):
            return apology("Specify symbol and shares")

        inv = db.execute("SELECT shares FROM inventory WHERE id=:id AND symbol=:symbol", id=session['user_id'], symbol=request.form.get("symbol"))

        amt = int(request.form.get("shares"))
        stock = lookup(request.form.get("symbol"))
        latest = stock['price']
        monies = int(amt*latest)
        in_inv = int(inv[0]['shares'])

        if amt > in_inv:
            return apology("You don't have enough shares")

        trans = db.execute("INSERT INTO transactions ('id', 'symbol', 'shares', 'price', 'debit') VALUES (:id, :symbol, :shares, :price, 'Credit')", id=session['user_id'], symbol=request.form.get("symbol"), shares=amt, price=latest)

        inv = db.execute("UPDATE inventory SET shares = shares - :amt WHERE id=:id AND symbol=:symbol", amt=amt, id=session['user_id'], symbol=request.form.get("symbol"))
        inv = db.execute("UPDATE users SET cash = cash + :cash", cash=monies)

        drop = db.execute("SELECT shares FROM inventory WHERE id=:id AND symbol=:symbol", id=session['user_id'], symbol=request.form.get("symbol"))
        in_inv = int(drop[0]['shares'])

        if in_inv == 0:
            drop = db.execute("DELETE FROM inventory WHERE id=:id AND symbol=:symbol", id=session['user_id'], symbol=request.form.get("symbol"))

        return redirect(url_for('index'))
    else:
        owned = db.execute("SELECT symbol FROM inventory WHERE id=:id", id=session['user_id'])
        return render_template("sell.html", symbol=owned)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
