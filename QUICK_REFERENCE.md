# Quick Reference Guide

## 🚀 Quick Start (5 minutes)

### 1. Start Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at: `http://localhost:8000`
API endpoint: `POST http://localhost:8000/api/verify`

### 2. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`
Automatically proxies `/api` to backend

### 3. Open Browser
- Frontend: `http://localhost:5173`
- Backend API Docs: `http://localhost:8000/docs`
- Backend Redoc: `http://localhost:8000/redoc`

---

## 📁 Key Files Quick Reference

### Backend

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app entry point |
| `backend/app/routes/verify.py` | `/api/verify` endpoint |
| `backend/app/services/classifier.py` | Document classifier |
| `backend/app/services/ocr_service.py` | OCR extraction |
| `backend/app/services/face_service.py` | FaceNet face matching |
| `backend/app/services/validators.py` | Aadhaar/MRZ validators |
| `backend/app/services/scoring.py` | Risk scoring |
| `backend/tests/test_validators.py` | 14 unit tests |

### Frontend

| File | Purpose |
|------|---------|
| `frontend/src/App.jsx` | Main app component |
| `frontend/src/components/UI.jsx` | Reusable components |
| `frontend/src/utils/imageQuality.js` | Image analysis |
| `frontend/src/styles.css` | Global styling |
| `frontend/vite.config.js` | Vite config |

---

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
pip install pytest
python -m pytest tests/ -v                          # All tests
python -m pytest tests/test_validators.py -v       # Validators only
python -m pytest tests/test_face_smoke.py -v       # Face tests
```

### Expected Results
```
tests/test_validators.py::TestVerhoeff::... PASSED
tests/test_validators.py::TestAadhaarChecksum::... PASSED
tests/test_validators.py::TestMRZValidate::... PASSED
================================ 14 passed in 0.04s ===
```

---

## 📊 API Reference

### Verify Endpoint

**Request:**
```http
POST /api/verify
Content-Type: multipart/form-data

id_image: <image file>
selfie: <image file>
```

**Response (Success):**
```json
{
  "document_type": "aadhaar",
  "extracted_fields": {
    "name": "John Doe",
    "dob": "01/01/1990",
    "document_number": "1234-5678-9012",
    "address": "...",
    "raw_text": "..."
  },
  "face_match": {
    "similarity": 0.88,
    "match": true,
    "method": "facenet"
  },
  "liveness": {
    "liveness_score": 0.95,
    "passed": true,
    "method": "placeholder"
  },
  "validations": {
    "aadhaar_format_ok": true,
    "qr_found": false,
    "hologram_detected": false
  },
  "score": 85.5,
  "risk_level": "Low",
  "explainability": {
    "face_component": 40.0,
    "liveness_component": 20.0,
    "validation_component": 30.0,
    "ocr_component": 10.0
  }
}
```

**Response (Error):**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## 🎨 UI Components Usage

### FileUploadBox
```jsx
<FileUploadBox
  label="ID Image"
  onFileSelect={(e) => handleSelect(e, 'id')}
  error={errors.id}
  preview={preview}
  quality={quality}
/>
```

### ResultCard
```jsx
<ResultCard result={verificationResult} />
```

### LoadingSpinner
```jsx
<LoadingSpinner step={3} totalSteps={6} />
```

### ProgressBar
```jsx
<ProgressBar step={3} totalSteps={6} />
```

### ErrorAlert
```jsx
<ErrorAlert
  error="Network error"
  onRetry={() => submit()}
  onDismiss={() => setError(null)}
/>
```

---

## 🔍 Image Quality Analysis

### Thresholds
- Blur: < 0.7 (lower is better)
- Brightness: 80-240 (optimal)
- Contrast: > 50 (minimum)
- Resolution: > 300×300px
- File size: < 10MB

### Example Quality Result
```javascript
{
  quality: 'good',           // or 'warning'
  score: 85,                 // 0-100
  issues: [],                // Array of issues
  metrics: {
    blur: 0.3,
    brightness: 150,
    contrast: 80,
    fileSize: 1048576,
    dimensions: {width: 1080, height: 1920}
  }
}
```

---

## 🔐 Security Notes

### What's Implemented
- ✅ File type validation
- ✅ File size limits (10MB)
- ✅ CORS enabled
- ✅ Input validation

### What's TODO
- ❌ AES-256 encryption at rest
- ❌ RBAC/JWT authentication
- ❌ Rate limiting
- ❌ Audit logging
- ❌ HTTPS/TLS (production)

---

## 📱 Responsive Breakpoints

```css
Desktop:  > 768px   /* 2-column layout */
Tablet:   648-768px /* 1-column layout */
Mobile:   < 648px   /* Stacked layout */
```

---

## 🐳 Docker Commands

### Build & Run
```bash
docker compose up --build
```

### Stop
```bash
docker compose down
```

### View Logs
```bash
docker compose logs -f backend
docker compose logs -f postgres
```

### Access Services
```bash
Backend:  http://localhost:8000
Frontend: http://localhost:3000
Postgres: localhost:5432
```

---

## 📚 Documentation Files

| File | Content |
|------|---------|
| `PROJECT_STATUS.md` | Overall project progress (65%) |
| `FRONTEND_IMPLEMENTATION.md` | Complete frontend feature docs |
| `FRONTEND_VISUAL_GUIDE.md` | User flow and visual guide |
| `FRONTEND_CHECKLIST.md` | Implementation checklist |
| `FRONTEND_FEATURES.md` | Frontend setup guide |
| `backend/README.md` | Backend setup guide |

---

## 🆘 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Clear cache
rm -rf backend/__pycache__
rm -rf backend/.pytest_cache

# Reinstall dependencies
pip install -r backend/requirements.txt --force-reinstall
```

### Frontend won't start
```bash
# Clear node modules
rm -rf frontend/node_modules package-lock.json

# Reinstall
npm install

# Check Node version
node --version  # Should be 16+
```

### API calls failing
```bash
# Check backend is running
curl http://localhost:8000

# Check CORS headers
curl -i http://localhost:8000/api/verify

# Check proxy config in vite.config.js
```

---

## 📞 Support

### Common Issues

**Q: "Cannot POST /api/verify"**
- A: Backend not running. Start with `python -m uvicorn app.main:app --reload`

**Q: "CORS error"**
- A: Check backend CORS middleware in `app/main.py`

**Q: "Image quality analysis slow"**
- A: First run loads model, subsequent runs are faster. Normal behavior.

**Q: "Face detection returns no match"**
- A: Check image quality. Ensure faces are clearly visible and well-lit.

**Q: "Module not found errors"**
- A: Run `pip install -r requirements.txt` or `npm install`

---

## 🎯 Next Features to Implement

### High Priority
1. OpenSanctions API integration (compliance)
2. AES-256 encryption (security)
3. SHAP explainability (transparency)
4. Audit logging (compliance)

### Medium Priority
5. Error Level Analysis (fraud detection)
6. S3 integration (storage)
7. Authentication/RBAC
8. Rate limiting

### Low Priority
9. Kubernetes deployment
10. CI/CD pipeline
11. Analytics integration
12. Multi-language support

---

## 📊 Performance Tips

### Frontend
- Image quality analysis runs in parallel
- Progress animation doesn't block API call
- Lazy loading for components
- CSS minified in production

### Backend
- Database queries indexed
- Async/await for I/O operations
- Model caching for classification
- Batch processing ready

---

## ✅ Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrated (if schema changed)
- [ ] SSL/TLS certificate installed
- [ ] API keys for external services
- [ ] Logging configured
- [ ] Error tracking enabled
- [ ] CDN configured (frontend)
- [ ] Monitoring alerts set up
- [ ] Backup strategy in place
- [ ] Security audit completed

---

## 🎉 You're All Set!

The KYC system is ready for use. Start with the **Quick Start** section above to get running in 5 minutes!

Questions? Check the documentation files or the README in each directory.

Happy verifying! 🚀
