import React, { useState, useRef } from "react";
import {
  Form,
  Button,
  Container,
  Alert,
  Table,
  Badge,
  Spinner,
} from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";

function QuestionChecker() {
  const [question, setQuestion] = useState("");
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResponse(null);
    setLoading(true);

    try {
      let res;

      if (file) {
        const formData = new FormData();
        formData.append("file", file);

        res = await fetch("http://localhost:5000/check_file", {
          method: "POST",
          body: formData,
        });
      } else if (question.trim() !== "") {
        res = await fetch("http://localhost:5000/check_question", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ question }),
        });
      } else {
        setLoading(false);
        setError("Please enter a question or upload a file.");
        return;
      }

      const data = await res.json();

      if (res.ok) {
        setResponse(data);
      } else {
        setError(data.error || "Something went wrong.");
      }
    } catch (err) {
      setError("Server error.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setQuestion("");
    setFile(null);
    setResponse(null);
    setError("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <Container className="py-4">
      <h2 className="text-center mb-4">Question Similarity Checker</h2>

      <Form
        className="border p-4 rounded shadow-sm bg-light"
        onSubmit={handleSubmit}
      >
        <Form.Group className="mb-3">
          <Form.Label>Enter a Question</Form.Label>
          <Form.Control
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Type your question here..."
            onKeyDown={(e) => {
              if (e.key === "Enter" && !file) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
        </Form.Group>

        <div className="mb-3 text-center">OR</div>

        <Form.Group className="mb-3">
          <Form.Label>Upload File (.csv, .xlsx, .docx)</Form.Label>
          <Form.Control
            type="file"
            accept=".csv,.xlsx,.xls,.docx"
            onChange={(e) => setFile(e.target.files[0])}
            ref={fileInputRef}
          />
        </Form.Group>

        <div className="d-flex gap-2">
          <Button type="submit" variant="primary">
            Submit
          </Button>
          <Button variant="secondary" onClick={handleClear}>
            Clear
          </Button>
        </div>
      </Form>

      {loading && (
        <div className="text-center my-4">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Analyzing...</span>
          </Spinner>
          <div className="mt-2">Analyzing questions...</div>
        </div>
      )}

      {error && (
        <Alert variant="danger" className="mt-3">
          {error}
        </Alert>
      )}

      {response && Array.isArray(response) && (
        <div className="mt-4">
          <h5 className="mb-3">Bulk Analysis Results</h5>
          <Table bordered hover responsive className="shadow-sm table-striped align-middle text-center">
            <thead className="table-dark">
              <tr>
                <th>#</th>
                <th>Question</th>
                <th>Similar?</th>
                <th>Same Topic?</th>
                <th>Predicted Topic</th>
                <th>Similar Question</th>
                <th>Marks</th>
                <th>Weightage</th>
              </tr>
            </thead>
            <tbody>
              {response.map((item, idx) => (
                <tr key={idx}>
                  <td>{idx + 1}</td>
                  <td className="text-start">{item.question}</td>
                  <td>
                    <Badge bg={item.similar_questions ? "success" : "secondary"}>
                      {item.similar_questions ? "Yes" : "No"}
                    </Badge>
                  </td>
                  <td>
                    <Badge bg={item.same_topic ? "success" : "secondary"}>
                      {item.same_topic ? "Yes" : "No"}
                    </Badge>
                  </td>
                  <td>
                    <Badge bg="info" text="dark">
                      {item.predicted_topic}
                    </Badge>
                  </td>
                  <td className="text-start">{item.similar_question_name}</td>
                  <td>
                    <Badge bg="primary">{item.marks}</Badge>
                  </td>
                  <td>
                    <Badge bg="warning" text="dark">
                      {item.weightage}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}

      {response && !Array.isArray(response) && (
        <Alert variant="success" className="mt-4">
          <p>
            <strong>Question:</strong> {response.question}
          </p>
          <p>
            <strong>Similar Question:</strong> {response.similar_question_name}
          </p>
          <p>
            <strong>Same Topic:</strong> {String(response.same_topic)}
          </p>
          <p>
            <strong>Predicted Topic:</strong> {response.predicted_topic}
          </p>
          <p>
            <strong>Marks:</strong> {response.marks}
          </p>
          <p>
            <strong>Weightage:</strong> {response.weightage}
          </p>
        </Alert>
      )}
    </Container>
  );
}

export default QuestionChecker;
