import React, { useState, useEffect } from "react";
import { Form, Button, Container, Alert } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";

function QuestionChecker() {
  const [question, setQuestion] = useState("");
  const [topic, setTopic] = useState("");
  const [availableTopics, setAvailableTopics] = useState([]);
  const [response, setResponse] = useState(null);

  useEffect(() => {
    fetch("http://localhost:5000/topics")
      .then((res) => res.json())
      .then((data) => setAvailableTopics(data))
      .catch((err) => console.error("Failed to load topics:", err));
  }, []);

  const handleSubmit = async () => {
    const res = await fetch("http://localhost:5000/check_question", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, topic }),
    });
    const data = await res.json();
    setResponse(data);
  };

  const handleClear = () => {
    setResponse(null);
    setQuestion("");
    setTopic("");
  };

  const isDisabled = question.trim() === "" || topic.trim() === "";

  return (
    <Container className="py-4">
      <h2 className="text-center mb-4">Question Similarity Checker</h2>

      <Form className="border p-4 rounded shadow-sm bg-light">
        <Form.Group className="mb-3">
          <Form.Label>Enter Question</Form.Label>
          <Form.Control
            type="text"
            placeholder="e.g., What is TCP/IP?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
        </Form.Group>

        <Form.Group className="mb-3">
          <Form.Label>Select Topic</Form.Label>
          <Form.Select
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          >
            <option value="">Select Topic</option>
            {availableTopics.map((t, index) => (
              <option key={index} value={t}>
                {t}
              </option>
            ))}
          </Form.Select>
        </Form.Group>

        <div className="d-flex gap-2">
          <Button variant="primary" onClick={handleSubmit} disabled={isDisabled}>
            Submit
          </Button>
          {response && (
            <Button variant="outline-danger" onClick={handleClear}>
              Remove Result
            </Button>
          )}
        </div>
      </Form>

      {response && (
        <Alert variant="secondary" className="mt-4">
          <p>
            <strong>Similar Question Found:</strong>{" "}
            {String(response.similar_questions)}
          </p>
          <p>
            <strong>Same Topic:</strong> {String(response.same_topic)}
          </p>
          <p>
            <strong>Similar Question Name:</strong>{" "}
            {response.similar_question_name}
          </p>
          <p>
            <strong>Invalid Topic:</strong> {String(response.invalid_topic)}
          </p>
          <p>
            <strong>Predicted Marks:</strong> {response.marks}
          </p>
          <p>
            <strong>Predicted Weightage:</strong> {response.weightage}
          </p>
        </Alert>
      )}
    </Container>
  );
}

export default QuestionChecker;
