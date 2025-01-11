#%% Libraries

import numpy as np
from gensim import corpora, models
import spacy
from spacy.lang.en import stop_words
from tqdm import tqdm

nlp = spacy.load("en_core_web_md")

#%% Preprocess text

# https://spacy.io/usage/linguistic-features


def preprocess_text(file_path, nlp, stop_word_removal=True, non_alpha_removal=True, lemmatization=True, lowercasing=True, additional_stop_words=[]):
    stop_words_to_use = list(stop_words.STOP_WORDS)
    stop_words_to_use.append(additional_stop_words)

    documents = []
    with open(file_path, "r") as f:
        for blog in tqdm(f):
            doc = nlp(blog.strip()) # Convert to spaCy doc

            if len(doc) > 1:
                if non_alpha_removal: # Remove non alpha characters
                    doc = [token for token in doc if token.is_alpha]
                
                if lemmatization: # Lemmatize words
                    doc = [token.lemma_ for token in doc]

                if stop_word_removal: # Remove stop words
                    doc = [token for token in doc if token not in stop_words_to_use]                
                
                if lowercasing: # Lowercase words
                    doc = [token.lower() for token in doc]

                documents.append(doc)

    # https://radimrehurek.com/gensim/auto_examples/core/run_corpora_and_vector_spaces.html
    dictionary = corpora.Dictionary(documents)
    corpus = [dictionary.doc2bow(doc) for doc in documents]

    dictionary.save("dictionary2.dict")
    corpora.MmCorpus.serialize("corpus2.mm", corpus)

preprocess_text("blogs.txt", nlp, additional_stop_words=["ride", "day", "bike", "road", "get", "go", "mile", "like", "way", "good", "come", "look", "nice", "think", "trip", "know", "see", "great", "today"])

#%%

# https://radimrehurek.com/gensim/auto_examples/core/run_topics_and_transformations.html

# dictionary = corpora.Dictionary.load("dictionary.dict")
# corpus = corpora.MmCorpus("corpus.mm")

# word_freq = {k: v for k, v in sorted(dictionary.cfs.items(), key = lambda item: item[1], reverse=True)}
# for id in list(word_freq.keys())[:100]:
#     print(dictionary[id])

# #%% Modelling

# tfidf = models.TfidfModel(corpus)
# corpus_tfidf = tfidf[corpus]

# # # https://radimrehurek.com/gensim/models/ldamodel.html
# lda = models.LdaModel(corpus_tfidf, num_topics=10)

# topics = lda.get_topics()
# for topic in range(10):
#     topic_probs = topics[topic, :]
#     print(f"Topic {topic}: {", ".join([dictionary[i] for i in np.argsort(topic_probs)[-10:]])}")

#%%
