import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  // --------------------------------------------------
  // Upload state
  // --------------------------------------------------

  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");

  // --------------------------------------------------
  // Query state
  // --------------------------------------------------

  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [asking, setAsking] = useState(false);

  // --------------------------------------------------
  // Document management state
  // --------------------------------------------------

  const [documents, setDocuments] = useState([]);
  const [selectedDocuments, setSelectedDocuments] = useState([]);

  // --------------------------------------------------
  // General error state
  // --------------------------------------------------

  const [error, setError] = useState("");

  // --------------------------------------------------
  // Load documents
  // --------------------------------------------------

  const loadDocuments = async () => {
    try {
      const response = await fetch(
        `${API_URL}/documents`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to load documents."
        );
      }

      setDocuments(data);

    } catch (err) {
      setError(err.message);
    }
  };

  // --------------------------------------------------
  // Load documents when application starts
  // --------------------------------------------------

  useEffect(() => {
    loadDocuments();
  }, []);

  // --------------------------------------------------
  // File selection
  // --------------------------------------------------

  const handleFileChange = (event) => {
    const selectedFiles = Array.from(
      event.target.files
    );

    const pdfFiles = selectedFiles.filter(
      (file) =>
        file.type === "application/pdf" ||
        file.name
          .toLowerCase()
          .endsWith(".pdf")
    );

    if (pdfFiles.length > 10) {
      setError(
        "You can upload a maximum of 10 PDFs at once."
      );

      setFiles(pdfFiles.slice(0, 10));
      return;
    }

    setFiles(pdfFiles);
    setUploadResult(null);
    setError("");
  };

  // --------------------------------------------------
  // Upload documents
  // --------------------------------------------------

  const uploadFiles = async () => {
    if (files.length === 0) {
      setError(
        "Please select at least one PDF."
      );
      return;
    }

    if (files.length > 10) {
      setError(
        "You can upload a maximum of 10 PDFs at once."
      );
      return;
    }

    setUploading(true);
    setError("");
    setUploadResult(null);

    setUploadStatus(
      "Uploading and processing documents..."
    );

    const formData = new FormData();

    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch(
        `${API_URL}/documents/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Upload failed."
        );
      }

      setUploadResult(data);

      // Refresh document list
      await loadDocuments();

      // Clear selected upload files
      setFiles([]);

    } catch (err) {
      setError(err.message);

    } finally {
      setUploading(false);
      setUploadStatus("");
    }
  };

  // --------------------------------------------------
  // Select / deselect document
  // --------------------------------------------------

  const toggleDocument = (filename) => {
    setSelectedDocuments((previous) => {
      if (previous.includes(filename)) {
        return previous.filter(
          (name) => name !== filename
        );
      }

      return [
        ...previous,
        filename,
      ];
    });
  };

  // --------------------------------------------------
  // Select all documents
  // --------------------------------------------------

  const selectAllDocuments = () => {
    setSelectedDocuments(
      documents.map(
        (document) => document.filename
      )
    );
  };

  // --------------------------------------------------
  // Clear document selection
  // --------------------------------------------------

  const clearDocumentSelection = () => {
    setSelectedDocuments([]);
  };

  // --------------------------------------------------
  // Delete one document
  // --------------------------------------------------

  const deleteDocument = async (filename) => {
    const confirmed = window.confirm(
      `Delete "${filename}"?`
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");

      const response = await fetch(
        `${API_URL}/documents/${encodeURIComponent(
          filename
        )}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Failed to delete document."
        );
      }

      // Remove from selected documents
      setSelectedDocuments(
        (previous) =>
          previous.filter(
            (name) => name !== filename
          )
      );

      // Refresh list
      await loadDocuments();

    } catch (err) {
      setError(err.message);
    }
  };

  // --------------------------------------------------
  // Delete all documents
  // --------------------------------------------------

  const clearAllDocuments = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to delete ALL uploaded documents?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");

      const response = await fetch(
        `${API_URL}/documents`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Failed to clear documents."
        );
      }

      setDocuments([]);
      setSelectedDocuments([]);
      setMessages([]);

    } catch (err) {
      setError(err.message);
    }
  };

  // --------------------------------------------------
  // Ask question
  // --------------------------------------------------

  const askQuestion = async () => {
    if (!query.trim()) {
      setError(
        "Please enter a question."
      );
      return;
    }

    const currentQuery = query.trim();

    setAsking(true);
    setError("");
    setQuery("");

    try {
      const response = await fetch(
        `${API_URL}/query`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            query: currentQuery,

            selected_documents:
              selectedDocuments.length > 0
                ? selectedDocuments
                : null,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Query failed."
        );
      }

      const newMessage = {
        question: currentQuery,
        answer: data.answer || "",
        sources: data.sources || [],
        selectedDocuments: [
          ...selectedDocuments,
        ],
      };

      setMessages((previous) => [
        ...previous,
        newMessage,
      ]);

    } catch (err) {
      setError(err.message);

    } finally {
      setAsking(false);
    }
  };

  // --------------------------------------------------
  // Render
  // --------------------------------------------------

  return (
    <div className="app">

      {/* ==========================================
          HEADER
      ========================================== */}

      <header className="header">

        <div className="logo">
          🧠 ResearchMind
        </div>

        <div className="subtitle">
          AI-powered research assistant
        </div>

      </header>


      <main className="container">

        {/* ==========================================
            UPLOAD SECTION
        ========================================== */}

        <section className="card">

          <h2>
            Upload Research Papers
          </h2>

          <p className="description">
            Upload up to 10 PDF documents and
            ask questions across them.
          </p>


          <label className="upload-box">

            <input
              type="file"
              accept=".pdf,application/pdf"
              multiple
              onChange={handleFileChange}
            />

            <div className="upload-icon">
              📄
            </div>

            <strong>
              Click to select PDF files
            </strong>

            <span>
              Multiple PDFs supported
            </span>

          </label>


          {/* Selected upload files */}

          {files.length > 0 && (

            <div className="file-list">

              <h3>
                Selected files
              </h3>

              {files.map((file) => (

                <div
                  className="file-item"
                  key={file.name}
                >
                  📄 {file.name}
                </div>

              ))}

            </div>

          )}


          {/* Upload loading */}

          {uploading && (

            <div className="loading-box">

              <div className="spinner"></div>

              <span>
                {uploadStatus}
              </span>

            </div>

          )}


          <button
            className="primary-button"
            onClick={uploadFiles}
            disabled={
              uploading ||
              files.length === 0
            }
          >
            {uploading
              ? "Processing..."
              : "Process Documents"}
          </button>


          {/* Upload result */}

          {uploadResult && (

            <div className="success-box">

              <strong>
                Documents processed successfully.
              </strong>

              {uploadResult.results?.map(
                (result) => (

                  <div
                    className="result-item"
                    key={result.filename}
                  >

                    <span>
                      {result.filename}
                    </span>

                    <span>
                      {result.status ===
                      "success"
                        ? `${result.chunks} chunks`
                        : result.error}
                    </span>

                  </div>

                )
              )}

            </div>

          )}

        </section>


        {/* ==========================================
            DOCUMENT MANAGEMENT
        ========================================== */}

        <section className="card documents-card">

          <div className="documents-header">

            <div>

              <h2>
                📚 Your Documents
              </h2>

              <p className="description">
                Select documents to control
                which papers ResearchMind searches.
              </p>

            </div>


            {documents.length > 0 && (

              <button
                className="clear-button"
                onClick={clearAllDocuments}
              >
                Clear All
              </button>

            )}

          </div>


          {/* No documents */}

          {documents.length === 0 ? (

            <p className="empty-documents">
              No documents uploaded yet.
            </p>

          ) : (

            <>

              {/* Document controls */}

              <div className="document-controls">

                <button
                  className="secondary-button"
                  onClick={selectAllDocuments}
                >
                  Select All
                </button>

                <button
                  className="secondary-button"
                  onClick={
                    clearDocumentSelection
                  }
                >
                  Clear Selection
                </button>

              </div>


              {/* Selection information */}

              <div className="selection-info">

                {selectedDocuments.length ===
                0 ? (

                  <span>
                    🔎 Searching all{" "}
                    {documents.length} documents
                  </span>

                ) : (

                  <span>
                    🎯 Searching{" "}
                    {selectedDocuments.length}{" "}
                    selected document
                    {selectedDocuments.length !==
                    1
                      ? "s"
                      : ""}
                  </span>

                )}

              </div>


              {/* Document list */}

              <div className="document-list">

                {documents.map(
                  (document) => (

                    <div
                      className="document-row"
                      key={
                        document.filename
                      }
                    >

                      <label
                        className="document-info"
                      >

                        <input
                          type="checkbox"
                          checked={selectedDocuments.includes(
                            document.filename
                          )}
                          onChange={() =>
                            toggleDocument(
                              document.filename
                            )
                          }
                        />

                        <span>

                          📄{" "}
                          {
                            document.filename
                          }

                          <small>
                            {
                              document.chunks
                            }{" "}
                            chunks
                          </small>

                        </span>

                      </label>


                      <button
                        className="delete-button"
                        onClick={() =>
                          deleteDocument(
                            document.filename
                          )
                        }
                      >
                        Delete
                      </button>

                    </div>

                  )
                )}

              </div>

            </>

          )}

        </section>


        {/* ==========================================
            QUERY SECTION
        ========================================== */}

        <section className="card">

          <h2>
            Ask ResearchMind
          </h2>

          <p className="description">

            {selectedDocuments.length === 0
              ? "Ask questions about all your uploaded research documents."
              : `Ask questions about your ${selectedDocuments.length} selected document${
                  selectedDocuments.length !==
                  1
                    ? "s"
                    : ""
                }.`}

          </p>


          {/* Selected document indicator */}

          {selectedDocuments.length > 0 && (

            <div className="query-scope">

              🎯 Querying only:

              <div className="selected-document-tags">

                {selectedDocuments.map(
                  (filename) => (

                    <span
                      className="document-tag"
                      key={filename}
                    >
                      📄 {filename}
                    </span>

                  )
                )}

              </div>

            </div>

          )}


          <textarea
            value={query}
            onChange={(event) =>
              setQuery(
                event.target.value
              )
            }
            placeholder="e.g. What is supervised learning?"
            rows="4"
          />


          <button
            className="primary-button"
            onClick={askQuestion}
            disabled={asking}
          >

            {asking ? (

              <>
                <span className="button-spinner"></span>
                Thinking...
              </>

            ) : (

              "Ask ResearchMind"

            )}

          </button>


          {/* ========================================
              CHAT WINDOW
          ======================================== */}

          <div className="chat-window">

            {messages.length === 0 && (

              <div className="empty-chat">

                🧠 Ask ResearchMind a question
                about your documents.

              </div>

            )}


            {messages.map(
              (message, index) => (

                <div
                  className="message-group"
                  key={index}
                >

                  {/* User message */}

                  <div className="user-message">

                    <div className="message-label">
                      You
                    </div>

                    <div className="message-content">
                      {message.question}
                    </div>

                  </div>


                  {/* AI message */}

                  <div className="ai-message">

                    <div className="message-label">
                      🧠 ResearchMind
                    </div>


                    {/* Query scope */}

                    {message.selectedDocuments?.length >
                      0 && (

                      <div className="message-scope">

                        🎯 Searched:

                        {message.selectedDocuments.map(
                          (filename) => (

                            <span
                              className="document-tag"
                              key={filename}
                            >
                              {filename}
                            </span>

                          )
                        )}

                      </div>

                    )}


                    <div className="message-content">

                      {message.answer}

                    </div>


                    {/* Sources */}

                    {message.sources.length >
                      0 && (

                      <div className="sources">

                        <h4>
                          Sources
                        </h4>


                        {message.sources.map(
                          (
                            source,
                            sourceIndex
                          ) => (

                            <div
                              className="source-item"
                              key={
                                sourceIndex
                              }
                            >

                              <div className="source-header">

                                <strong>

                                  [
                                  {sourceIndex +
                                    1}
                                  ] 📄{" "}

                                  {
                                    source.document_name
                                  }

                                </strong>


                                <span>

                                  Chunk{" "}

                                  {
                                    source.chunk_id
                                  }

                                </span>

                              </div>


                              {source.text && (

                                <p className="source-text">

                                  "{source.text}"

                                </p>

                              )}

                            </div>

                          )
                        )}

                      </div>

                    )}

                  </div>

                </div>

              )
            )}

          </div>

        </section>


        {/* ==========================================
            ERROR
        ========================================== */}

        {error && (

          <div className="error-box">

            ⚠️ {error}

          </div>

        )}

      </main>

    </div>
  );
}

export default App;