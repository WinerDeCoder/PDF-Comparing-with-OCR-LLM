// client/src/App.js
import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [responseText, setResponseText] = useState("Response will appear here...");
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file1 || !file2) {
      setResponseText("Please upload both PDF files.");
      return;
    }

    const formData = new FormData();
    formData.append("file_1", file1);
    formData.append("file_2", file2);

    try {
      setLoading(true);
      setResponseText("Processing...");
      const response = await axios.post("http://172.17.16.10:8006/upload-pdf", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      if (response.data.status === "success") {
        // Ensure it's a JSON object, even if the server sends a string
        let responseContent = response.data.mistral_response;
        if (typeof responseContent === 'string') {
          responseContent = JSON.parse(responseContent);
        }
        // Pretty print the JSON
        const formattedResponse = JSON.stringify(responseContent, null, 2);
        setResponseText(formattedResponse);
        
      } else {
        setResponseText("Error: " + response.data.message);
      }
    } catch (error) {
      setResponseText("Error: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>PDF Comparison Tool</h1>

      <input type="file" accept="application/pdf" onChange={(e) => setFile1(e.target.files[0])} />
      <input type="file" accept="application/pdf" onChange={(e) => setFile2(e.target.files[0])} />

      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Processing..." : "Process"}
      </button>

      <div style={{ marginTop: "20px", whiteSpace: "pre-wrap", textAlign: "left", background: "#f6f6f6", padding: "10px", borderRadius: "8px" }}>
        <pre>{responseText}</pre>
      </div> 
    </div>
  );
}

export default App;

