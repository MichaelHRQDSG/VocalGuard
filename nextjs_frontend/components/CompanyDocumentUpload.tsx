// CompanyDocumentUpload Component
import React, { useState, useEffect } from 'react';
import './ImageSlider.css'; // 导入样式

const CompanyDocumentUpload = () => {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [documentType, setDocumentType] = useState('HR'); // Default selection is 'HR'
    const [uploadMessage, setUploadMessage] = useState('');
  
    // Handle file selection
    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files) {
        const file = e.target.files[0];
        if (file.type !== 'application/pdf') {
          alert('Only PDF files are allowed.');
          return;
        }
        setSelectedFile(file);
      }
    };
  
    // Handle form submission
    const handleSubmit = async (e: React.FormEvent) => {
      e.preventDefault();
  
      if (!selectedFile) {
        alert('Please select a PDF file to upload.');
        return;
      }
  
      try {
        const formData = new FormData();
        formData.append('documentFile', selectedFile); // Append the selected PDF file
        formData.append('documentType', documentType); // Append the selected document type
  
        // Send the POST request with FormData
        const response = await fetch('http://101.64.178.171:8001/upload-document', {
          method: 'POST',
          body: formData,
        });
  
        if (!response.ok) {
          alert('Upload failed, please try again.');
          return;
        }
  
        const data = await response.json();
        setUploadMessage(`File uploaded successfully! Document ID: ${data.document_id}`);
      } catch (error) {
        console.error('Error uploading document:', error);
        alert('An error occurred during upload, please try again.');
      }
    };
  
    return (
      <div className="container">
        <h1>Company Document Upload</h1>
        <p>Upload your company documents here. Please select the appropriate category for the document.</p>
  
        <form className="upload-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="document-upload" className="file-label">
              Upload PDF Document
            </label>
            <input
              id="document-upload"
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
              className="file-input"
            />
          </div>
  
          {/* Radio button selection for document type */}
          <div className="form-group">
            <p>Select Document Type:</p>
            <label>
              <input
                type="radio"
                name="documentType"
                value="HR"
                checked={documentType === 'HR'}
                onChange={() => setDocumentType('HR')}
              />
              Human Resources Document
            </label>
            <label>
              <input
                type="radio"
                name="documentType"
                value="Policy"
                checked={documentType === 'Policy'}
                onChange={() => setDocumentType('Policy')}
              />
              Policy Document
            </label>
          </div>
  
          <button type="submit" className="btn">Upload Document</button>
        </form>
  
        {uploadMessage && <div className="upload-message">{uploadMessage}</div>}
      </div>
    );
  };
  
  export default CompanyDocumentUpload;
  