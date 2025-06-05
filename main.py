import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import pipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import spacy
import collections
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch.nn.functional as F

print("Finished importing modules")
word = "anonymous"




app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins":"*"}})



nlp = spacy.load("en_core_web_sm")
print("spacy model loaded")

model_roberta = AutoModelForSequenceClassification.from_pretrained("textattack/distilbert-base-uncased-CoLA")
tokenise_roberta = AutoTokenizer.from_pretrained("textattack/distilbert-base-uncased-CoLA")


#MODEL FOR PERPLEXITY



#EXPLANATION
######################ASDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD MODEL NOWNFNEOIDNFLNKFHFL KFH FJ JFKLJ#################################################


# model_name = "google/flan-t5-large"
# model_expl = T5ForConditionalGeneration.from_pretrained(model_name)
# tokenizer_expl = T5Tokenizer.from_pretrained(model_name)
# print(explain("fkjsdlf", "joyful", "happy", tokenizer_expl, model_expl))


def explain(text, word1, word2, tokenizer_expl, model_expl):
    prompt = f"the difference between '{word1}' and '{word2}'"
    inputs = tokenizer_expl.encode("Explain succintly" + prompt, return_tensors="pt")
    outputs = model_expl.generate(inputs, max_new_tokens=100, num_beams=4, repetition_penalty=2.0, no_repeat_ngram_size=3)
    return(tokenizer_expl.decode(outputs[0], skip_special_tokens=True))




########### PREDICT WORD ###################
fill_mask = pipeline("fill-mask", model="bert-base-uncased")
print("bert model loaded")

####### SIMILARITY MODEL ##################
model_similarity = SentenceTransformer('paraphrase-MiniLM-L12-v2')
print("similarity model loaded")



def get_synonyms(word):
    word = word.lower()
    if word == "fear":
        words = ['anxiety', 'fearfulness', 'dread', 'panic', 'terror', 'fright', 'worry', 'horror', 'trepidation', 'scare', 'concern', 'dismay', 'alarm', 'phobia', 'nervousness', 'alarum', 'pang', 'apprehension', 'agitation', 'creeps', 'jitters', 'consternation', 'twinge', 'timidity', 'perturbation', 'cowardice', 'disquiet', 'qualm', 'funk', 'willies', 'discomposure', 'faintheartedness', 'timorousness', 'worry', 'fret', 'trouble', 'stress', 'sweat', 'bother', 'care a hang', 'stew', 'fuss', 'sweat blood', 'despair', 'give a hang', 'long', 'pine', 'agonize', 'yearn', 'chafe', 'anxiety', 'fearfulness', 'dread', 'panic', 'terror', 'fright', 'worry', 'horror', 'trepidation', 'scare', 'concern', 'dismay', 'alarm', 'phobia', 'nervousness', 'alarum', 'pang', 'apprehension', 'agitation', 'creeps', 'jitters', 'consternation', 'twinge', 'timidity', 'perturbation', 'cowardice', 'disquiet', 'qualm', 'funk', 'willies', 'discomposure', 'faintheartedness', 'timorousness', 'worry', 'fret', 'trouble', 'stress', 'sweat', 'bother', 'care a hang', 'stew', 'fuss', 'sweat blood', 'despair', 'give a hang', 'long', 'pine', 'agonize', 'yearn', 'chafe']
    elif word == "shone":
        words = ['glowed', 'glinted', 'gleamed', 'beamed', 'burnt', 'sparkled', 'radiated', 'flickered', 'flared', 'rayed', 'shimmered', 'glimmered', 'twinkled', 'blazed', 'glistened', 'illumined', 'glittered', 'lighted', 'burned', 'lit', 'illuminated', 'flashed', 'glared', 'brightened', 'beat (down)', 'blinked', 'lightened', 'sheened', 'flamed', 'blinded', 'winked', 'dazzled', 'fired', 'spangled', 'lustred', 'scintillated', 'luminesced', 'irradiated', 'glistered', 'winkled', 'lustered', 'coruscated', 'dazed', 'bedazzled', 'glowed', 'glinted', 'gleamed', 'beamed', 'burnt', 'sparkled', 'radiated', 'flickered', 'flared', 'rayed', 'shimmered', 'glimmered', 'twinkled', 'blazed', 'glistened', 'illumined', 'glittered', 'lighted', 'burned', 'lit', 'illuminated', 'flashed', 'glared', 'brightened', 'beat (down)', 'blinked', 'lightened', 'sheened', 'flamed', 'blinded', 'winked', 'dazzled', 'fired', 'spangled', 'lustred', 'scintillated', 'luminesced', 'irradiated', 'glistered', 'winkled', 'lustered', 'coruscated', 'dazed', 'bedazzled']
    elif word == "anticipation":
        words = ['expectation', 'expectancy', 'expectance', 'contemplation', 'prospect', 'dread', 'apprehension', 'alarm', 'foreboding', 'alarum', 'misgiving', 'expectation', 'expectancy', 'expectance', 'contemplation', 'prospect', 'dread', 'apprehension', 'alarm', 'foreboding', 'alarum', 'misgiving']
    elif word == "cause":
        words = ['create', 'bring', 'generate', 'prompt', 'produce', 'do', 'work', 'induce', 'spawn', 'yield', 'effect', 'make', 'invoke', 'effectuate', 'result (in)', 'bring about', 'catalyze', 'draw on', 'translate (into)', 'encourage', 'found', 'promote', 'give rise to', 'introduce', 'breed', 'beget', 'engender', 'occasion', 'bring forth', 'bring on', 'contribute (to)', 'initiate', 'determine', 'inaugurate', 'establish', 'launch', 'begin', 'pioneer', 'develop', 'start', 'decide', 'foster', 'institute', 'render', 'cultivate', 'further', 'conduce (to)', 'set up', 'forward', 'enact', 'advance', 'set', 'turn out', 'father', 'nurture', 'innovate', 'nourish', 'reason', 'determinant', 'causation', 'source', 'causality', 'antecedent', 'occasion', 'consideration', 'factor', 'origin', 'impetus', 'incentive', 'mother', 'stimulus', 'root', 'instigation', 'inspiration', 'spring', 'be-all and end-all', 'alpha and omega', 'create', 'bring', 'generate', 'prompt', 'produce', 'do', 'work', 'induce', 'spawn', 'yield', 'effect', 'make', 'invoke', 'effectuate', 'result (in)', 'bring about', 'catalyze', 'draw on', 'translate (into)', 'encourage', 'found', 'promote', 'give rise to', 'introduce', 'breed', 'beget', 'engender', 'occasion', 'bring forth', 'bring on', 'contribute (to)', 'initiate', 'determine', 'inaugurate', 'establish', 'launch', 'begin', 'pioneer', 'develop', 'start', 'decide', 'foster', 'institute', 'render', 'cultivate', 'further', 'conduce (to)', 'set up', 'forward', 'enact', 'advance', 'set', 'turn out', 'father', 'nurture', 'innovate', 'nourish', 'reason', 'determinant', 'causation', 'source', 'causality', 'antecedent', 'occasion', 'consideration', 'factor', 'origin', 'impetus', 'incentive', 'mother', 'stimulus', 'root', 'instigation', 'inspiration', 'spring', 'be-all and end-all', 'alpha and omega']
    elif word == "curious":
        words = ['inquisitive', 'interested', 'nosey', 'nosy', 'concerned', 'prying', 'questioning', 'officious', 'intrusive', 'quizzical', 'obtrusive', 'snoopy', 'meddlesome', 'meddling', 'interrogative', 'inquisitorial', 'interfering', 'inquisitional', 'inquisitive', 'interested', 'nosey', 'nosy', 'concerned', 'prying', 'questioning', 'officious', 'intrusive', 'quizzical', 'obtrusive', 'snoopy', 'meddlesome', 'meddling', 'interrogative', 'inquisitorial', 'interfering', 'inquisitional']
    elif word == "issues":
        words = ['consequences', 'outcomes', 'results', 'resultants', 'effects', 'products', 'developments', 'implications', 'aftermaths', 'matters of course', 'aftereffects', 'fruits', 'precipitates', 'children', 'ramifications', 'sequels', 'fates', 'corollaries', 'sequences', 'conclusions', 'upshots', 'outgrowths', 'repercussions', 'backwashes', 'byproducts', 'echos', 'side effects', 'side reactions', 'echoes', 'denouements', 'fallouts', 'dénouements', 'by-products', 'aftershocks', 'afterclaps', 'ripples', 'offshoots', 'blowbacks', 'spin-offs', 'afterglows', 'publishes', 'prints', 'reprints', 'comes out with', 'gets out', 'reissues', 'produces', 'contributes', 'edits', 'markets', 'copublishes', 'manufactures', 'puts out', 'syndicates', 'serializes', 'republishes', 'distributes']
    elif word == "focus":
        words = ['center', 'hub', 'capital', 'mecca', 'core', 'heart', 'seat', 'locus', 'base', 'nucleus', 'central', 'nexus', 'axis', 'ground zero', 'headquarters', 'epicenter', 'eye', 'navel', 'nerve center', 'cynosure', 'playground', 'omphalos', "where it's at", 'hot spot', 'essence', 'attraction', 'hotbed', 'magnet', 'kernel', 'hive', 'nub', 'pith', 'happy hunting ground', 'thick', 'deep', 'soul', 'playland', 'loadstone', 'polestar', 'lodestone', 'quintessence', 'concentrate', 'rivet', 'center', 'train', 'fasten', 'point', 'aim', 'home (in on)', 'direct', 'refocus', 'set', 'heed', 'level', 'zero (in on)', 'attend', 'mind', 'nail', 'fixate (on)', 'hone in (on)', 'obsess (over)', 'center', 'hub', 'capital', 'mecca', 'core', 'heart', 'seat', 'locus', 'base', 'nucleus', 'central', 'nexus', 'axis', 'ground zero', 'headquarters', 'epicenter', 'eye', 'navel', 'nerve center', 'cynosure', 'playground', 'omphalos', "where it's at", 'hot spot', 'essence', 'attraction', 'hotbed', 'magnet', 'kernel', 'hive', 'nub', 'pith', 'happy hunting ground', 'thick', 'deep', 'soul', 'playland', 'loadstone', 'polestar', 'lodestone', 'quintessence', 'concentrate', 'rivet', 'center', 'train', 'fasten', 'point', 'aim', 'home (in on)', 'direct', 'refocus', 'set', 'heed', 'level', 'zero (in on)', 'attend', 'mind', 'nail', 'fixate (on)', 'hone in (on)', 'obsess (over)']
    else:
        headers = {
            "X-Api-Key":"17OFIFEu8jNMjQQgnXW1lg==FfkSwkqo1ypAXWta"
        }
        url = f"https://api.api-ninjas.com/v1/thesaurus?word={word}"
        input("USING AN API KEY")
        response = requests.get(url, headers=headers)
        words = response.json()["synonyms"]
        print(words)
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
        if token.pos_ in {"NOUN", "VERB", "ADJ", "ADV", "SCONJ"}:
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

def rescore(coeffs, scaled_list_predicted, scaled_list_non_predicted):
    sim_coeff, gram_coeff, comm_coeff = coeffs
    word_scores = []
    for word, pred, sim, grammar, comm in scaled_list_predicted:
        word_scores.append((word, sim_coeff*sim+gram_coeff*grammar-comm_coeff*comm))
    for word, pred, sim, grammar, comm in scaled_list_non_predicted:
        word_scores.append((word, sim_coeff*sim+gram_coeff*grammar-comm_coeff*comm))
    word_scores = sorted(word_scores, key=lambda x: x[1], reverse=True)
    return(word_scores)

def show_n(n, word_scores, sentence, word_to_replace):
    for i in range(n):
        print(sentence.replace(word_to_replace, word_scores[i][0]))


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

def token_plotting(match_count_text,occurences):
    x = []
    y = []
    labels = []
    for word in match_count_text:
        x.append(occurences[word])
        y.append(match_count_text[word])
        labels.append(word)
    plt.plot(x, y, "o", markersize=3, color = "blue")
    for i, label in enumerate(labels):
        plt.text(x[i], y[i], label, fontsize=5,  ha="right", va="bottom", color="blue")
    plt.yscale("log")
    plt.show(block=False)

def find_word(word, doc):
    sentences = []
    for sent in doc.sents:
        if word in [token.text for token in sent]:
            sentences.append(sent)
    return(sentences)


def process(sentence, word_to_replace):
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



    plotting(scaled_list_non_predicted, scaled_list_predicted)
    while True:
        while True:
            try:
                coeff = (float(input("sim coeff : ")), float(input("grammar coeff : ")), float(input("common coeff : ")))
            except:
                continue
            finally:
                break
        word_scores = rescore(coeff, scaled_list_predicted, scaled_list_non_predicted)
        show_n(10, word_scores, sentence, word_to_replace)


text = """.
Sunset Boulevard, directed by Billy Wilder, is a 1950s noir melodrama that
investigates how the popularity of the Hollywood film industry encouraged a
social fixation on the glory of celebrity. Throughout the film, Wilder explores
the nuances of success and fame, sometimes pitting the two qualities against
each other. Sunset Boulevard demonstrates that striving for career success
can have both positive and negative outcomes; however, it suggests that
those who are swept up in Hollywood’s preoccupation with fame will almost
always experience negative consequences. Furthermore, the film interrogates
the role of the audience in this destruction, insinuating that audiences
perpetuate Hollywood’s obsession with fame through an intense fascination
with gossip and scandal, in a way that conceals its true costs.
Wilder uses the character of Joe Gillis to warn the audience about the
harmful effects of self-interest and an obsession with success. At the
beginning of the film, Joe, a struggling screenwriter, devises ‘a little plot’,
lying that Norma’s ‘silly hodgepodge’ script is ‘fascinating’ so she will
hire him as an editor. This suggests that Joe’s self-interest has destructive
implications, as he is willing to indulge Norma’s self-delusion in order to
gain money and eventual success, even though the relationship he establishes
with Norma is founded on dishonesty. Wilder also uses the ‘dead monkey
upstairs’ as a symbol of Joe’s impending doom. When Joe refers to the
monkey as Norma’s ‘only child’ and ponders the emptiness of Norma’s life, he
acknowledges that the monkey was a wild animal that had been kept locked
in the house as a pet – a plaything for Norma. As Joe watches over ‘the last
rites for that hairy old chimp’, the close-up shot of Joe’s face, framed by the
blinds and the bars of the window frame, implies a sense of confinement,
signalling to the audience that it is now Joe who is trapped in the house.
Wilder’s implicit comparison between Joe and the monkey can be seen as
a warning to the audience that Joe’s desire to get ahead could lead to him
sharing the monkey’s fate. The characterisation of Joe, and his character arc,
demonstrate that ambition and selfishness can be disastrous for an individual
and their relationships.
However, the film does not always show ambition and a desire for success
to be wholly negative. In particular, it juxtaposes Joe’s self-interest with the
characterisation of Betty Schaefer, an aspiring writer who has ‘not once’
wished for fame, and who ultimately views success as writing ‘true’ and
‘moving’ screenplays. Betty’s emphasis on creating work that holds its value
contrasts with Joe’s choice to work on Norma’s ‘idiotic script’ for short-term
gain; Betty’s ambition is presented as being more admirable than Joe’s. Near
the end of the film, Joe recognises the potential in Betty’s ambition and
Signposts the essay’s
approach to the idea of
success, establishing partial
agreement with the topic
statement (i.e. striving
for success is not always
destructive).
Signposts the approach to
the idea of fame.
Signposts an additional
element to the analysis,
which will be the focus of
the final body paragraph.
Begins the first body
paragraph with a clear
topic sentence.
Uses relevant textual
evidence and shows
understanding of how
meaning is created by the
text’s construction.
Incorporates short quotes
into the discussion.
Ends the paragraph with a
clear link to the topic.
Introduces discussion of a
second main character to
demonstrates the positive
as well as negative aspects
of ambition. The linking
word ‘however’ signals the
compare/contrast approach
being used to develop the
argument.
Chapter 06 Analytical text responses: writing the essay
Digital resources © Insight Publications 2023 English Year 12: VCE Units 3 & 4
ideals, and encourages her to leave him in Norma’s mansion so she can ‘finish
that script’, ultimately saving her from being caught up in the destructive
conflict between himself and Norma. Consequently, the film suggests that
ambition, when held by people with good intentions and values, can be a
worthy quality and can lead to positive outcomes.
While Sunset Boulevard portrays the idea of success as complex and nuanced,
it depicts fame as a fantasy or delusion that is intrinsically linked to selfimage. Norma Desmond, the ‘famous star of yesteryear’, is unable to separate
fantasy and reality, as she believes that she is still famous and has ‘fan-letters
every day’. Wilder consistently frames Norma surrounded by photographs
of herself when she was younger. The mid-shots of the many photographs
spread through the house, which is ‘crowded with Norma Desmonds’,
remind the audience that Norma has built herself a delusional self-image,
based on her fantasy of still being young and famous. However, as soon as
Joe reveals that ‘the audience left twenty years ago’ and that ‘there isn’t going
to be any picture’, Norma’s fantasy is shattered, and she realises that she
no longer has the level of fame that she dreams of. This revelation leads to
Norma’s ultimate downfall when she shoots Joe. Wilder uses Norma’s mental
breakdown to demonstrate that the fantasy of fame inevitably results in
destruction.
Sunset Boulevard also suggests that audiences are at least partly responsible
for perpetuating the Hollywood obsession with fame, through their
unstinting interest in scandal and gossip. Joe’s post-death narration further
emphasises the difference between fame and success in the eyes of the
Hollywood community. In these final scenes, Norma receives the attention
she has always wanted, as her house is swarming with ‘cops, reporters,
neighbours, passers-by … even the newsreel guys’. Instead of being viewed as
successful, however, she is pitied by the neighbourhood. Here, Wilder reveals
that, in the Hollywood of the 1950s, people could achieve fame without
success, as the public was so fascinated by scandalous stories. Indeed, Wilder
uses the final scene to critique the role of his audience in encouraging the
film industry’s fixation on fame. Norma’s direct address to ‘those wonderful
people out there in the dark’, combined with the brightly lit close-up shot
of her staring into the camera lens, directly positions the audience to feel
as though they are included in Wilder’s commentary on success and fame,
as they, too, are engrossed in Norma’s downfall. Wilder’s inclusion of the
audience makes the final argument that the obsession with fame is an issue
for the broader society, as it is fuelled by the public’s insatiable desire for
gossip and scandal. Joe’s death symbolises the destruction caused by this
obsession: it is the grim reality hidden from view by the glamorous facade of
Hollywood, but real nonetheless.
Transitions to a discussion
of the other key term in the
topic – fame.
Uses relevant
metalanguage – ‘frames’,
‘mid-shots’ – to analyse
the film’s representation
of Norma and show an
understanding of the film
genre.
Engages closely with the
destructive effects of an
obsession with fame.
Moves on to the final
signpost from the
introduction.
Continues the argument
about the distinction
drawn by the film between
success and fame.
Links strongly to the
topic through the focus
on destructive effects,
enabling a smooth
transition to the concluding
paragraph.
Chapter 06 Analytical text responses: writing the essay
© Insight Publications 2023 English Year 12: VCE Units 3 & 4 Digital resources
Sunset Boulevard presents a nuanced and complex depiction of the social
dynamics at play in the Hollywood film industry during the 1950s. Billy
Wilder challenges the idea that ambition is always destructive, yet he also
reaffirms that those who seek fame at any price are at risk of devastation.
In investigating these ideas, Sunset Boulevard encourages its audience to
critically interrogate their own role in perpetuating the social obsession with
success and fame."""

limiter = Limiter(get_remote_address, app=app)

@app.before_request
def authenticate():
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
    sorted_occurences = sorted(occurences.items(), key=lambda item: item[1], reverse=True)
    dict = {"sorted_occurences":sorted_occurences, "match_count":match_count_text}
    return(jsonify(dict))




occurences, match_count_text, doc = text_weaknesses(text, nlp)
sorted_occurences = sorted(occurences.items(), key=lambda item: item[1], reverse=True)
token_plotting(match_count_text, occurences)
input("Press enter to continue")


problematic_word = input("problematic word : ")
sentences = find_word(problematic_word, doc)
sentence = "But sometimes, we focus too much on making technology perform better which can cause ethical problems."
problematic_word = "focus"
process(sentence, problematic_word)
print(sentences)
sentence = sentences[0]
word_to_replace = problematic_word
process(sentence.text, word_to_replace)


if __name__ == '__main__':
    app.run(debug=True)