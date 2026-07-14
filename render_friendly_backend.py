print("Starting to import modules")
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
import sqlite3
import spacy
import collections
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
print("Finished importing modules")

load_dotenv()


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins":"*"}})

nlp = fill_mask = model_similarity = model_roberta = tokenise_roberta = None

def load_all():
    global nlp, fill_mask, model_similarity, model_roberta, tokenise_roberta
    if nlp:
        return
    nlp = spacy.load("en_core_web_sm")
    print("spacy model loaded")

    model_roberta = AutoModelForSequenceClassification.from_pretrained("textattack/distilbert-base-uncased-CoLA")
    tokenise_roberta = AutoTokenizer.from_pretrained("textattack/distilbert-base-uncased-CoLA")

    ########### PREDICT WORD ###################
    fill_mask = pipeline("fill-mask", model="distilbert/distilbert-base-uncased")
    print("bert model loaded")

    ####### SIMILARITY MODEL ##################
    model_similarity = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')
    print("similarity model loaded")



def get_synonyms(word):
    word = word.lower()
    using_api_key = False
    words = []
    datamuse_resp = requests.get(f"https://api.datamuse.com/words?ml={word}").json()
    words = words + [word["word"] for word in datamuse_resp]
    words = [word for word in words if " " not in word]
    return(set(words))


# def noun_adj(word):
#     url = f"https://api.datamuse.com/words?rel_{type}={word}&max=25"
#     response = requests.get(url)
#     return([item['word'] for item in response.json()])


def predictions(sentence, word, fill_mask):
    #Returns a list of 25 words most likely to replace the current word. 
    masked_sentence = sentence + " " + sentence.replace(f"{word}", "[MASK]")
    print(masked_sentence)
    predictions = fill_mask(masked_sentence, top_k=25)
    words = [pred["token_str"] for pred in predictions]
    return(words)

#####  SIMILARITY OF SENTENCES #############
def get_similarity(sentence1, sentence2, model_similarity):
    #Returns the similarity between sentences
    embedding1 = model_similarity.encode([sentence1])
    embedding2 = model_similarity.encode([sentence2])
    return cosine_similarity(embedding1, embedding2)[0][0]


########### roberta CoLa Grammar #####################
def Perplex(text):
    #Returns the probability of correctness (1 means correct, 0 incorrect)
    tokenised_sent = tokenise_roberta(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model_roberta(**tokenised_sent).logits
    probs = F.softmax(logits, dim=1)
    return(float(probs[0][1]))

def match_count(words):
    '''
    Returns the number of times that word was found in the ngram DB
    '''
    conn = sqlite3.connect('cleandb.db')
    cursor = conn.cursor()
    results = {}
    for word in words:
        try:
            cursor.execute(f"SELECT match_count FROM ngram1_filtered WHERE word = ?", (word,))
        except:
            print(f"FAILED TO EXECUTE THE FOLLOWING \nSELECT match_count FROM ngram1_filtered WHERE word = '{word}'")
            input(f"Error with the following word : {word}")
        result = cursor.fetchall()
        if result == []:
            print(f"{word} was not found in the ngram1 database.")
            results[word] = 999
        else:
            results[word] = result[0][0]
    cursor.close()
    conn.close()
    return(results)

def text_weaknesses(text, nlp):
    ''' Returns : 
        occurences : dict the number of occurences of that word in the text provided 
        match_count : The number of times that word was used according to ngrams
        doc :  The text after being processed by spacy (collection of tokens)
    '''
    doc = nlp(text)
    occurences = collections.defaultdict(int)
    for token in doc:
        if token.pos_ in {"NOUN", "VERB", "ADJ", "ADV"}:
            word = token.lemma_
            occurences[word] += 1
    word_list = [key for key in occurences]
    match_count_text = match_count(word_list)
    return(occurences, match_count_text, doc)

def evaluate_options(sentence, word_to_replace, model_similarity, fill_mask):
    ### DICTIONARY STORING THE SCORE OF ALL SYNONYMS ACQUIRED BY THE API {synonyms: [in_predictions, similarity, Perplex]}}
    synonyms = get_synonyms(word_to_replace)
    dictionary = {}
    predicted_words = predictions(sentence, word_to_replace, fill_mask)
    words = synonyms.union(set(predicted_words))
    match_count_dict = match_count(words)
    print(words)
    for synonym in words:
        modified_sentence = sentence.replace(word_to_replace, synonym)
        similarity = get_similarity(sentence, modified_sentence, model_similarity)    
        perplexity = Perplex(modified_sentence)
        dictionary[synonym] = [1 if synonym in predicted_words else 0, similarity, perplexity, match_count_dict[synonym]]
    return(dictionary)



limiter = Limiter(get_remote_address, app=app)

@app.before_request
def authenticate():
    load_all()
    if request.method == 'OPTIONS':
        print("OPTIONS REQUEST SO NO AUTHENTIFICATIONS")
        return None  # Skip authentication for OPTIONS requests

    token = request.headers.get('Authorization')
    print(f"Request URL: {request.url}")
    print(f"Request Origin: {request.headers.get('Origin')}")
    print(f"Request Referer: {request.headers.get('Referer')}")
    if token != "JfslidfjskfnKfnsdfjlhJfKLFjsinNfskjflshNfsdjhfslfhsjJhfjslfhsldfHu*(#@HfHFSFKHUhfshof)":
        print(f"failed to authenticate, token given was {token}")
        return jsonify({"error": "Unauthorized"}), 401

@app.errorhandler(404)
@limiter.limit("5 per minute")
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.route('/api/graph', methods=['POST', "OPTIONS"])
@limiter.limit("5 per minute")
def text_graph():
    if request.method == 'OPTIONS':
        response = app.make_response('')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        response.headers['Access-Control-Allow-Credentials'] = 'true'  # Allow credentials (cookies, Authorization headers)
        response.status_code = 200
        return response
    print("Trying")
    data = request.json
    text = data.get("text")
    print(text)
    occurences, match_count_text, doc = text_weaknesses(text, nlp)
    print(occurences, match_count_text, doc)
    #SORT IT BETTER (WITH HIGH OCCURENCES AND HIGH MATCH COUNT first)
    sorted_occurences = sorted(occurences.items(), key=lambda item: (item[1]), reverse=True)
    dict = {"sorted_occurences":sorted_occurences, "match_count":match_count_text}
    return(jsonify(dict))


@app.route('/api/alternatives', methods=['POST', "OPTIONS"])
@limiter.limit("5 per minute")
def alternatives():
    if request.method == 'OPTIONS':
        response = app.make_response('')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        response.headers['Access-Control-Allow-Credentials'] = 'true'  # Allow credentials (cookies, Authorization headers)
        response.status_code = 200
        return response
    data = request.json
    word_to_replace = data.get("word")
    sentence = data.get("sentence")[0]
    print("Trying")
    print(f"processing {sentence}, with word = {word_to_replace}")
    candidate_words = evaluate_options(sentence, word_to_replace, model_similarity, fill_mask)
    notDone = True
    while notDone:
        notDone = False
        candidates_predicted = []
        candidates_non_predicted = []
        for key in candidate_words:
            if candidate_words[key][0]==1:
                candidates_predicted.append((key,candidate_words[key][0],candidate_words[key][1],candidate_words[key][2],candidate_words[key][3]))
            else:
                candidates_non_predicted.append((key,candidate_words[key][0],candidate_words[key][1],candidate_words[key][2],candidate_words[key][3]))


        candidates_predicted = sorted(candidates_predicted, key=lambda x: x[3])
        candidates_non_predicted = sorted(candidates_non_predicted, key=lambda x: x[3])
        sim_values = [candidate_words[x][1] for x in candidate_words]
        perp_values = [candidate_words[x][2] for x in candidate_words]
        match_values = [candidate_words[x][3] for x in candidate_words]

        average_similar = sum(sim_values)/len(sim_values)
        average_perp = sum(perp_values)/len(perp_values)
        average_match = sum(match_values)/len(match_values)

        sd_similar = np.std(sim_values)
        sd_perp = np.std(perp_values)
        sd_match = np.std(match_values)

        #print(f"avg:{average_perp}, sd:{sd_perp}")
        #print(f"avg:{average_similar}, sd:{sd_similar}")
        #print(f"avg:{average_match}, sd:{sd_match}")
        
        scaled_list_predicted = []
        scaled_list_non_predicted = []
        for item in candidates_predicted:
            if (item[2]-average_similar)/sd_similar>-3 and (item[3]-average_perp)/sd_perp>-3:
                scaled_list_predicted.append((item[0], item[1], (item[2]-average_similar)/sd_similar, (item[3]-average_perp)/sd_perp, (item[4]-average_match)/sd_match))
            else:
                del candidate_words[item[0]]
                notDone=True
                print(f"Deleted {item[0]}")
        for item2 in candidates_non_predicted:
            if (item2[2]-average_similar)/sd_similar>-3 and (item2[3]-average_perp)/sd_perp>-3:
                scaled_list_non_predicted.append((item2[0], item2[1], (item2[2]-average_similar)/sd_similar, (item2[3]-average_perp)/sd_perp, (item2[4]-average_match)/sd_match))
            else:
                del candidate_words[item2[0]]
                notDone=True
                print(f"Deleted {item2[0]}")
    response = {} 
    for word, pred, similar, gramm, match in scaled_list_predicted + scaled_list_predicted:
        response[word] = (float(similar), float(gramm), float(match))
    print(response)
    return jsonify(response)



if __name__ == '__main__':
    app.run(debug=False, port=int(os.getenv("PORT", 5000)), host=os.getenv("HOST"))