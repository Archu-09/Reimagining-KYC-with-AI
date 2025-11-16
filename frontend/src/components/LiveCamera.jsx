import React, { useRef, useState } from 'react'

export function LiveCamera({ onCapture, onCancel }) {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const [cameraActive, setCameraActive] = useState(false)
  const [error, setError] = useState(null)

  const startCamera = async () => {
    try {
      setError(null)
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user' },
        audio: false,
      })

      if (videoRef.current) {
        videoRef.current.srcObject = stream
        videoRef.current.muted = true
        videoRef.current.playsInline = true
        await videoRef.current.play()
        setCameraActive(true)
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err)
      setError(`Camera error: ${msg}`)
      setCameraActive(false)
    }
  }

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks()
      tracks.forEach((track) => track.stop())
    }
    setCameraActive(false)
  }

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const context = canvasRef.current.getContext('2d')
      canvasRef.current.width = videoRef.current.videoWidth
      canvasRef.current.height = videoRef.current.videoHeight

      // Flip horizontally for selfie (mirror effect)
      context.scale(-1, 1)
      context.drawImage(videoRef.current, -canvasRef.current.width, 0)

      // Convert to blob and pass back
      canvasRef.current.toBlob((blob) => {
        const file = new File([blob], 'selfie.jpg', { type: 'image/jpeg' })
        // Send attestation with a simple "captured" flag (no challenges for now)
        const attestation = { method: 'simple_capture', timestamp: Date.now(), passed: true }
        onCapture(file, attestation)
        stopCamera()
      }, 'image/jpeg', 0.95)
    }
  }

  const handleCancel = () => {
    stopCamera()
    onCancel()
  }

  return (
    <div className="live-camera-modal">
      <div className="live-camera-content">
        <h2>📷 Take a Selfie</h2>
        <p className="live-camera-hint">
          Position your face clearly in the frame and ensure good lighting.
        </p>

        {error && <div className="error-message">{error}</div>}

        {!cameraActive ? (
          <button onClick={startCamera} className="btn btn-primary">
            🎥 Start Camera
          </button>
        ) : (
          <>
            <div className="camera-container">
              <video ref={videoRef} autoPlay muted playsInline className="live-video-feed" />
              <canvas ref={canvasRef} style={{ display: 'none' }} />
            </div>

            <div className="camera-buttons">
              <button onClick={capturePhoto} className="btn btn-success">
                📸 Capture Selfie
              </button>
              <button onClick={handleCancel} className="btn btn-secondary">
                ✕ Cancel
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
