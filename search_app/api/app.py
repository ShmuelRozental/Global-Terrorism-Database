from flask import Flask, jsonify, request
from datetime import datetime
from elasticsearch import Elasticsearch

app = Flask(__name__)

es = Elasticsearch(hosts=["http://localhost:9200"])


@app.route('/search/keywords', methods=['GET'])
def search_by_keywords():
    keywords = request.args.get('keywords', '')
    limit = request.args.get('limit', 10, type=int)
    
    query = {
        "query": {
            "multi_match": {
                "query": keywords,
                "fields": ["summary", "location.country", "target_type.target_type_name"]
            }
        },
        "size": limit
    }
    response = es.search(index="historic_events", body=query)
    results = [hit["_source"] for hit in response["hits"]["hits"]]
    return jsonify(results)


@app.route('/search/historic', methods=['GET'])
def search_historic_endpoint():
    limit = request.args.get('limit', 10, type=int)
    
    query = {
        "query": {"match_all": {}},
        "size": limit
    }
    response = es.search(index="historic_events", body=query)
    results = [hit["_source"] for hit in response["hits"]["hits"]]
    return jsonify(results)


@app.route('/search/combined', methods=['GET'])
def search_combined_endpoint():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    limit = request.args.get('limit', 10, type=int)

    query = {
        "query": {
            "bool": {
                "must": [],
                "filter": []
            }
        },
        "size": limit
    }

    if start_date and end_date:
        query["query"]["bool"]["filter"].append({
            "range": {
                "date": {
                    "gte": start_date,
                    "lte": end_date,
                    "format": "yyyy-MM-dd"
                }
            }
        })

    response = es.search(index="historic_events", body=query)
    results = [hit["_source"] for hit in response["hits"]["hits"]]
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
