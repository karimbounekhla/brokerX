# BrokerX
Simple Stock Trading Game in Python/Flask, using SQL for the DB and HTML/CSS (Bootstrap) for the layout. 
Featuring user registration/login and real time stock price query using API.

## Tools 

* Python 3.7.3 - The Back-End
* [Flask](http://flask.palletsprojects.com/en/1.1.x/) - The Web Framework used
* [Jinja](https://www.palletsprojects.com/p/jinja/) - Template Engine
* [SQLite](https://www.sqlite.org/index.html) - Database Engine
* [BootStrap](https://getbootstrap.com/) - Front-End component (Menu)

## Screenshots

![Register](https://github.com/karimbounekhla/brokerX/blob/master/screenshots/1register.png)
![Buy](https://github.com/karimbounekhla/brokerX/blob/master/screenshots/6buy.png)
![Main](https://github.com/karimbounekhla/brokerX/blob/master/screenshots/9main.png)
![Sell](https://github.com/karimbounekhla/brokerX/blob/master/screenshots/8sell.png)
![History](https://github.com/karimbounekhla/brokerX/blob/master/screenshots/7history.png)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites

You will need Python 3.x and the following libraries and packages. Type commands in terminal to install:

`pip install flask`

`pip install flask_session`

`pip install sqlite3`

`pip install cs50`

In addition, you will need a Vantage AUTH Key to access real-time stock data and use this application. 
Request a Key by signing up on [Alpha Vantage](https://www.alphavantage.co/)

### Installing

A step by step series of examples that tell you how to get a development env running

Download all files into a folder. Ensure that all imported libraries in `app.py` and `helpers.py` are 
installed on your machine or virtual environment.

Edit `helpers.py` by replacing 'AUTH_KEY' in the `lookup()` function with your personal AUTH Key (See prerequisites)

```
url = f"https://www.alphavantage.co/query?apikey=AUTH_KEY&datatype=csv&function" \
              f"=TIME_SERIES_INTRADAY&interval=1min&symbol={symbol} "
```

Run the program on your machine or virtual environment.

```
flask run
```

## Task List

- [ ] Leaderboard showing all players and their stock performance
- [ ] Realized gains/losses, and addition to volume-dependent service fee per transaction
- [ ] 'Forgot Password'
- [ ] Graphical representation of performance vs major stock indices (S&P 500, DOW, etc.)

## License / Copyright

* This project is licensed under the MIT License.
* Harvard CS50 
