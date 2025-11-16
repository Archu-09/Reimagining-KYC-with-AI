# Frontend - Reimagining KYC with AI

A modern, responsive React + Vite frontend for the KYC verification system with real-time image quality feedback, progress tracking, and detailed result visualization.

## Features

✨ **Real-time Image Quality Analysis**
- Detects blur, brightness, contrast, and resolution issues
- Provides intelligent guidance ("Please retake in better light")
- Quality score and severity-based feedback

📊 **Progress Tracking**
- Step-by-step progress bar with visual indicators
- Real-time status updates during verification
- Estimated time feedback

⚠️ **Comprehensive Error Handling**
- User-friendly error messages
- Retry functionality
- Network error recovery

📈 **Detailed Result Display**
- Risk score visualization
- Component-wise score breakdown (face match, liveness, validation, OCR)
- Explainability with SHAP-ready output
- Document information display

📱 **Responsive Design**
- Works on desktop, tablet, and mobile
- Touch-friendly file upload
- Accessible UI components

## Setup & Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The dev server will be available at `http://localhost:5173` and automatically proxies `/api` calls to `http://localhost:8000` (backend).

## Backend Integration

Make sure the backend is running on `http://localhost:8000`:
```bash
cd ../backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
src/
├── App.jsx                    # Main application component
├── main.jsx                   # React entry point
├── styles.css                 # Global styles
├── components/
│   └── UI.jsx                # Reusable UI components
└── utils/
    └── imageQuality.js       # Image quality analysis
```

## Component Guide

### `FileUploadBox`
Handles file selection with preview and quality feedback.

### `ImageQualityFeedback`
Displays quality issues with severity and actionable guidance.

### `ProgressBar & LoadingSpinner`
Visual feedback during verification process.

### `ResultCard`
Comprehensive display of verification results with explainability breakdown.

### `ErrorAlert`
User-friendly error messages with retry options.

## Image Quality Thresholds

- **Blur Score**: <0.7 (lower is better)
- **Brightness**: 80-240 (optimal range)
- **Contrast**: >50 (minimum)
- **Resolution**: >300x300 pixels
- **File Size**: <10MB

## Environment Configuration

For production deployment, set the API endpoint:
```javascript
const API_BASE = process.env.VITE_API_URL || '/api'
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Android)

## Accessibility

- ARIA labels on all interactive elements
- Keyboard navigation support
- High contrast mode compatible
- Screen reader friendly
