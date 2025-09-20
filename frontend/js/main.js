// Main JavaScript for Signature Recognition System
class SignatureRecognitionApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api/v1';
        this.auth = new AuthManager();
        this.currentUser = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkAuthentication();
    }

    checkAuthentication() {
        if (this.auth.isAuthenticated()) {
            this.showAuthenticatedUI();
            this.loadTemplates();
            this.loadHistory();
        } else {
            this.showLoginUI();
        }
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // File upload handlers
        this.setupFileUpload('fileInput', 'uploadArea');
        this.setupFileUpload('verifyFileInput', 'verifyUploadArea');

        // Button handlers
        document.getElementById('analyzeBtn').addEventListener('click', () => this.analyzeSignature());
        document.getElementById('verifyBtn').addEventListener('click', () => this.verifySignature());
        document.getElementById('refreshTemplates').addEventListener('click', () => this.loadTemplates());
        document.getElementById('refreshHistory').addEventListener('click', () => this.loadHistory());

        // Template selection
        document.getElementById('templateSelect').addEventListener('change', () => this.updateVerifyButton());
    }

    setupFileUpload(inputId, areaId) {
        const fileInput = document.getElementById(inputId);
        const uploadArea = document.getElementById(areaId);

        // Click to upload
        uploadArea.addEventListener('click', () => fileInput.click());

        // File selection
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e, inputId));

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                this.handleFileSelect({ target: { files } }, inputId);
            }
        });
    }

    handleFileSelect(event, inputId) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.showToast('Please select a valid image file', 'error');
            return;
        }

        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            this.showToast('File size must be less than 10MB', 'error');
            return;
        }

        // Update UI
        this.updateFilePreview(file, inputId);
        this.updateAnalyzeButton();
        this.updateVerifyButton();
    }

    updateFilePreview(file, inputId) {
        const uploadArea = document.getElementById(inputId === 'fileInput' ? 'uploadArea' : 'verifyUploadArea');
        const reader = new FileReader();
        
        reader.onload = (e) => {
            uploadArea.innerHTML = `
                <div class="file-preview">
                    <img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px; border-radius: 10px;">
                    <p><strong>${file.name}</strong></p>
                    <p>Size: ${this.formatFileSize(file.size)}</p>
                    <button class="btn btn-primary" onclick="document.getElementById('${inputId}').click()">
                        <i class="fas fa-edit"></i> Change File
                    </button>
                </div>
            `;
        };
        
        reader.readAsDataURL(file);
    }

    updateAnalyzeButton() {
        const fileInput = document.getElementById('fileInput');
        const analyzeBtn = document.getElementById('analyzeBtn');
        analyzeBtn.disabled = !fileInput.files.length;
    }

    updateVerifyButton() {
        const fileInput = document.getElementById('verifyFileInput');
        const templateSelect = document.getElementById('templateSelect');
        const verifyBtn = document.getElementById('verifyBtn');
        verifyBtn.disabled = !fileInput.files.length || !templateSelect.value;
    }

    async analyzeSignature() {
        if (!this.auth.isAuthenticated()) {
            this.showToast('Please login first', 'error');
            this.showLoginUI();
            return;
        }

        const fileInput = document.getElementById('fileInput');
        const templateName = document.getElementById('templateName').value;
        
        if (!fileInput.files.length) {
            this.showToast('Please select a file first', 'error');
            return;
        }

        this.showLoading(true);
        
        try {
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            if (templateName) {
                formData.append('template_name', templateName);
            }

            const response = await this.auth.makeAuthenticatedRequest(`${this.apiBaseUrl}/signature/upload`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                this.displayAnalysisResults(result.analysis_result);
                this.showToast('Signature analyzed successfully!', 'success');
                
                // Clear form
                fileInput.value = '';
                document.getElementById('templateName').value = '';
                this.updateAnalyzeButton();
                
                // Refresh templates and history
                this.loadTemplates();
                this.loadHistory();
            } else {
                throw new Error(result.detail || 'Analysis failed');
            }
        } catch (error) {
            this.showToast(`Analysis failed: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async verifySignature() {
        if (!this.auth.isAuthenticated()) {
            this.showToast('Please login first', 'error');
            this.showLoginUI();
            return;
        }

        const fileInput = document.getElementById('verifyFileInput');
        const templateSelect = document.getElementById('templateSelect');
        
        if (!fileInput.files.length || !templateSelect.value) {
            this.showToast('Please select a file and template', 'error');
            return;
        }

        this.showLoading(true);
        
        try {
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('template_id', templateSelect.value);

            const response = await this.auth.makeAuthenticatedRequest(`${this.apiBaseUrl}/signature/verify`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                this.displayVerificationResults(result.analysis_result);
                this.showToast('Signature verification completed!', 'success');
                
                // Clear form
                fileInput.value = '';
                templateSelect.value = '';
                this.updateVerifyButton();
                
                // Refresh history
                this.loadHistory();
            } else {
                throw new Error(result.detail || 'Verification failed');
            }
        } catch (error) {
            this.showToast(`Verification failed: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    displayAnalysisResults(result) {
        const resultsSection = document.getElementById('resultsSection');
        const authenticityScore = document.getElementById('authenticityScore');
        const confidenceLevel = document.getElementById('confidenceLevel');
        const resultStatus = document.getElementById('resultStatus');
        const resultDetails = document.getElementById('resultDetails');

        // Update scores
        authenticityScore.textContent = (result.authenticity_score * 100).toFixed(1) + '%';
        confidenceLevel.textContent = (result.confidence_level * 100).toFixed(1) + '%';

        // Update status
        resultStatus.className = 'result-status';
        if (result.is_authentic) {
            resultStatus.classList.add('authentic');
            resultStatus.innerHTML = '<i class="fas fa-check-circle"></i><span>Signature appears to be authentic</span>';
        } else {
            resultStatus.classList.add('suspicious');
            resultStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i><span>Signature appears to be suspicious</span>';
        }

        // Update details
        try {
            const details = JSON.parse(result.analysis_details);
            resultDetails.innerHTML = this.formatAnalysisDetails(details);
        } catch (e) {
            resultDetails.textContent = result.analysis_details;
        }

        // Show results
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    displayVerificationResults(result) {
        const verificationResults = document.getElementById('verificationResults');
        const matchScore = document.getElementById('matchScore');
        const matchConfidence = document.getElementById('matchConfidence');
        const verificationStatus = document.getElementById('verificationStatus');
        const verificationDetails = document.getElementById('verificationDetails');

        // Update scores
        matchScore.textContent = (result.authenticity_score * 100).toFixed(1) + '%';
        matchConfidence.textContent = (result.confidence_level * 100).toFixed(1) + '%';

        // Update status
        verificationStatus.className = 'result-status';
        if (result.is_authentic) {
            verificationStatus.classList.add('authentic');
            verificationStatus.innerHTML = '<i class="fas fa-check-circle"></i><span>Signature matches template</span>';
        } else {
            verificationStatus.classList.add('suspicious');
            verificationStatus.innerHTML = '<i class="fas fa-times-circle"></i><span>Signature does not match template</span>';
        }

        // Update details
        try {
            const details = JSON.parse(result.analysis_details);
            verificationDetails.innerHTML = this.formatAnalysisDetails(details);
        } catch (e) {
            verificationDetails.textContent = result.analysis_details;
        }

        // Show results
        verificationResults.style.display = 'block';
        verificationResults.scrollIntoView({ behavior: 'smooth' });
    }

    formatAnalysisDetails(details) {
        let html = '<div class="analysis-details">';
        
        if (details.feature_analysis) {
            html += '<h4>Feature Analysis</h4><ul>';
            for (const [key, value] of Object.entries(details.feature_analysis)) {
                html += `<li><strong>${key.replace('_', ' ')}:</strong> ${value.toFixed(3)}</li>`;
            }
            html += '</ul>';
        }
        
        if (details.stroke_analysis) {
            html += '<h4>Stroke Analysis</h4><ul>';
            for (const [key, value] of Object.entries(details.stroke_analysis)) {
                html += `<li><strong>${key.replace('_', ' ')}:</strong> ${value.toFixed(3)}</li>`;
            }
            html += '</ul>';
        }
        
        if (details.quality_indicators) {
            html += '<h4>Quality Indicators</h4><ul>';
            for (const [key, value] of Object.entries(details.quality_indicators)) {
                html += `<li><strong>${key.replace('_', ' ')}:</strong> ${value.toFixed(3)}</li>`;
            }
            html += '</ul>';
        }
        
        html += '</div>';
        return html;
    }

    async loadTemplates() {
        if (!this.auth.isAuthenticated()) {
            return;
        }

        try {
            const response = await this.auth.makeAuthenticatedRequest(`${this.apiBaseUrl}/signature/templates`);
            const result = await response.json();

            if (response.ok) {
                this.displayTemplates(result.templates);
                this.updateTemplateSelect(result.templates);
            } else {
                throw new Error(result.detail || 'Failed to load templates');
            }
        } catch (error) {
            this.showToast(`Failed to load templates: ${error.message}`, 'error');
            const templatesGrid = document.getElementById('templatesGrid');
            if (templatesGrid) {
                templatesGrid.innerHTML = '<div class="loading">Failed to load templates</div>';
            }
        }
    }

    displayTemplates(templates) {
        const templatesGrid = document.getElementById('templatesGrid');
        
        if (templates.length === 0) {
            templatesGrid.innerHTML = '<div class="loading">No templates found. Upload a signature and save it as a template.</div>';
            return;
        }

        templatesGrid.innerHTML = templates.map(template => `
            <div class="template-card">
                <div class="template-header">
                    <div class="template-name">${template.template_name}</div>
                    <div class="template-status ${template.is_verified ? 'verified' : 'pending'}">
                        ${template.is_verified ? 'Verified' : 'Pending'}
                    </div>
                </div>
                <div class="template-info">
                    <p><i class="fas fa-calendar"></i> Created: ${new Date(template.created_at).toLocaleDateString()}</p>
                </div>
                <div class="template-actions">
                    <button class="btn btn-danger" onclick="app.deleteTemplate(${template.id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('');
    }

    updateTemplateSelect(templates) {
        const templateSelect = document.getElementById('templateSelect');
        templateSelect.innerHTML = '<option value="">Choose a template...</option>';
        
        templates.forEach(template => {
            const option = document.createElement('option');
            option.value = template.id;
            option.textContent = template.template_name;
            templateSelect.appendChild(option);
        });
    }

    async deleteTemplate(templateId) {
        if (!this.auth.isAuthenticated()) {
            this.showToast('Please login first', 'error');
            return;
        }

        if (!confirm('Are you sure you want to delete this template?')) {
            return;
        }

        try {
            const response = await this.auth.makeAuthenticatedRequest(`${this.apiBaseUrl}/signature/templates/${templateId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('Template deleted successfully', 'success');
                this.loadTemplates();
            } else {
                const result = await response.json();
                throw new Error(result.detail || 'Failed to delete template');
            }
        } catch (error) {
            this.showToast(`Failed to delete template: ${error.message}`, 'error');
        }
    }

    async loadHistory() {
        if (!this.auth.isAuthenticated()) {
            return;
        }

        try {
            const response = await this.auth.makeAuthenticatedRequest(`${this.apiBaseUrl}/signature/history?limit=20`);
            const result = await response.json();

            if (response.ok) {
                this.displayHistory(result.verification_history);
            } else {
                throw new Error(result.detail || 'Failed to load history');
            }
        } catch (error) {
            this.showToast(`Failed to load history: ${error.message}`, 'error');
            const historyList = document.getElementById('historyList');
            if (historyList) {
                historyList.innerHTML = '<div class="loading">Failed to load history</div>';
            }
        }
    }

    displayHistory(history) {
        const historyList = document.getElementById('historyList');
        
        if (history.length === 0) {
            historyList.innerHTML = '<div class="loading">No verification history found.</div>';
            return;
        }

        historyList.innerHTML = history.map(item => `
            <div class="history-item">
                <div class="history-header">
                    <div class="history-date">
                        <i class="fas fa-clock"></i> ${new Date(item.created_at).toLocaleString()}
                    </div>
                    <div class="history-score">
                        Score: ${(item.authenticity_score * 100).toFixed(1)}%
                    </div>
                    <div class="history-status ${item.is_authentic ? 'authentic' : 'suspicious'}">
                        ${item.is_authentic ? 'Authentic' : 'Suspicious'}
                    </div>
                </div>
                <div class="history-details">
                    <p><strong>Confidence:</strong> ${(item.confidence_level * 100).toFixed(1)}%</p>
                    <p><strong>Processing Time:</strong> ${item.processing_time.toFixed(2)}s</p>
                </div>
            </div>
        `).join('');
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        // Load data for specific tabs
        if (tabName === 'templates') {
            this.loadTemplates();
        } else if (tabName === 'history') {
            this.loadHistory();
        }
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showLoginUI() {
        // Hide main content and show login form
        const mainContent = document.querySelector('.main-content');
        const navTabs = document.querySelector('.nav-tabs');
        
        if (mainContent && navTabs) {
            navTabs.style.display = 'none';
            mainContent.innerHTML = `
                <div class="login-container">
                    <div class="login-form">
                        <h2><i class="fas fa-signature"></i> Signature Recognition System</h2>
                        <p>Please login to continue</p>
                        
                        <div class="login-tabs">
                            <button class="login-tab active" data-login-tab="login">Login</button>
                            <button class="login-tab" data-login-tab="register">Register</button>
                        </div>
                        
                        <div class="login-content">
                            <form id="loginForm" class="auth-form">
                                <div class="form-group">
                                    <label for="loginUsername">Username</label>
                                    <input type="text" id="loginUsername" required>
                                </div>
                                <div class="form-group">
                                    <label for="loginPassword">Password</label>
                                    <input type="password" id="loginPassword" required>
                                </div>
                                <button type="submit" class="btn btn-primary">Login</button>
                            </form>
                            
                            <form id="registerForm" class="auth-form" style="display: none;">
                                <div class="form-group">
                                    <label for="regUsername">Username</label>
                                    <input type="text" id="regUsername" required>
                                </div>
                                <div class="form-group">
                                    <label for="regEmail">Email</label>
                                    <input type="email" id="regEmail" required>
                                </div>
                                <div class="form-group">
                                    <label for="regFullName">Full Name</label>
                                    <input type="text" id="regFullName" required>
                                </div>
                                <div class="form-group">
                                    <label for="regPassword">Password</label>
                                    <input type="password" id="regPassword" required>
                                </div>
                                <button type="submit" class="btn btn-primary">Register</button>
                            </form>
                        </div>
                        
                        <div class="demo-credentials">
                            <h4>Demo Credentials:</h4>
                            <p><strong>Username:</strong> templateuser</p>
                            <p><strong>Password:</strong> password123</p>
                        </div>
                    </div>
                </div>
            `;
            
            this.setupLoginEventListeners();
        }
    }

    showAuthenticatedUI() {
        // Show main content and hide login form
        const mainContent = document.querySelector('.main-content');
        const navTabs = document.querySelector('.nav-tabs');
        
        if (mainContent && navTabs) {
            navTabs.style.display = 'flex';
            mainContent.innerHTML = `
                <div class="tab-content active" id="upload">
                    <div class="upload-section">
                        <div class="upload-area" id="uploadArea">
                            <div class="upload-content">
                                <i class="fas fa-cloud-upload-alt"></i>
                                <h3>Upload Signature Image</h3>
                                <p>Drag and drop your signature image here or click to browse</p>
                                <input type="file" id="fileInput" accept="image/*" hidden>
                                <button class="btn btn-primary" onclick="document.getElementById('fileInput').click()">
                                    Choose File
                                </button>
                            </div>
                        </div>
                        
                        <div class="upload-options">
                            <div class="form-group">
                                <label for="templateName">Save as Template (Optional)</label>
                                <input type="text" id="templateName" placeholder="Enter template name">
                            </div>
                            <button class="btn btn-success" id="analyzeBtn" disabled>
                                <i class="fas fa-search"></i> Analyze Signature
                            </button>
                        </div>
                    </div>

                    <div class="results-section" id="resultsSection" style="display: none;">
                        <h3>Analysis Results</h3>
                        <div class="result-card">
                            <div class="result-header">
                                <div class="authenticity-score">
                                    <span class="score-label">Authenticity Score</span>
                                    <span class="score-value" id="authenticityScore">0.0</span>
                                </div>
                                <div class="confidence-level">
                                    <span class="confidence-label">Confidence</span>
                                    <span class="confidence-value" id="confidenceLevel">0.0</span>
                                </div>
                            </div>
                            <div class="result-status" id="resultStatus">
                                <i class="fas fa-question-circle"></i>
                                <span>Analysis in progress...</span>
                            </div>
                            <div class="result-details" id="resultDetails"></div>
                        </div>
                    </div>
                </div>

                <div class="tab-content" id="verify">
                    <div class="verify-section">
                        <div class="upload-area" id="verifyUploadArea">
                            <div class="upload-content">
                                <i class="fas fa-file-signature"></i>
                                <h3>Upload Signature to Verify</h3>
                                <p>Select a signature image to verify against your templates</p>
                                <input type="file" id="verifyFileInput" accept="image/*" hidden>
                                <button class="btn btn-primary" onclick="document.getElementById('verifyFileInput').click()">
                                    Choose File
                                </button>
                            </div>
                        </div>
                        
                        <div class="template-selection">
                            <div class="form-group">
                                <label for="templateSelect">Select Template</label>
                                <select id="templateSelect">
                                    <option value="">Choose a template...</option>
                                </select>
                            </div>
                            <button class="btn btn-success" id="verifyBtn" disabled>
                                <i class="fas fa-check-double"></i> Verify Signature
                            </button>
                        </div>
                    </div>

                    <div class="verification-results" id="verificationResults" style="display: none;">
                        <h3>Verification Results</h3>
                        <div class="result-card">
                            <div class="result-header">
                                <div class="authenticity-score">
                                    <span class="score-label">Match Score</span>
                                    <span class="score-value" id="matchScore">0.0</span>
                                </div>
                                <div class="confidence-level">
                                    <span class="confidence-label">Confidence</span>
                                    <span class="confidence-value" id="matchConfidence">0.0</span>
                                </div>
                            </div>
                            <div class="result-status" id="verificationStatus">
                                <i class="fas fa-question-circle"></i>
                                <span>Verification in progress...</span>
                            </div>
                            <div class="result-details" id="verificationDetails"></div>
                        </div>
                    </div>
                </div>

                <div class="tab-content" id="templates">
                    <div class="templates-section">
                        <div class="section-header">
                            <h3>My Signature Templates</h3>
                            <button class="btn btn-primary" id="refreshTemplates">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                        </div>
                        <div class="templates-grid" id="templatesGrid">
                            <div class="loading">Loading templates...</div>
                        </div>
                    </div>
                </div>

                <div class="tab-content" id="history">
                    <div class="history-section">
                        <div class="section-header">
                            <h3>Verification History</h3>
                            <button class="btn btn-primary" id="refreshHistory">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                        </div>
                        <div class="history-list" id="historyList">
                            <div class="loading">Loading history...</div>
                        </div>
                    </div>
                </div>
            `;
            
            // Re-setup event listeners for the new UI
            this.setupEventListeners();
        }
    }

    setupLoginEventListeners() {
        // Login/Register tab switching
        document.querySelectorAll('.login-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabType = e.target.dataset.loginTab;
                
                // Update tab appearance
                document.querySelectorAll('.login-tab').forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
                
                // Show/hide forms
                document.getElementById('loginForm').style.display = tabType === 'login' ? 'block' : 'none';
                document.getElementById('registerForm').style.display = tabType === 'register' ? 'block' : 'none';
            });
        });

        // Login form
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            
            const result = await this.auth.login(username, password);
            if (result.success) {
                this.showToast('Login successful!', 'success');
                this.showAuthenticatedUI();
                this.loadTemplates();
                this.loadHistory();
            } else {
                this.showToast(`Login failed: ${result.error}`, 'error');
            }
        });

        // Register form
        document.getElementById('registerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('regUsername').value;
            const email = document.getElementById('regEmail').value;
            const fullName = document.getElementById('regFullName').value;
            const password = document.getElementById('regPassword').value;
            
            const result = await this.auth.register(username, email, password, fullName);
            if (result.success) {
                this.showToast('Registration successful! Please login.', 'success');
                // Switch to login tab
                document.querySelector('[data-login-tab="login"]').click();
            } else {
                this.showToast(`Registration failed: ${result.error}`, 'error');
            }
        });
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SignatureRecognitionApp();
});
