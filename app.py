from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from similarity_checker import QuestionSimilarityChecker, read_input_file, analyze_questions

app = Flask(__name__)
CORS(app)

# Initialize model once
try:
    similarity_checker = QuestionSimilarityChecker()
except Exception as e:
    print(f"❌ Failed to initialize model: {e}")
    similarity_checker = None

@app.route('/check_question', methods=['POST'])
def check_question():
    if similarity_checker is None:
        return jsonify({"error": "Model not initialized properly."}), 500

    try:
        # JSON input
        if request.is_json:
            data = request.get_json()
            new_question = data.get("question", "").strip()

        # FormData input
        elif "question" in request.form:
            new_question = request.form.get("question", "").strip()

        else:
            return jsonify({"error": "Unsupported request format."}), 415

        if not new_question:
            return jsonify({"error": "No valid question provided."}), 400

        similar_exist, same_topic, predicted_topic, similar_question = similarity_checker.check_similarity(new_question)
        marks = similarity_checker.predict_marks(new_question)
        weightage = similarity_checker.predict_weightage(new_question)

        return jsonify({
            "question": new_question,
            "similar_questions": similar_exist,
            "same_topic": same_topic,
            "predicted_topic": predicted_topic,
            "similar_question_name": similar_question,
            "marks": int(marks) if str(marks).isdigit() else str(marks),
            "weightage": int(weightage) if str(weightage).isdigit() else str(weightage)
        })

    except Exception as e:
        print(f"❌ Error in /check_question: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/check_file', methods=['POST'])
def check_file():
    if similarity_checker is None:
        return jsonify({"error": "Model not initialized properly."}), 500

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({"error": "No filename provided."}), 400

    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[-1].lower()
    temp_path = f"temp_input.{ext}"

    try:
        file.save(temp_path)
        df = read_input_file(temp_path)
        result_df = analyze_questions(similarity_checker, df)
        return jsonify(result_df.to_dict(orient="records"))

    except Exception as e:
        print(f"❌ Error in /check_file: {e}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route('/topics', methods=['GET'])
def get_topics():
    if similarity_checker is None:
        return jsonify({"error": "Model not initialized properly."}), 500

    try:
        topics = similarity_checker.dataset['topic'].dropna().unique().tolist()
        return jsonify(topics)
    except Exception as e:
        print(f"❌ Error in /topics: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/model_metrics', methods=['GET'])
def get_model_metrics():
    if similarity_checker is None:
        return jsonify({"error": "Model not initialized properly."}), 500

    try:
        return jsonify(similarity_checker.metrics)
    except Exception as e:
        print(f"❌ Error in /model_metrics: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
