// Advanced Signature Scanner and Analysis
class SignatureScanner {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.isDrawing = false;
        this.lastX = 0;
        this.lastY = 0;
        this.strokes = [];
        this.currentStroke = [];
        this.init();
    }

    init() {
        this.createCanvas();
        this.setupEventListeners();
    }

    createCanvas() {
        // Create canvas element
        this.canvas = document.createElement('canvas');
        this.canvas.width = 400;
        this.canvas.height = 200;
        this.canvas.style.border = '2px solid #ddd';
        this.canvas.style.borderRadius = '10px';
        this.canvas.style.cursor = 'crosshair';
        this.canvas.style.backgroundColor = 'white';

        this.ctx = this.canvas.getContext('2d');
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        this.ctx.strokeStyle = '#000';
        this.ctx.lineWidth = 2;

        // Add canvas to upload area if it exists
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea) {
            const canvasContainer = document.createElement('div');
            canvasContainer.className = 'canvas-container';
            canvasContainer.innerHTML = `
                <h4>Or draw your signature:</h4>
                <div class="canvas-wrapper">
                    ${this.canvas.outerHTML}
                </div>
                <div class="canvas-controls">
                    <button class="btn btn-secondary" onclick="signatureScanner.clearCanvas()">
                        <i class="fas fa-eraser"></i> Clear
                    </button>
                    <button class="btn btn-primary" onclick="signatureScanner.saveSignature()">
                        <i class="fas fa-save"></i> Save Signature
                    </button>
                </div>
            `;
            uploadArea.appendChild(canvasContainer);
        }
    }

    setupEventListeners() {
        if (!this.canvas) return;

        // Mouse events
        this.canvas.addEventListener('mousedown', (e) => this.startDrawing(e));
        this.canvas.addEventListener('mousemove', (e) => this.draw(e));
        this.canvas.addEventListener('mouseup', () => this.stopDrawing());
        this.canvas.addEventListener('mouseout', () => this.stopDrawing());

        // Touch events for mobile
        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousedown', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            this.canvas.dispatchEvent(mouseEvent);
        });

        this.canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousemove', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            this.canvas.dispatchEvent(mouseEvent);
        });

        this.canvas.addEventListener('touchend', (e) => {
            e.preventDefault();
            const mouseEvent = new MouseEvent('mouseup', {});
            this.canvas.dispatchEvent(mouseEvent);
        });
    }

    getMousePos(e) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    startDrawing(e) {
        this.isDrawing = true;
        const pos = this.getMousePos(e);
        this.lastX = pos.x;
        this.lastY = pos.y;
        this.currentStroke = [{ x: pos.x, y: pos.y, time: Date.now() }];
    }

    draw(e) {
        if (!this.isDrawing) return;

        const pos = this.getMousePos(e);
        
        this.ctx.beginPath();
        this.ctx.moveTo(this.lastX, this.lastY);
        this.ctx.lineTo(pos.x, pos.y);
        this.ctx.stroke();

        this.currentStroke.push({ x: pos.x, y: pos.y, time: Date.now() });
        this.lastX = pos.x;
        this.lastY = pos.y;
    }

    stopDrawing() {
        if (this.isDrawing) {
            this.isDrawing = false;
            if (this.currentStroke.length > 0) {
                this.strokes.push(this.currentStroke);
                this.currentStroke = [];
            }
        }
    }

    clearCanvas() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.strokes = [];
        this.currentStroke = [];
    }

    saveSignature() {
        if (this.strokes.length === 0) {
            app.showToast('Please draw a signature first', 'error');
            return;
        }

        // Convert canvas to blob
        this.canvas.toBlob((blob) => {
            // Create a file from the blob
            const file = new File([blob], 'signature.png', { type: 'image/png' });
            
            // Set the file input
            const fileInput = document.getElementById('fileInput');
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            
            // Update UI
            app.updateFilePreview(file, 'fileInput');
            app.updateAnalyzeButton();
            
            app.showToast('Signature saved successfully!', 'success');
        }, 'image/png');
    }

    analyzeSignature() {
        if (this.strokes.length === 0) {
            return null;
        }

        const analysis = {
            strokeCount: this.strokes.length,
            totalLength: 0,
            averageSpeed: 0,
            pressureVariation: 0,
            penLifts: this.strokes.length - 1,
            timeSpan: 0
        };

        let totalTime = 0;
        let totalDistance = 0;

        this.strokes.forEach(stroke => {
            if (stroke.length > 1) {
                for (let i = 1; i < stroke.length; i++) {
                    const dx = stroke[i].x - stroke[i-1].x;
                    const dy = stroke[i].y - stroke[i-1].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    const time = stroke[i].time - stroke[i-1].time;
                    
                    totalDistance += distance;
                    totalTime += time;
                }
            }
        });

        analysis.totalLength = totalDistance;
        analysis.averageSpeed = totalTime > 0 ? totalDistance / totalTime : 0;
        analysis.timeSpan = totalTime;

        return analysis;
    }

    getSignatureFeatures() {
        const analysis = this.analyzeSignature();
        if (!analysis) return null;

        // Calculate additional features
        const bounds = this.getSignatureBounds();
        const aspectRatio = bounds.width / bounds.height;
        const density = this.calculateDensity(bounds);

        return {
            ...analysis,
            aspectRatio,
            density,
            bounds,
            complexity: this.calculateComplexity()
        };
    }

    getSignatureBounds() {
        if (this.strokes.length === 0) {
            return { x: 0, y: 0, width: 0, height: 0 };
        }

        let minX = Infinity, minY = Infinity;
        let maxX = -Infinity, maxY = -Infinity;

        this.strokes.forEach(stroke => {
            stroke.forEach(point => {
                minX = Math.min(minX, point.x);
                minY = Math.min(minY, point.y);
                maxX = Math.max(maxX, point.x);
                maxY = Math.max(maxY, point.y);
            });
        });

        return {
            x: minX,
            y: minY,
            width: maxX - minX,
            height: maxY - minY
        };
    }

    calculateDensity(bounds) {
        if (bounds.width === 0 || bounds.height === 0) return 0;
        
        const totalArea = bounds.width * bounds.height;
        const signatureArea = this.calculateSignatureArea();
        return signatureArea / totalArea;
    }

    calculateSignatureArea() {
        // Approximate signature area by counting pixels
        const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        const data = imageData.data;
        let signaturePixels = 0;

        for (let i = 0; i < data.length; i += 4) {
            // Check if pixel is not white (signature pixel)
            if (data[i] < 250 || data[i + 1] < 250 || data[i + 2] < 250) {
                signaturePixels++;
            }
        }

        return signaturePixels;
    }

    calculateComplexity() {
        if (this.strokes.length === 0) return 0;

        let totalCurvature = 0;
        let pointCount = 0;

        this.strokes.forEach(stroke => {
            if (stroke.length >= 3) {
                for (let i = 1; i < stroke.length - 1; i++) {
                    const p1 = stroke[i - 1];
                    const p2 = stroke[i];
                    const p3 = stroke[i + 1];

                    // Calculate curvature using cross product
                    const v1 = { x: p2.x - p1.x, y: p2.y - p1.y };
                    const v2 = { x: p3.x - p2.x, y: p3.y - p2.y };
                    
                    const crossProduct = Math.abs(v1.x * v2.y - v1.y * v2.x);
                    const v1Length = Math.sqrt(v1.x * v1.x + v1.y * v1.y);
                    const v2Length = Math.sqrt(v2.x * v2.x + v2.y * v2.y);
                    
                    if (v1Length > 0 && v2Length > 0) {
                        totalCurvature += crossProduct / (v1Length * v2Length);
                        pointCount++;
                    }
                }
            }
        });

        return pointCount > 0 ? totalCurvature / pointCount : 0;
    }
}

// Initialize signature scanner when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.signatureScanner = new SignatureScanner();
});
