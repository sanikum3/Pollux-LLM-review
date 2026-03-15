from pdf_extract import extract
from grobid import get_data
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import json
import re

def split_sentences_ru(text):
    text = re.sub(r'\s+', ' ', text)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 30]

def analyze(text_f):
    TOPICS = [
        "Economics",
        "Digital economy",
        "E-commerce",
        "Business",
        "Management",
        "Marketing",
        "Technology",
        "Information technology",
        "Artificial intelligence",
        "Data analysis",
        "Innovation",
        "Public policy",
        "Education",
        "Social sciences"
    ]

    get_data(text_f) #ВРЕМЕННО
    file_name = extract("result.xml")
    file_name = "result.txt"
    with open(file_name, 'r', encoding='utf-8') as file:
        text = file.read()
    tokenizer = AutoTokenizer.from_pretrained(
        "joeddav/xlm-roberta-large-xnli",
        use_fast=False
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        "joeddav/xlm-roberta-large-xnli"
    )    
    classifier = pipeline("zero-shot-classification", model=model, tokenizer=tokenizer)
    embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    sentences = split_sentences_ru(text)
    preview = " ".join(sentences[:10])
    topic_result = classifier(preview, TOPICS)

    main_topic = topic_result["labels"][0]

    embeddings = embedder.encode(sentences)

    n_clust = min(3, len(sentences))
    kmeans = KMeans(n_clusters=n_clust, random_state=42)

    labels = kmeans.fit_predict(embeddings)

    subtopics = {}
    for s, l in zip(sentences, labels):
        subtopics.setdefault(f"subtopic_{l+1}", []).append(s)

    return ({
        "main_topic" : main_topic,
        "subtopics" : subtopics,
        "text_length" : len(text),
        "sentence_count" : len(sentences)
    }  , text)  

def build_input(orig_text, analysis):
    payload = {
        "original_text" : orig_text,
        "analysis" : analysis,
        "task" : "Написать экспертную рецензию"
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)

