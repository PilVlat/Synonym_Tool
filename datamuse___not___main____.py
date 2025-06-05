import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import pipeline
from transformers import GPT2LMHeadModel, GPT2Tokenizer, AutoModelForCausalLM, AutoTokenizer
import torch
import numpy as np
import sqlite3
import matplotlib.pyplot as plt

#MODEL FOR PERPLEXITY

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-0.5B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-0.5B")

########### PREDICT WORD ###################
fill_mask = pipeline("fill-mask", model="bert-base-uncased")

####### SIMILARITY MODEL ##################
model_similarity = SentenceTransformer('paraphrase-MiniLM-L12-v2')

def get_synonyms(word):
    word = word.lower()
    if word == "fear":
        words = ['anxiety', 'fearfulness', 'dread', 'panic', 'terror', 'fright', 'worry', 'horror', 'trepidation', 'scare', 'concern', 'dismay', 'alarm', 'phobia', 'nervousness', 'alarum', 'pang', 'apprehension', 'agitation', 'creeps', 'jitters', 'consternation', 'twinge', 'timidity', 'perturbation', 'cowardice', 'disquiet', 'qualm', 'funk', 'willies', 'discomposure', 'faintheartedness', 'timorousness', 'worry', 'fret', 'trouble', 'stress', 'sweat', 'bother', 'care a hang', 'stew', 'fuss', 'sweat blood', 'despair', 'give a hang', 'long', 'pine', 'agonize', 'yearn', 'chafe', 'anxiety', 'fearfulness', 'dread', 'panic', 'terror', 'fright', 'worry', 'horror', 'trepidation', 'scare', 'concern', 'dismay', 'alarm', 'phobia', 'nervousness', 'alarum', 'pang', 'apprehension', 'agitation', 'creeps', 'jitters', 'consternation', 'twinge', 'timidity', 'perturbation', 'cowardice', 'disquiet', 'qualm', 'funk', 'willies', 'discomposure', 'faintheartedness', 'timorousness', 'worry', 'fret', 'trouble', 'stress', 'sweat', 'bother', 'care a hang', 'stew', 'fuss', 'sweat blood', 'despair', 'give a hang', 'long', 'pine', 'agonize', 'yearn', 'chafe']
    elif word == "shone":
        words = ['glowed', 'glinted', 'gleamed', 'beamed', 'burnt', 'sparkled', 'radiated', 'flickered', 'flared', 'rayed', 'shimmered', 'glimmered', 'twinkled', 'blazed', 'glistened', 'illumined', 'glittered', 'lighted', 'burned', 'lit', 'illuminated', 'flashed', 'glared', 'brightened', 'beat (down)', 'blinked', 'lightened', 'sheened', 'flamed', 'blinded', 'winked', 'dazzled', 'fired', 'spangled', 'lustred', 'scintillated', 'luminesced', 'irradiated', 'glistered', 'winkled', 'lustered', 'coruscated', 'dazed', 'bedazzled', 'glowed', 'glinted', 'gleamed', 'beamed', 'burnt', 'sparkled', 'radiated', 'flickered', 'flared', 'rayed', 'shimmered', 'glimmered', 'twinkled', 'blazed', 'glistened', 'illumined', 'glittered', 'lighted', 'burned', 'lit', 'illuminated', 'flashed', 'glared', 'brightened', 'beat (down)', 'blinked', 'lightened', 'sheened', 'flamed', 'blinded', 'winked', 'dazzled', 'fired', 'spangled', 'lustred', 'scintillated', 'luminesced', 'irradiated', 'glistered', 'winkled', 'lustered', 'coruscated', 'dazed', 'bedazzled']
    elif word == "anticipation":
        words = ['expectation', 'expectancy', 'expectance', 'contemplation', 'prospect', 'dread', 'apprehension', 'alarm', 'foreboding', 'alarum', 'misgiving', 'expectation', 'expectancy', 'expectance', 'contemplation', 'prospect', 'dread', 'apprehension', 'alarm', 'foreboding', 'alarum', 'misgiving']
    else:
        headers = {
            "X-Api-Key":"17OFIFEu8jNMjQQgnXW1lg==FfkSwkqo1ypAXWta"
        }
        url = f"https://api.api-ninjas.com/v1/thesaurus?word={word}"
        input("USING AN API KEY")
        response = requests.get(url, headers=headers)
        words = response.json()["synonyms"]
    datamuse_resp = requests.get(f"https://api.datamuse.com/words?ml={word}").json()
    words = words + [word["word"] for word in datamuse_resp]
    return(set(words))


def noun_adj(word):
    url = f"https://api.datamuse.com/words?rel_{type}={word}&max=25"
    response = requests.get(url)
    return([item['word'] for item in response.json()])


def predictions(sentence, word, fill_mask):
    masked_sentence = sentence + " " + sentence.replace(f" {word} ", "[MASK]")
    predictions = fill_mask(masked_sentence, top_k=100)
    words = [pred["token_str"] for pred in predictions]
    return(words)



#####  SIMILARITY OF SENTENCES #############
def get_similarity(sentence1, sentence2, model_similarity):
    embedding1 = model_similarity.encode([sentence1])
    embedding2 = model_similarity.encode([sentence2])
    return cosine_similarity(embedding1, embedding2)[0][0]


########### GPT-2 PERPLEX #####################
def Perplex(text, model):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs, labels=inputs["input_ids"])
        loss = outputs.loss
        perplexity = torch.exp(loss)
    return(perplexity.item())

def match_count(words):
    conn = sqlite3.connect('cleandb.db')
    cursor = conn.cursor()
    results = {}
    for word in words:
        cursor.execute(f"SELECT match_count FROM ngram1_filtered WHERE word = '{word}'")
        result = cursor.fetchall()
        if result == []:
            print(f"{word} was not found in the ngram1 database.")
            results[word] = 999
        else:
            results[word] = result[0][0]
    cursor.close()
    conn.close()
    return(results)


def evaluate_options(sentence, word_to_replace, model_similarity, fill_mask, model):
    ### DICTIONARY STORING THE SCORE OF ALL SYNONYMS ACQUIRED BY THE API {synonyms: [in_predictions, similarity, Perplex]}}
    synonyms = get_synonyms(word_to_replace)
    dictionary = {}
    predicted_words = predictions(sentence, word_to_replace, fill_mask)
    match_count_dict = match_count(synonyms)
    print(predicted_words)
    for synonym in synonyms:
        modified_sentence = sentence.replace(word_to_replace, synonym)
        similarity = get_similarity(sentence, modified_sentence, model_similarity)    
        perplexity = Perplex(modified_sentence, model)
        dictionary[synonym] = [1 if synonym in predicted_words else 0, similarity, perplexity, match_count_dict[synonym]]
    return(dictionary)

sentence = "The fear I felt was overwhelming."
word_to_replace = "fear"
candidate_words = evaluate_options(sentence, word_to_replace, model_similarity, fill_mask, model)
print(candidate_words)
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
print(match_values)

average_similar = sum(sim_values)/len(sim_values)
average_perp = sum(perp_values)/len(perp_values)
average_match = sum(match_values)/len(match_values)

sd_similar = np.std(sim_values)
sd_perp = np.std(perp_values)
sd_match = np.std(match_values)

print(f"avg:{average_perp}, sd:{sd_perp}")
print(f"avg:{average_similar}, sd:{sd_similar}")
print(f"avg:{average_match}, sd:{sd_match}")

scaled_list_predicted = []
scaled_list_non_predicted = []
for item in candidates_predicted:
    scaled_list_predicted.append((item[0], item[1], (item[2]-average_similar)/sd_similar, (item[3]-average_perp)/sd_perp, (item[4]-average_match)/sd_match))

for item2 in candidates_non_predicted:
    scaled_list_non_predicted.append((item2[0], item2[1], (item2[2]-average_similar)/sd_similar, (item2[3]-average_perp)/sd_perp, (item2[4]-average_match)/sd_match))

print(scaled_list_non_predicted)
print(scaled_list_predicted)

def rescore(k, scaled_list_predicted):
    word_scores = []
    for word, pred, sim, perpl, comm in scaled_list_predicted:
        word_scores.append((word, sim-2*perpl+k*comm))
    for word, pred, sim, perpl, comm in scaled_list_non_predicted:
        word_scores.append((word, sim-2*perpl+k*comm))
    word_scores = sorted(word_scores, key=lambda x: x[1], reverse=True)
    return(word_scores)

def show_n(n, word_scores):
    for i in range(n):
        print(f"The {word_scores[i][0]} I felt was overwhelming.")


def plotting(scaled_list_non_predicted, scaled_list_predicted):
    def plot(scaled, fig, ax, color):
        x = []
        y = []
        label = []

        for key, a,b,c,score in scaled:
            label.append(key)
            x.append(b)
            y.append(c)
        ax.plot(x,y,"o",label="WORDS", markersize=4, color = color)
        for i, label in enumerate(label):
            ax.text(x[i], y[i], label, fontsize=5, ha="right", va="bottom", color=color)

    fig, ax = plt.subplots()
    values = scaled_list_non_predicted+scaled_list_predicted
    plot(values,fig,ax,"blue")
    plt.show(block=False)

plotting(scaled_list_non_predicted, scaled_list_predicted)
while True:
    k = float(input("slider"))
    word_scores = rescore(k, scaled_list_predicted)
    show_n(5, word_scores)