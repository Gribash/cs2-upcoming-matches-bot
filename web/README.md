# CS2 Matches Web (Next.js)

## Run locally

1) Install deps (Node 18+ recommended):

```
npm install
```

2) Configure API base (optional, defaults to http://localhost:8000):

```
export NEXT_PUBLIC_API_BASE=http://localhost:8000
```

3) Start dev server:

```
npm run dev
```

Open http://localhost:3000

- Upcoming: /
- Live: /live
- Recent: /recent

## Notes
- Reads from your local API: GET /api/matches/*
- CORS for localhost is already enabled in backend.
- To build:

```
npm run build && npm start
```
