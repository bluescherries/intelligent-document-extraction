document.addEventListener("DOMContentLoaded", () => {
    console.log("Frontend JavaScript initialized successfully.");

    const form = document.getElementById("documentForm");
    const documentType = document.getElementById("documentType");
    const documentFile = document.getElementById("documentFile");
    const processButton = document.getElementById("processButton");
    const resultContainer = document.getElementById("resultContainer");

    console.log("Frontend elements:", {
        form,
        documentType,
        documentFile,
        processButton,
        resultContainer
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        console.log("Process Document button clicked.");

        const file = documentFile.files[0];
        const selectedDocumentType = documentType.value;

        if (!file) {
            showError("Please select a document.");
            return;
        }

        console.log("Selected document:", file.name);
        console.log("Selected document type:", selectedDocumentType);

        /*
         * The frontend uses CASH_FLOW_STATEMENT,
         * but our backend uses CASH_FLOW.
         *
         * Convert only this one document type.
         */
        let backendDocumentType = selectedDocumentType;

        if (selectedDocumentType === "CASH_FLOW_STATEMENT") {
            backendDocumentType = "CASH_FLOW";
        }

        console.log("Backend document type:", backendDocumentType);

        const formData = new FormData();

        formData.append("file", file);
        formData.append("document_type", backendDocumentType);

        console.log("Sending request to backend...");

        processButton.disabled = true;
        processButton.textContent = "Processing...";

        resultContainer.innerHTML = `
            <div class="processing-message">
                <h2>Processing Document...</h2>
                <p>Please wait while the document is being extracted and validated.</p>
            </div>
        `;

        try {
            const response = await fetch(
                "https://intelligent-document-extraction-i1uw.onrender.com/api/v1/documents/process",
                {
                    method: "POST",
                    body: formData
                }
            );

            console.log("Backend response status:", response.status);

            const data = await response.json();

            console.log("Backend response:", data);

            if (!response.ok) {
                const errorMessage =
                    data?.detail?.message ||
                    data?.detail?.error ||
                    data?.detail ||
                    "Document processing failed.";

                throw new Error(
                    typeof errorMessage === "string"
                        ? errorMessage
                        : JSON.stringify(errorMessage)
                );
            }

            displayResult(data);

        } catch (error) {
            console.error("Document processing error:", error);

            showError(error.message);

        } finally {
            processButton.disabled = false;
            processButton.textContent = "Process Document";
        }
    });

    function showError(message) {
        resultContainer.innerHTML = `
            <div class="error-result">
                <h2>Processing Failed</h2>
                <p>${escapeHtml(message)}</p>
                <p>Please check the document type, file format and backend server.</p>
            </div>
        `;
    }

    function displayResult(data) {
        const extractedData = data.extracted_data || {};
        const validationData = data.financial_validation || {};

        const status = data.status || "UNKNOWN";

        resultContainer.innerHTML = `
            <div class="result-card">

                <div class="result-header">
                    <div>
                        <h2>Processing Result</h2>
                        <p>Document successfully processed</p>
                    </div>

                    <span class="status-badge ${status.toLowerCase()}">
                        ${escapeHtml(status)}
                    </span>
                </div>

                <div class="result-summary">

                    <div class="summary-box">
                        <span>Document Name</span>
                        <strong>
                            ${escapeHtml(data.document_name || "N/A")}
                        </strong>
                    </div>

                    <div class="summary-box">
                        <span>Document Type</span>
                        <strong>
                            ${escapeHtml(data.document_type || "N/A")}
                        </strong>
                    </div>

                    <div class="summary-box">
                        <span>Database ID</span>
                        <strong>
                            #${escapeHtml(String(data.id || "N/A"))}
                        </strong>
                    </div>

                </div>

                <hr>

                <h3>Extracted Information</h3>

                <p class="section-description">
                    Information extracted from the document
                </p>

                <div class="json-container">
                    <pre>${escapeHtml(
                        JSON.stringify(extractedData, null, 2)
                    )}</pre>
                </div>

                <hr>

                <h3>Financial Validation</h3>

                <div class="json-container">
                    <pre>${escapeHtml(
                        JSON.stringify(validationData, null, 2)
                    )}</pre>
                </div>

                <hr>

                <h3>Raw JSON Response</h3>

                <div class="json-container">
                    <pre>${escapeHtml(
                        JSON.stringify(data, null, 2)
                    )}</pre>
                </div>

            </div>
        `;
    }

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});