# Overview
This project is a web-based Flask application called Sarcasm Game that predicts sarcasm in user-submitted text messages. It integrates two machine learning models, logistic regression and Naive Bayes, to classify text as sarcastic or not. Players can submit their nickname and message to the game, where a sarcasm score is computed and stored in a MySQL database. A leaderboard shows the top players based on their sarcasm scores.

## Features:
- Machine Learning Prediction: Uses logistic regression and Naive Bayes models to predict sarcasm in the text.
- Leaderboard: Displays the top 10 players based on sarcasm score.
- Player Position: Provides each player with their ranking compared to others.
- Text Preprocessing: Includes stemming and stopword removal for both English and Indonesian languages.
- Caching: Utilizes caching for frequently used text transformations and predictions.

## Tech Stack:
- Backend: Flask, MySQL
- Frontend: HTML, CSS (via templates/index.html)
- Machine Learning: Logistic Regression, Naive Bayes
- Other: NLTK (for text preprocessing), Sastrawi (for Indonesian stemming)

## Prerequisites
- Ensure you have the following installed before running the project:
- Python 3.x
- MySQL
- Required Python libraries (listed in requirements.txt)

## Libraries & Tools:
- Flask: Web framework for Python.
- mysql-connector-python: MySQL database connection.
- nltk: Natural language processing library for English stemming and stopword removal.
- Sastrawi: For Indonesian stemming.
- joblib: For loading pre-trained machine learning models.

### Key Functions
- load_models(): Loads pre-trained models and vectorizers from disk.
- transform_text(text): Preprocesses the text (lowercasing, tokenizing, stemming, and removing stopwords in both English and Indonesian).
- predict_log_reg(): Generates predictions using the logistic regression model.
- predict_naive_bayes(): Generates predictions using the Naive Bayes model.
- add_character(): Stores the user's nickname, message, sarcasm result, and score in the database.
- check_leaderboard(): Retrieves the top 10 players from the database.
- get_player_position(): Fetches the player's rank and total number of players.

### Customization
- Database: Change database connection details in get_db_connection() function in app.py.
- Models: You can replace the sarcasm detection models with more advanced or different machine learning models, and the predictions will still work.
