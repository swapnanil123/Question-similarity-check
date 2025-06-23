import pandas as pd
import docx
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sentence_transformers import SentenceTransformer, util
import numpy as np


class QuestionSimilarityChecker:
    def __init__(self):
        # Load dataset
        self.dataset = pd.read_csv("Final_dataset.csv")

        # Embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.question_vectors = self.embedding_model.encode(
            self.dataset['question'].tolist(), convert_to_tensor=True
        )

        # Topic prediction setup
        self.topic_encoder = LabelEncoder()
        topics_encoded = self.topic_encoder.fit_transform(self.dataset['topic'].astype(str))

        self.topic_model = RandomForestClassifier(n_estimators=100)
        self.topic_model.fit(self.question_vectors.cpu().numpy(), topics_encoded)

        # Semantic threshold
        self.similarity_threshold = 0.6

        # Marks and weightage setup
        self.marks = self.dataset['marks'].values
        self.weightage = self.dataset['weightage'].values

        self.X_train, self.X_test, self.y_marks_train, self.y_marks_test, self.y_weightage_train, self.y_weightage_test = train_test_split(
            self.question_vectors.cpu().numpy(),
            self.marks,
            self.weightage,
            test_size=0.2,
            random_state=42
        )

        self.marks_model = LogisticRegression(max_iter=1000)
        self.marks_model.fit(self.X_train, self.y_marks_train)

        self.weightage_model = LogisticRegression(max_iter=1000)
        self.weightage_model.fit(self.X_train, self.y_weightage_train)

    def check_similarity(self, new_question):
        new_vector = self.embedding_model.encode(new_question, convert_to_tensor=True)

        cosine_scores = util.cos_sim(new_vector, self.question_vectors)
        similar_indices = [i for i, score in enumerate(cosine_scores[0]) if score >= self.similarity_threshold]

        similar_questions = self.dataset.iloc[similar_indices]['question'].tolist()
        similar_topics = self.dataset.iloc[similar_indices]['topic'].tolist()

        topic_probs = self.topic_model.predict_proba(new_vector.cpu().numpy().reshape(1, -1))
        max_prob_index = topic_probs.argmax()
        max_prob = topic_probs[0, max_prob_index]

        if max_prob < 0.3:  # LOWERED from 0.5
            predicted_topic = "Unknown"
        else:
            predicted_topic = self.topic_encoder.inverse_transform([max_prob_index])[0]

        same_question = similar_questions[0] if similar_questions else "null"
        same_topic = any(t == predicted_topic for t in similar_topics) if predicted_topic != "Unknown" else False
        similar_exist = len(similar_questions) > 0

        return similar_exist, same_topic, predicted_topic, same_question

    def predict_marks(self, question_text):
        embedded = self.embedding_model.encode(question_text, convert_to_tensor=True).cpu().numpy().reshape(1, -1)
        predicted = self.marks_model.predict(embedded)
        return predicted[0]

    def predict_weightage(self, question_text):
        embedded = self.embedding_model.encode(question_text, convert_to_tensor=True).cpu().numpy().reshape(1, -1)
        predicted = self.weightage_model.predict(embedded)
        return predicted[0]


def read_input_file(filepath):
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath, header=None)
        if df.shape[1] == 1:
            df.columns = ['question']
    elif filepath.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(filepath)
        if df.shape[1] == 1:
            df.columns = ['question']
    elif filepath.endswith('.docx'):
        doc = docx.Document(filepath)
        data = [para.text for para in doc.paragraphs if para.text.strip()]
        df = pd.DataFrame(data, columns=["question"])
    else:
        raise ValueError("Unsupported file format")

    df = df[df['question'].notna()]
    df = df[df['question'].str.strip() != '']
    return df.reset_index(drop=True)


def analyze_questions(model, new_df):
    results = []
    for question in new_df['question']:
        similar_exist, same_topic, predicted_topic, matched_q = model.check_similarity(question)

        try:
            predicted_marks = model.predict_marks(question)
            predicted_weightage = model.predict_weightage(question)
        except:
            predicted_marks = 0
            predicted_weightage = 0

        results.append({
            "question": question,
            "similar_questions": similar_exist,
            "same_topic": same_topic,
            "predicted_topic": predicted_topic,
            "similar_question_name": matched_q,
            "marks": predicted_marks,
            "weightage": predicted_weightage
        })

    return pd.DataFrame(results)

