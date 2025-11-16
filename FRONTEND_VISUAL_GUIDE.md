# Frontend User Flow & Visual Guide

## 📍 User Journey

### Step 1: Initial Load
```
┌─────────────────────────────────────┐
│  🔐 Reimagining KYC with AI         │
│  Fast, secure, and transparent      │
│  identity verification              │
└─────────────────────────────────────┘
         ↓
    Upload form displayed
```

### Step 2: File Selection & Quality Check
```
┌─────────────────────────────────────┐
│ ID Image (Aadhaar/Passport/DL)      │
│ ┌─────────────────────────────────┐ │
│ │  [📸] Click or drag image       │ │
│ │       PNG, JPG, up to 10MB      │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ✓ Image quality is excellent!       │ (green)
│   [or]                              │
│ ⚠ Quality Score: 65/100             │ (yellow)
│   📸 Image is blurry...             │
│   🌙 Image is too dark...           │
│   ☀️ Image is overexposed...        │
│   ⚫ Low contrast detected...        │
└─────────────────────────────────────┘

Same for Selfie image...
```

### Step 3: Pre-Submit Validation
```
┌─────────────────────────────────────┐
│ ✓ Verify Identity                   │ (enabled)
│                                     │
│ Both images selected with good      │ (hint)
│ quality                             │
└─────────────────────────────────────┘
```

### Step 4: Verification in Progress
```
┌─────────────────────────────────────┐
│ Progress Bar:                       │
│ ████████░░░░░░░░░░░░░░░ 30%        │
│                                     │
│ ● 1  ● 2  ● 3  ● 4  ○ 5  ○ 6      │
│                                     │
│        ⟳ Verifying your identity... │
│        (Step 3/6)                   │
│                                     │
│ ✓ Analyzing images                  │
│ ✓ Classifying document              │
│ → Extracting information            │
│ ○ Matching faces                    │
│ ○ Validating document               │
│ ○ Computing risk score              │
└─────────────────────────────────────┘
```

### Step 5a: Success - Results Display
```
┌─────────────────────────────────────┐
│ Verification Complete               │
│                                     │
│     ┌─────────┐      Low Risk       │
│     │   85    │       (green)       │
│     │ Score   │                     │
│     └─────────┘                     │
│                                     │
│ Document Information                │
│ ├─ Type: Aadhaar                    │
│ ├─ Name: John Doe                   │
│ ├─ DOB: 01/01/1990                  │
│ └─ Document No: 1234-5678-9012      │
│                                     │
│ Verification Results                │
│ ├─ Face Match: ✓ Matched (88.3%)   │
│ ├─ Liveness: ✓ Passed              │
│ └─ Aadhaar Format: ✓ Valid         │
│                                     │
│ Score Breakdown (Explainability)    │
│ ├─ Face Match:   [████████░] 40%   │
│ ├─ Liveness:     [████░░░░░] 20%   │
│ ├─ Validation:   [██████░░░] 30%   │
│ └─ OCR:          [██░░░░░░░] 10%   │
│                                     │
│ [Download Report] [Verify Again]    │
└─────────────────────────────────────┘
```

### Step 5b: Error - Error Alert
```
┌─────────────────────────────────────┐
│ ⚠️                                  │
│   Verification Failed               │
│   Network error. Please check your  │
│   connection and try again.         │
│                         [×]         │
│                                     │
│ [Retry]           [Dismiss]         │
└─────────────────────────────────────┘
```

---

## 🎨 Color Scheme

| Element | Color | Usage |
|---------|-------|-------|
| Primary Gradient | #667eea → #764ba2 | Header, buttons, progress |
| Success | #10b981 | Good quality, low risk |
| Warning | #f59e0b | Medium risk, quality issues |
| Error | #dc2626 | High risk, failures |
| Neutral | #6b7280 | Text, secondary UI |
| Background | #f9fafb | Cards, groups |

---

## 📊 Image Quality Feedback Examples

### Good Quality ✓
```
✓ Image quality is excellent!
```

### Blur Issue 📸
```
⚠ Quality Score: 55/100

📸 Image is blurry. Please retake in better
   light with a steady hand. (HIGH severity)
```

### Brightness Issues 🌙 ☀️
```
⚠ Quality Score: 65/100

🌙 Image is too dark. Please take the photo
   in better lighting. (MEDIUM severity)

☀️ Image is overexposed. Please reduce glare
   and retake. (MEDIUM severity)
```

### Multiple Issues ⚫
```
⚠ Quality Score: 40/100

⚫ Low contrast detected. Please ensure the
   document is clearly visible. (MEDIUM severity)

📏 Image resolution is too low. Please use a
   higher quality photo. (HIGH severity)
```

---

## 🖥️ Responsive Layout

### Desktop (>768px)
```
┌─────────────────────────────────────┐
│         HEADER (Full width)         │
├──────────────┬──────────────────────┤
│  ID Image    │  Selfie Image        │
│  Upload      │  Upload              │
│              │                      │
├──────────────┴──────────────────────┤
│  [✓ Verify Identity]                │
└─────────────────────────────────────┘
```

### Tablet (648-768px)
```
┌─────────────────────┐
│   HEADER            │
├─────────────────────┤
│  ID Image Upload    │
│                     │
├─────────────────────┤
│  Selfie Upload      │
│                     │
├─────────────────────┤
│ [✓ Verify Identity] │
└─────────────────────┘
```

### Mobile (<648px)
```
┌──────────────┐
│    HEADER    │
├──────────────┤
│ ID Upload    │
│              │
├──────────────┤
│ Selfie Upload│
│              │
├──────────────┤
│   [Verify]   │
└──────────────┘
```

---

## ⌨️ Keyboard Navigation

- `Tab`: Move focus between inputs and buttons
- `Enter`: Submit form (when focused on Verify button)
- `Space`: Activate buttons
- `Escape`: Dismiss error alerts
- `Shift+Tab`: Move focus backward

---

## 🎬 Animation Timeline

### Loading Progress (4.8 seconds total)
```
0s:   Step 1 (Analyzing images)
0.8s: Step 2 (Classifying document)
1.6s: Step 3 (Extracting information)
2.4s: Step 4 (Matching faces)
3.2s: Step 5 (Validating document)
4.0s: Step 6 (Computing risk score)
4.8s: Results displayed
```

### Spinner Animation
- Duration: 1s per rotation
- Infinite loop during loading
- Color: Gradient purple/violet

### Progress Bar
- Smooth width transition: 0.5s
- Linear easing
- Color: Gradient matching header

---

## 📱 Touch Interactions

| Action | Feedback |
|--------|----------|
| Tap file area | Highlight border, show file picker |
| Tap button | Color darken, slight scale-down |
| Long press (2s) | Haptic feedback (mobile) |
| Swipe (future) | Dismiss error alerts |

---

## ♿ Accessibility Features

| Feature | Implementation |
|---------|-----------------|
| Screen Reader | Semantic HTML, ARIA labels |
| Keyboard Nav | Full keyboard support |
| Focus Indicators | Visible outline on all interactive |
| Color Contrast | WCAG AA compliant |
| Text Size | Min 16px on mobile |
| Skip Links | Direct to main content |

---

## 🔄 State Management Flow

```
Initial State
├─ idFile: null, selfieFile: null
├─ result: null, error: null
└─ loading: false

↓

User Selects Files
├─ idFile: File object
├─ idQuality: analyzed
├─ canSubmit(): checks quality
└─ Button enabled/disabled

↓

Submit Form
├─ loading: true
├─ error: null
├─ currentStep: 0
└─ Simulate progress loop

↓

API Response Success
├─ loading: false
├─ result: data
├─ error: null
└─ Display ResultCard

or

API Response Error
├─ loading: false
├─ result: null
├─ error: message
└─ Display ErrorAlert
```

---

## 📋 Data Flow

```
User Input
    ↓
File Validation
    ├─ Type check
    ├─ Size check
    └─ Preview generation
    ↓
Image Quality Analysis
    ├─ Canvas analysis
    ├─ Blur detection
    ├─ Brightness calc
    ├─ Contrast calc
    └─ Quality score
    ↓
Real-time Feedback
    ├─ Quality score
    ├─ Issues list
    └─ Enable/disable submit
    ↓
Form Submission
    ├─ FormData creation
    ├─ Progress simulation
    ├─ API POST /api/verify
    └─ Wait for response
    ↓
Response Handling
    ├─ Success → ResultCard
    ├─ Error → ErrorAlert
    └─ Network error → Retry
```

---

This visual guide helps understand the complete user experience! 🎉
