# 🐳 Docker Quick Start Card

## 📥 Installation (Choose Your OS)

### 🍎 macOS
1. Download: https://www.docker.com/products/docker-desktop
2. Choose: **Mac with Apple chip** (M1/M2/M3) or **Intel chip**
3. Install: Drag Docker.app to Applications
4. Start: Open Docker from Applications
5. Verify: `docker --version`

### 🪟 Windows
1. Enable WSL 2: `wsl --install` (PowerShell as Admin)
2. Restart computer
3. Download: https://www.docker.com/products/docker-desktop
4. Install: Run `Docker Desktop Installer.exe`
5. Verify: `docker --version`

### 🐧 Linux (Ubuntu/Debian)
```bash
# Quick install script
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```
Verify: `docker --version`

---

## ✅ Test Installation

```bash
docker run hello-world
```
If you see "Hello from Docker!" → ✅ **You're ready!**

---

## 🚀 Run This Project

### Step 1: Navigate to Project
```bash
cd /Users/agalca/Downloads/CoursorProject/task-management-api
```

### Step 2: Start Everything
```bash
./docker-start.sh
```
**OR**
```bash
docker-compose up -d
```

### Step 3: Verify
```bash
# Check services
docker-compose ps

# Test API
curl http://localhost:5003/api/auth/health
```

### Step 4: Access
- **API**: http://localhost:5003
- **Swagger**: http://localhost:5003/apidocs

---

## 📋 Essential Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Restart
docker-compose restart

# Run tests
docker-compose exec api pytest

# Clean up
docker system prune -a
```

---

## 🐛 Common Issues

### "Cannot connect to Docker daemon"
→ Start Docker Desktop

### "Port already in use"
→ Change port in `docker-compose.yml` or stop conflicting service

### "Permission denied"
→ **Linux**: `sudo usermod -aG docker $USER` then logout/login  
→ **Mac/Win**: Run Docker Desktop as admin

### "No space left"
→ `docker system prune -a`

---

## 📚 Full Guides

- **`DOCKER_INSTALLATION_GUIDE.md`** - Complete installation guide
- **`DOCKER_GUIDE.md`** - Detailed Docker usage
- **`DOCKER_DEPLOYMENT_READY.md`** - Quick reference

---

## 🎯 Your Workflow

```bash
# 1. Start
docker-compose up -d

# 2. Code (changes auto-reload)
# Edit files in your IDE

# 3. Test
docker-compose exec api pytest

# 4. View logs
docker-compose logs -f api

# 5. Stop
docker-compose down
```

---

## ✨ That's It!

**One command starts everything:**
```bash
./docker-start.sh
```

**Your API runs at:** http://localhost:5003 🚀
