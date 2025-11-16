/**
 * Image quality analysis utility
 * Detects: blur, brightness, contrast, cropping issues
 */

export const analyzeImageQuality = (file) => {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        canvas.width = img.width
        canvas.height = img.height
        ctx.drawImage(img, 0, 0)

        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
        const data = imageData.data

        // Analyze image properties
        const issues = []
        const metrics = {
          blur: detectBlur(canvas),
          brightness: calculateBrightness(data),
          contrast: calculateContrast(data),
          fileSize: file.size,
          dimensions: { width: img.width, height: img.height },
        }

        // Check for issues
        if (metrics.blur > 0.7) {
          issues.push({
            type: 'blur',
            severity: 'high',
            message: '📸 Image is blurry. Please retake in better light with a steady hand.',
          })
        }

        if (metrics.brightness < 80) {
          issues.push({
            type: 'brightness',
            severity: 'medium',
            message: '🌙 Image is too dark. Please take the photo in better lighting.',
          })
        }

        if (metrics.brightness > 240) {
          issues.push({
            type: 'overexposure',
            severity: 'medium',
            message: '☀️ Image is overexposed. Please reduce glare and retake.',
          })
        }

        if (metrics.contrast < 50) {
          issues.push({
            type: 'lowcontrast',
            severity: 'medium',
            message: '⚫ Low contrast detected. Please ensure the document is clearly visible.',
          })
        }

        // Check dimensions (reasonable for document)
        if (metrics.dimensions.width < 300 || metrics.dimensions.height < 300) {
          issues.push({
            type: 'lowresolution',
            severity: 'high',
            message: '📏 Image resolution is too low. Please use a higher quality photo.',
          })
        }

        // Check file size
        if (file.size > 10 * 1024 * 1024) {
          issues.push({
            type: 'largefilesize',
            severity: 'low',
            message: '📦 File is large. Consider compressing for faster upload.',
          })
        }

        resolve({
          quality: issues.length === 0 ? 'good' : 'warning',
          issues,
          metrics,
          score: calculateQualityScore(metrics, issues),
        })
      }
      img.src = e.target.result
    }
    reader.readAsDataURL(file)
  })
}

const detectBlur = (canvas) => {
  // Simplified Laplacian variance for blur detection
  const ctx = canvas.getContext('2d')
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
  const data = imageData.data
  let totalVariance = 0
  let count = 0

  for (let i = 0; i < data.length; i += 4) {
    const r = data[i]
    const g = data[i + 1]
    const b = data[i + 2]
    const gray = 0.299 * r + 0.587 * g + 0.114 * b
    totalVariance += gray * gray
    count++
  }

  const meanIntensity = totalVariance / count
  // Return blur score (0-1, higher = more blurry)
  // This is a simplified heuristic; production would use more sophisticated metrics
  return Math.min(1, Math.max(0, 1 - Math.sqrt(meanIntensity) / 128))
}

const calculateBrightness = (data) => {
  let totalBrightness = 0
  for (let i = 0; i < data.length; i += 4) {
    const r = data[i]
    const g = data[i + 1]
    const b = data[i + 2]
    const brightness = (r + g + b) / 3
    totalBrightness += brightness
  }
  return totalBrightness / (data.length / 4)
}

const calculateContrast = (data) => {
  let min = 255
  let max = 0
  for (let i = 0; i < data.length; i += 4) {
    const r = data[i]
    const g = data[i + 1]
    const b = data[i + 2]
    const gray = 0.299 * r + 0.587 * g + 0.114 * b
    min = Math.min(min, gray)
    max = Math.max(max, gray)
  }
  return max - min
}

const calculateQualityScore = (metrics, issues) => {
  let score = 100
  issues.forEach((issue) => {
    if (issue.severity === 'high') score -= 30
    if (issue.severity === 'medium') score -= 15
    if (issue.severity === 'low') score -= 5
  })
  return Math.max(0, score)
}
