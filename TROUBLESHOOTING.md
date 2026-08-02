# LifeOS Troubleshooting

## Quick checks

| Symptom | Try this |
|---------|----------|
| Browser: "This site can't be reached" | Containers not running. Run `Start LifeOS.bat` or `docker compose up -d` |
| Port already in use | Close other apps on 5173/8000, or `docker compose down` then start again |
| Docker Desktop not running | Open Docker Desktop, wait for "Engine running", then retry |
| First start is very slow | Normal – downloads AI models (~1 GB). Only happens once |
| Backend health never becomes OK | `docker compose logs backend` – share the last 30 lines if stuck |

## Common commands

```powershell
cd C:\Users\Christian\lifeos-app   # or your folder name

# Status
docker compose ps

# Logs
docker compose logs backend
docker compose logs frontend

# Stop
docker compose down

# Full reset (deletes containers + data volume)
docker compose down -v

# Rebuild from scratch
docker compose up --build
```

## Update fails

1. Open Docker Desktop first
2. Double-click **Update LifeOS.bat**
3. If git pull fails: check internet, then `git pull origin main` manually
4. If compose fails: run `docker compose up --build` to see full error

## Still stuck?

Copy the **red error text** from PowerShell and the output of:

```powershell
docker compose ps
docker compose logs --tail 50
```
