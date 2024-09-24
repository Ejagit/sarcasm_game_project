import os
from flask import Flask, render_template, request
import mysql.connector
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from functools import lru_cache

app = Flask(__name__)

# Ensure required NLTK datasets are downloaded
nltk.download('punkt')
nltk.download('stopwords')

# Load models and vectorizers
def load_models():
    return {
        'log_reg': joblib.load("/home/sarcasmgame/flask/log_reg_sarcasm.joblib"),
        'tfidf_vectorizer': joblib.load("/home/sarcasmgame/flask/tfidf_vectorizer.joblib"),
        'nb': joblib.load("/home/sarcasmgame/flask/multinomial_nb_model.joblib"),
        'count_vectorizer': joblib.load("/home/sarcasmgame/flask/count_vectorizer.joblib")
    }

models = load_models()

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'YOUR_HOST_DB'),
        user=os.getenv('DB_USER', 'YOUR_USER_DB'),
        password=os.getenv('DB_PASSWORD', 'YOUR_PSW_DB'),
        database=os.getenv('DB_NAME', 'YOUR_DB_NAME')
    )

@lru_cache(maxsize=1000)
def transform_text(text):
    ps = PorterStemmer()
    factory = StemmerFactory()
    indo_stemmer = factory.create_stemmer()
    text = text.lower()
    text = nltk.word_tokenize(text)
    y = [i for i in text if i.isalnum()]
    y = [i for i in y if i not in stopwords.words('english') and i not in stopwords.words('indonesian') and i not in string.punctuation]
    return " ".join([min(ps.stem(i), indo_stemmer.stem(i)) for i in y])

# Prediction functions
def predict_log_reg(final_text):
    tfidf_text = models['tfidf_vectorizer'].transform([final_text]).toarray()
    return models['log_reg'].predict(tfidf_text)[0], round(models['log_reg'].predict_proba(tfidf_text)[0][1] * 100, 2)

def predict_naive_bayes(final_text):
    count_vectorized_text = models['count_vectorizer'].transform([final_text]).toarray()
    return models['nb'].predict(count_vectorized_text)[0], round(models['nb'].predict_proba(count_vectorized_text)[0][1] * 100, 2)

@lru_cache(maxsize=1000)
def add_character(nickname, message_text):
    final_text = transform_text(message_text)
    
    nb_prediction, nb_score = predict_naive_bayes(final_text)
    log_reg_prediction, log_reg_score = predict_log_reg(final_text)
    
    final_score = round((nb_score + log_reg_score) / 2, 2)
    final_prediction = 1 if final_score > 50 else 0
    
    sarcasm = 'True' if final_prediction == 1 else 'False'
    
    query = "INSERT INTO #YOUR_DB_NAME (nickname, message, sarcasm, score) VALUES (%s, %s, %s, %s);"
    values = (nickname, message_text, sarcasm, final_score)
    
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, values)
        conn.commit()
    except mysql.connector.Error as e:
        print(f"Error inserting data: {e}")
    finally:
        if conn.is_connected():
            conn.close()

def check_leaderboard():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM (#YOUR_DB_NAME))")
            return cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Error fetching leaderboard: {e}")
        return []
    finally:
        if conn.is_connected():
            conn.close()

def get_leaderboard(nickname):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM #YOUR_DB_NAME ORDER BY score DESC LIMIT 10")
            leaderboard_results = cursor.fetchall()
            
            player_in_top_10 = any(row[0] == nickname for row in leaderboard_results)
            
            if not player_in_top_10:
                cursor.execute("""
                    SELECT *
                    FROM #YOUR_DB_NAME
                    WHERE nickname = %s
                    ORDER BY score DESC
                    LIMIT 1
                """, (nickname,))
                player_info = cursor.fetchone()
            else:
                player_info = None
            
            return leaderboard_results, player_info
    except mysql.connector.Error as e:
        print(f"Error fetching leaderboard: {e}")
        return [], None
    finally:
        if conn.is_connected():
            conn.close()

def get_player_position(nickname):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) + 1 AS position
                FROM #YOUR_DB_NAME
                WHERE score > (
                    SELECT score
                    FROM #YOUR_DB_NAME
                    WHERE nickname = %s
                    ORDER BY score DESC
                    LIMIT 1
                );
            """, (nickname,))
            position = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM #YOUR_DB_NAME;")
            total_players = cursor.fetchone()[0]
            
            return position, total_players
    except mysql.connector.Error as e:
        print(f"Error getting player position: {e}")
        return None, None
    finally:
        if conn.is_connected():
            conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    player_position = None
    total_players = None
    nickname = None
    
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        message_text = request.form.get('message')
        if nickname and message_text:
            add_character(nickname, message_text)
            player_position, total_players = get_player_position(nickname)
    
    results = check_leaderboard()
    leaderboard_results, player_info = get_leaderboard(nickname)
    
    return render_template(
        'index.html',
        results=results,
        leaderboard_results=leaderboard_results,
        player_info=player_info,
        player_position=player_position,
        total_players=total_players
    )