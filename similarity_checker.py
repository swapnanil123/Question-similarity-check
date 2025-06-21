import pandas as pd
import csv
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sentence_transformers import SentenceTransformer, util

class QuestionSimilarityChecker:
    def __init__(self):
        # Load dataset
        self.dataset = pd.read_csv("Final_dataset.csv")
        
        # Use semantic embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.question_vectors = self.embedding_model.encode(
            self.dataset['question'].tolist(), convert_to_tensor=True
        )
        
        # Threshold for semantic similarity
        self.similarity_threshold = 0.6

        # Train topic prediction model
        self.topic_model = LogisticRegression(max_iter=1000)
        self.topic_model.fit(self.question_vectors.cpu().numpy(), self.dataset['topic'].tolist())

        # Prepare marks and weightage
        self.marks = self.dataset['marks'].values
        self.weightage = self.dataset['weightage'].values

        self.marks_classes = self.convert_to_classes(self.marks)
        self.weightage_classes = self.convert_to_classes(self.weightage)

        # Split for marks and weightage training
        self.X_train, self.X_test, self.y_marks_train, self.y_marks_test, self.y_weightage_train, self.y_weightage_test = train_test_split(
            self.question_vectors.cpu().numpy(), self.marks_classes, self.weightage_classes, test_size=0.2, random_state=42
        )

        self.marks_model = LogisticRegression(max_iter=1000)
        self.marks_model.fit(self.X_train, self.y_marks_train)

        self.weightage_model = LogisticRegression(max_iter=1000)
        self.weightage_model.fit(self.X_train, self.y_weightage_train)

    def convert_to_classes(self, values):
        return values  # you can later convert to labels like 'low', 'medium', 'high'

    def convert_to_values(self, classes):
        return classes

    def check_similarity(self, new_question, given_topic):
        # Semantic embedding
        new_question_vector = self.embedding_model.encode(new_question, convert_to_tensor=True)

        # Semantic similarity
        cosine_scores = util.cos_sim(new_question_vector, self.question_vectors)
        similar_indices = [i for i, score in enumerate(cosine_scores[0]) if score >= self.similarity_threshold]
        
        similar_questions = self.dataset.iloc[similar_indices]['question'].tolist()
        similar_topics = self.dataset.iloc[similar_indices]['topic'].tolist()

        same_topic_indices = [i for i, topic in enumerate(similar_topics) if topic == given_topic]
        similar_questions_exist = len(similar_questions) > 0
        similar_questions_same_topic = len(same_topic_indices) > 0

        # Predict topic
        predicted_topic = self.topic_model.predict(new_question_vector.cpu().numpy().reshape(1, -1))[0]
        is_valid_topic = given_topic != predicted_topic

        same_question = similar_questions[0] if similar_questions_exist else "null"

        return similar_questions_exist, similar_questions_same_topic, is_valid_topic, same_question

    def predict_marks(self, question_vector):
        # Embed the question and predict marks
        embedded = self.embedding_model.encode(question_vector, convert_to_tensor=True).cpu().numpy().reshape(1, -1)
        predicted_marks_class = self.marks_model.predict(embedded)
        predicted_marks = self.convert_to_values(predicted_marks_class)[0]
        return predicted_marks

    def predict_weightage(self, question_vector):
        embedded = self.embedding_model.encode(question_vector, convert_to_tensor=True).cpu().numpy().reshape(1, -1)
        predicted_weightage_class = self.weightage_model.predict(embedded)
        predicted_weightage = self.convert_to_values(predicted_weightage_class)[0]
        return predicted_weightage
