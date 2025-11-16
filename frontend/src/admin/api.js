const API_BASE = 'http://localhost:8000/api'

export async function fetchJobs() {
  const res = await fetch(`${API_BASE}/admin/jobs`)
  if (!res.ok) throw new Error('Failed to fetch jobs')
  return res.json()
}

export async function fetchJob(id) {
  const res = await fetch(`${API_BASE}/admin/jobs/${id}`)
  if (!res.ok) throw new Error('Failed to fetch job')
  return res.json()
}

export async function fetchEla(jobId) {
  const res = await fetch(`${API_BASE}/admin/forgery/ela/${jobId}`)
  if (!res.ok) throw new Error('Failed to fetch ELA')
  // try to return JSON or blob
  const contentType = res.headers.get('content-type') || ''
  if (contentType.includes('image')) {
    const blob = await res.blob()
    return URL.createObjectURL(blob)
  }
  return res.json()
}

export async function reviewJob(id, action, comments) {
  const res = await fetch(`${API_BASE}/admin/jobs/${id}/review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, comments }),
  })
  if (!res.ok) throw new Error('Failed to submit review')
  return res.json()
}

export default { fetchJobs, fetchJob, fetchEla, reviewJob }
