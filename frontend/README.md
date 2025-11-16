# Frontend (minimal)

This is a tiny Vite + React frontend that posts `id_image` and `selfie` to the backend `POST /api/verify`.

Run locally:

```bash
cd frontend
npm install
npm run dev
```

The dev server proxies requests to the backend root by using the same hostname; in production you should serve the frontend from a CDN or configure CORS/proxying properly.
