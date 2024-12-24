from flask import Flask, jsonify, request
from datetime import datetime
from search import search_keywords, search_news, search_historic, search_combined

app = Flask(__name__)


@app.route('/search/keywords', methods=['GET'])
def search_by_keywords():
    keywords = request.args.get('keywords', '')
    limit = request.args.get('limit', 10, type=int)
    results = search_keywords(keywords, limit)
    return jsonify(results)


@app.route('/search/news', methods=['GET'])
def search_news_endpoint():
    limit = request.args.get('limit', 10, type=int)
    results = search_news(limit)
    return jsonify(results)


@app.route('/search/historic', methods=['GET'])
def search_historic_endpoint():
    limit = request.args.get('limit', 10, type=int)
    results = search_historic(limit)
    return jsonify(results)


@app.route('/search/combined', methods=['GET'])
def search_combined_endpoint():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    limit = request.args.get('limit', 10, type=int)
    results = search_combined(start_date, end_date, limit)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
