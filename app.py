from flask import Flask, request, jsonify
from flask_cors import CORS
from similarity_checker import QuestionSimilarityChecker

app = Flask(__name__)
CORS(app)

similarity_checker = QuestionSimilarityChecker()

@app.route('/check_question', methods=['POST'])
def check_question():
    data = request.json
    new_question = data.get('question')
    given_topic = data.get('topic')

    similar_questions_exist, similar_questions_same_topic, invalid_topic, similar_question = similarity_checker.check_similarity(new_question, given_topic)
    
    # No need to manually vectorize anymore
    marks = similarity_checker.predict_marks(new_question)
    weightage = similarity_checker.predict_weightage(new_question)

    output_data = {
        "similar_questions": similar_questions_exist,
        "same_topic": similar_questions_same_topic,
        "similar_question_name": similar_question,
        "invalid_topic": invalid_topic,
        "marks": int(marks),
        "weightage": int(weightage)
    }

    return jsonify(output_data)


# ✅ Add this part here — BELOW check_question, ABOVE main block
@app.route('/topics', methods=['GET'])
def get_topics():
    topics = similarity_checker.dataset['topic'].dropna().unique().tolist()
    return jsonify(topics)

# ⬇️ Keep this at the end
if __name__ == '__main__':
    app.run(debug=True)
