import { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const SUGGESTED_PROMPTS = [
  "Summarize uploaded papers",
  "Compare methodologies",
  "List key findings",
  "Generate literature review",
];

const DOC_TAGS = [
  ["NLP", "Transformer"],
  ["Vision", "Benchmark"],
  ["Healthcare", "Clinical"],
  ["LLM", "Retrieval"],
];

function toTitle(filename) {
  return filename
    .replace(/\.pdf$/i, "")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function getStatus(chunks) {
  if (!chunks || chunks <= 0) {
    return "Queued";
  }

  if (chunks < 3) {
    return "Indexing";
  }

  return "Ready";
}

function App() {
  const fileInputRef = useRef(null);

  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [dragActive, setDragActive] = useState(false);

  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [asking, setAsking] = useState(false);

  const [documents, setDocuments] = useState([]);
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [documentSearch, setDocumentSearch] = useState("");

  const [error, setError] = useState("");
  const [theme, setTheme] = useState("light");

  const filteredDocuments = useMemo(() => {
    if (!documentSearch.trim()) {
      return documents;
    }

    const needle = documentSearch.toLowerCase();
    return documents.filter((document) =>
      document.filename.toLowerCase().includes(needle)
    );
  }, [documents, documentSearch]);

  const latestMessage = messages[messages.length - 1] || null;

  const sourcePreview = useMemo(() => {
    if (!latestMessage?.sources?.length) {
      return [];
    }

    return latestMessage.sources.slice(0, 4);
  }, [latestMessage]);

  const insights = useMemo(() => {
    if (!latestMessage?.answer) {
      return {
        keyFindings: [
          "Upload your first paper set to generate insight snapshots.",
          "Run a question to surface evidence-backed findings.",
          "Use source chips to narrow scope by paper.",
        ],
        summary:
          "ResearchMind will extract high-confidence conclusions and summarize them here.",
      };
    }

    const findings = latestMessage.answer
      .split(/(?<=[.!?])\s+/)
      .filter(Boolean)
      .slice(0, 3)
      .map((sentence) =>
        sentence.length > 150 ? `${sentence.slice(0, 150)}...` : sentence
      );

    return {
      keyFindings: findings.length > 0 ? findings : [latestMessage.answer.slice(0, 160)],
      summary:
        latestMessage.answer.length > 280
          ? `${latestMessage.answer.slice(0, 280)}...`
          : latestMessage.answer,
    };
  }, [latestMessage]);

  const loadDocuments = async () => {
    try {
      const response = await fetch(`${API_URL}/documents`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to load documents.");
      }

      setDocuments(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    document.body.dataset.theme = theme;
  }, [theme]);

  const normalizeFiles = (rawFiles) => {
    const selectedFiles = Array.from(rawFiles || []);

    const pdfFiles = selectedFiles.filter(
      (file) => file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")
    );

    if (pdfFiles.length > 10) {
      setError("You can upload a maximum of 10 PDFs at once.");
      return pdfFiles.slice(0, 10);
    }

    setError("");
    return pdfFiles;
  };

  const handleFileChange = (event) => {
    const next = normalizeFiles(event.target.files);
    setFiles(next);
    setUploadResult(null);
  };

  const onDropFiles = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragActive(false);

    const next = normalizeFiles(event.dataTransfer?.files);
    setFiles(next);
    setUploadResult(null);
  };

  const uploadFiles = async () => {
    if (files.length === 0) {
      setError("Please select at least one PDF.");
      return;
    }

    if (files.length > 10) {
      setError("You can upload a maximum of 10 PDFs at once.");
      return;
    }

    setUploading(true);
    setError("");
    setUploadResult(null);
    setUploadStatus("Uploading and indexing documents...");

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch(`${API_URL}/documents/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed.");
      }

      setUploadResult(data);
      await loadDocuments();
      setFiles([]);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      setUploadStatus("");
    }
  };

  const toggleDocument = (filename) => {
    setSelectedDocuments((previous) => {
      if (previous.includes(filename)) {
        return previous.filter((name) => name !== filename);
      }

      return [...previous, filename];
    });
  };

  const selectAllDocuments = () => {
    setSelectedDocuments(documents.map((document) => document.filename));
  };

  const clearDocumentSelection = () => {
    setSelectedDocuments([]);
  };

  const deleteDocument = async (filename) => {
    const confirmed = window.confirm(`Delete \"${filename}\"?`);

    if (!confirmed) {
      return;
    }

    try {
      setError("");

      const response = await fetch(`${API_URL}/documents/${encodeURIComponent(filename)}`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to delete document.");
      }

      setSelectedDocuments((previous) => previous.filter((name) => name !== filename));
      await loadDocuments();
    } catch (err) {
      setError(err.message);
    }
  };

  const clearAllDocuments = async () => {
    const confirmed = window.confirm("Are you sure you want to delete ALL uploaded documents?");

    if (!confirmed) {
      return;
    }

    try {
      setError("");

      const response = await fetch(`${API_URL}/documents`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to clear documents.");
      }

      setDocuments([]);
      setSelectedDocuments([]);
      setMessages([]);
    } catch (err) {
      setError(err.message);
    }
  };

  const askQuestion = async () => {
    if (!query.trim()) {
      setError("Please enter a question.");
      return;
    }

    const currentQuery = query.trim();

    setAsking(true);
    setError("");
    setQuery("");

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: currentQuery,
          selected_documents: selectedDocuments.length > 0 ? selectedDocuments : null,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Query failed.");
      }

      setMessages((previous) => [
        ...previous,
        {
          question: currentQuery,
          answer: data.answer || "",
          sources: data.sources || [],
          selectedDocuments: [...selectedDocuments],
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setAsking(false);
    }
  };

  const applyPrompt = (prompt) => {
    setQuery(prompt);
  };

  return (
    <div className="rm-app">
      <aside className="rm-sidebar">
        <div className="sidebar-top">
          <div className="brand-block">
            <div className="brand-mark">RM</div>
            <div>
              <h1 className="brand-title">ResearchMind</h1>
              <p className="brand-subtitle">AI Research Assistant</p>
            </div>
          </div>

          <input
            ref={fileInputRef}
            className="file-input"
            type="file"
            accept=".pdf,application/pdf"
            multiple
            onChange={handleFileChange}
          />

          <button className="sidebar-upload" onClick={() => fileInputRef.current?.click()}>
            Upload Documents
          </button>

          <input
            className="doc-search"
            placeholder="Search documents"
            value={documentSearch}
            onChange={(event) => setDocumentSearch(event.target.value)}
          />
        </div>

        <div className="sidebar-section">
          <div className="section-header-row">
            <h2>Uploaded Papers</h2>
            <span>{filteredDocuments.length}</span>
          </div>

          <div className="sidebar-doc-list">
            {filteredDocuments.length === 0 && (
              <div className="empty-small">No papers match your search.</div>
            )}

            {filteredDocuments.map((document, index) => {
              const isSelected = selectedDocuments.includes(document.filename);
              const status = getStatus(document.chunks);

              return (
                <label key={document.filename} className={`sidebar-doc-item ${isSelected ? "active" : ""}`}>
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => toggleDocument(document.filename)}
                  />

                  <div className="doc-item-content">
                    <div className="doc-item-title">{toTitle(document.filename)}</div>
                    <div className="doc-item-meta">
                      <span className={`status-dot ${status.toLowerCase()}`}></span>
                      <span>{status}</span>
                      <span>{document.chunks || 0} chunks</span>
                    </div>
                  </div>

                  <button
                    type="button"
                    className="inline-delete"
                    onClick={() => deleteDocument(document.filename)}
                    aria-label={`Delete ${document.filename}`}
                  >
                    x
                  </button>
                </label>
              );
            })}
          </div>

          <div className="sidebar-actions">
            <button onClick={selectAllDocuments}>Select All</button>
            <button onClick={clearDocumentSelection}>Clear</button>
            <button onClick={clearAllDocuments}>Clear All</button>
          </div>
        </div>

      </aside>

      <main className="rm-main">
        <header className="top-nav">
          <div className="workspace-pill">Workspace: Research Lab</div>

          <div className="top-nav-actions">
            <button
              className="nav-icon"
              onClick={() => setTheme((previous) => (previous === "light" ? "dim" : "light"))}
            >
              {theme === "light" ? "Dim" : "Light"}
            </button>
          </div>
        </header>

        <div className="content-grid">
          <section className="conversation-zone">
            <div className="hero-card">
              <p className="hero-kicker">ResearchMind</p>
              <h2>AI Research Assistant</h2>
              <p>
                Ask evidence-grounded questions across your private paper collection with citations,
                source previews, and structured insight extraction.
              </p>
            </div>

            <div className="ask-card">
              <div className="ask-row">
                <textarea
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Ask questions across your research papers..."
                  rows="3"
                />
                <button className="ask-button" onClick={askQuestion} disabled={asking}>
                  {asking ? "Thinking..." : "Ask"}
                </button>
              </div>

              <div className="scope-row">
                {selectedDocuments.length === 0 ? (
                  <span>Query scope: All uploaded papers</span>
                ) : (
                  <span>Query scope: {selectedDocuments.length} selected paper(s)</span>
                )}
              </div>

              <div className="prompt-row">
                {SUGGESTED_PROMPTS.map((prompt) => (
                  <button key={prompt} onClick={() => applyPrompt(prompt)}>
                    {prompt}
                  </button>
                ))}
              </div>
            </div>

            <div className="chat-card">
              {messages.length === 0 && (
                <div className="chat-empty">
                  <div className="empty-title">Start your first research conversation</div>
                  <p>
                    Upload papers, choose a prompt, and ask focused questions to generate answers with
                    citations.
                  </p>
                </div>
              )}

              {messages.map((message, index) => {
                const sourceChips = Array.from(
                  new Set((message.sources || []).map((source) => source.document_name || "Source"))
                );

                return (
                  <div className="chat-turn" key={`${message.timestamp || index}-${index}`}>
                    <div className="user-bubble">
                      <div className="bubble-label">You</div>
                      <p>{message.question}</p>
                    </div>

                    <div className="assistant-row">
                      <div className="assistant-bubble">
                        <div className="bubble-label">ResearchMind</div>

                        {message.selectedDocuments?.length > 0 && (
                          <div className="doc-chip-row">
                            {message.selectedDocuments.map((filename) => (
                              <span key={filename} className="doc-chip">
                                {toTitle(filename)}
                              </span>
                            ))}
                          </div>
                        )}

                        <p>{message.answer}</p>

                        {sourceChips.length > 0 && (
                          <div className="source-chip-row">
                            {sourceChips.map((sourceName) => (
                              <span key={sourceName} className="source-chip">
                                {toTitle(sourceName)}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <section className="workspace-card">
              <div className="section-header-row">
                <h2>Document Workspace</h2>
                <span>{documents.length} docs</span>
              </div>

              <div
                className={`drop-zone ${dragActive ? "dragging" : ""}`}
                onDragOver={(event) => {
                  event.preventDefault();
                  setDragActive(true);
                }}
                onDragLeave={(event) => {
                  event.preventDefault();
                  setDragActive(false);
                }}
                onDrop={onDropFiles}
              >
                <div className="drop-illustration">PDF</div>
                <div>
                  <strong>Drag and drop PDF files</strong>
                  <p>or use Upload Documents in the sidebar. Up to 10 PDFs per batch.</p>
                </div>
              </div>

              {files.length > 0 && (
                <div className="queued-files">
                  <div className="queued-header">Queued for upload</div>
                  {files.map((file) => (
                    <div key={file.name} className="queued-file-item">
                      <span>{file.name}</span>
                      <span>{Math.round(file.size / 1024)} KB</span>
                    </div>
                  ))}
                </div>
              )}

              <button className="process-button" onClick={uploadFiles} disabled={uploading || files.length === 0}>
                {uploading ? "Processing documents..." : "Process Documents"}
              </button>

              {uploading && (
                <div className="upload-progress-wrap">
                  <div className="upload-progress-indeterminate"></div>
                  <span>{uploadStatus}</span>
                </div>
              )}

              {uploadResult?.results?.length > 0 && (
                <div className="upload-result">
                  {uploadResult.results.map((result) => (
                    <div key={result.filename} className="upload-result-row">
                      <span>{toTitle(result.filename)}</span>
                      <span>{result.status === "success" ? `${result.chunks} chunks indexed` : result.error}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="doc-card-grid">
                {documents.length === 0 && (
                  <div className="workspace-empty">
                    <h3>No uploaded PDFs yet</h3>
                    <p>
                      Add your first research papers to unlock citation-grounded Q and A and automated
                      insight extraction.
                    </p>
                  </div>
                )}

                {documents.map((document, index) => {
                  const status = getStatus(document.chunks);
                  const tags = DOC_TAGS[index % DOC_TAGS.length];

                  return (
                    <article key={document.filename} className="doc-workspace-card">
                      <div className="doc-workspace-header">
                        <h3>{toTitle(document.filename)}</h3>
                        <span className={`status-pill ${status.toLowerCase()}`}>{status}</span>
                      </div>

                      <p className="doc-authors">Authors: Research Team Unknown</p>
                      <p className="doc-date">
                        Uploaded: {new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                      </p>

                      <div className="doc-progress-track">
                        <div
                          className="doc-progress-fill"
                          style={{ width: `${Math.min(100, ((document.chunks || 0) / 8) * 100)}%` }}
                        ></div>
                      </div>

                      <div className="tag-row">
                        {tags.map((tag) => (
                          <span key={tag}>{tag}</span>
                        ))}
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>
          </section>

          <aside className="insights-zone">
            <section className="insight-card">
              <h2>Research Insights</h2>

              <h3>Key Findings</h3>
              <ul>
                {insights.keyFindings.map((finding) => (
                  <li key={finding}>{finding}</li>
                ))}
              </ul>

              <h3>Generated Summary</h3>
              <p>{insights.summary}</p>
            </section>

            <section className="insight-card">
              <h2>Reference Previews</h2>

              {sourcePreview.length === 0 && (
                <div className="empty-small">
                  Ask a question to populate source previews from the latest answer.
                </div>
              )}

              {sourcePreview.map((source, index) => (
                <article className="preview-card" key={`${source.document_name}-${index}`}>
                  <h3>{toTitle(source.document_name || "Paper")}</h3>
                  <span>Chunk {source.chunk_id ?? "N/A"}</span>
                  <p>{source.text || "No text preview returned by the API."}</p>
                </article>
              ))}
            </section>
          </aside>
        </div>

        {error && <div className="error-banner">{error}</div>}
      </main>
    </div>
  );
}

export default App;
