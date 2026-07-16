# 🐳 Docker Installation & Usage Guide

## Complete Guide for Beginners

This guide will walk you through installing Docker and using it with the Task Management API.

---

## 📋 Table of Contents

1. [What is Docker?](#what-is-docker)
2. [Installation by Operating System](#installation-by-operating-system)
3. [Verify Installation](#verify-installation)
4. [Docker Basics](#docker-basics)
5. [Using Docker with This Project](#using-docker-with-this-project)
6. [Common Issues & Solutions](#common-issues--solutions)

---

## 🤔 What is Docker?

**Docker** is a platform that packages your application and all its dependencies into **containers**.

### Why Use Docker?

✅ **No manual setup** - No need to install Python, Redis, etc.  
✅ **Works everywhere** - Same environment on Mac, Windows, Linux  
✅ **Isolated** - Doesn't mess with your system  
✅ **One command** - Start everything instantly  
✅ **Clean** - Easy to remove when done  

### Think of it like this:
- **Without Docker**: Install Python, Redis, configure everything manually
- **With Docker**: Run one command, everything works

---

## 💻 Installation by Operating System

### 🍎 macOS Installation

#### Step 1: Download Docker Desktop
1. Go to: https://www.docker.com/products/docker-desktop
2. Click **"Download for Mac"**
3. Choose your Mac type:
   - **Apple Silicon (M1/M2/M3)**: Download "Mac with Apple chip"
   - **Intel Mac**: Download "Mac with Intel chip"

#### Step 2: Install Docker Desktop
1. Open the downloaded `.dmg` file
2. Drag **Docker.app** to your **Applications** folder
3. Open **Docker** from Applications
4. Follow the setup wizard:
   - Accept the terms
   - Grant permissions when asked
   - Wait for Docker to start (whale icon in menu bar)

#### Step 3: Verify Installation
```bash
# Open Terminal and run:
docker --version
docker-compose --version

# You should see version numbers like:
# Docker version 24.0.6
# Docker Compose version v2.23.0
```

#### macOS Troubleshooting
- **"Docker Desktop requires macOS 10.15 or later"**: Update your macOS
- **Permission denied**: Run `sudo docker ps` and enter your password
- **Docker not starting**: Restart your Mac

---

### 🪟 Windows Installation

#### Step 1: System Requirements
- **Windows 10/11** (64-bit): Pro, Enterprise, or Education
- **WSL 2** enabled (Windows Subsystem for Linux)

#### Step 2: Enable WSL 2
```powershell
# Open PowerShell as Administrator and run:
wsl --install

# Restart your computer when prompted
```

#### Step 3: Download Docker Desktop
1. Go to: https://www.docker.com/products/docker-desktop
2. Click **"Download for Windows"**
3. Run the installer: `Docker Desktop Installer.exe`

#### Step 4: Install Docker Desktop
1. Double-click the installer
2. Follow the installation wizard:
   - Check "Use WSL 2 instead of Hyper-V"
   - Accept the terms
   - Wait for installation
3. Restart your computer
4. Start Docker Desktop from Start Menu

#### Step 5: Verify Installation
```powershell
# Open PowerShell or Command Prompt and run:
docker --version
docker-compose --version
```

#### Windows Troubleshooting
- **"WSL 2 installation is incomplete"**: 
  ```powershell
  wsl --update
  wsl --set-default-version 2
  ```
- **"Docker Desktop requires Windows 10 Pro"**: 
  - Upgrade to Windows 10/11 Pro, or
  - Use Docker Toolbox (older version)
- **Virtualization not enabled**: 
  - Restart PC → Enter BIOS → Enable VT-x/AMD-V

---

### 🐧 Linux Installation (Ubuntu/Debian)

#### Step 1: Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### Step 2: Install Docker
```bash
# Install prerequisites
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

#### Step 3: Start Docker
```bash
# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Verify it's running
sudo systemctl status docker
```

#### Step 4: Add Your User to Docker Group (Optional)
```bash
# Avoid using 'sudo' for every command
sudo usermod -aG docker $USER

# Log out and log back in for changes to take effect
# Or run:
newgrp docker
```

#### Step 5: Verify Installation
```bash
docker --version
docker compose version  # Note: 'compose' not 'docker-compose'
```

---

## ✅ Verify Installation

### Test Docker is Working

Run this command in your terminal:
```bash
docker run hello-world
```

**Expected output:**
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

If you see this, **Docker is installed correctly!** ✅

---

## 📚 Docker Basics

### Key Concepts

#### 1. **Container**
- A running instance of your application
- Like a lightweight virtual machine
- Isolated from your system

#### 2. **Image**
- A blueprint for containers
- Contains your app and dependencies
- Built from a `Dockerfile`

#### 3. **Docker Compose**
- Tool to run multiple containers
- Defined in `docker-compose.yml`
- Start everything with one command

#### 4. **Volume**
- Persistent storage for containers
- Data survives container restarts
- Like a shared folder

---

### Essential Docker Commands

#### Container Management
```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop a container
docker stop <container-name>

# Start a container
docker start <container-name>

# Remove a container
docker rm <container-name>

# View container logs
docker logs <container-name>
docker logs -f <container-name>  # Follow logs in real-time
```

#### Image Management
```bash
# List images
docker images

# Remove an image
docker rmi <image-name>

# Pull an image from Docker Hub
docker pull redis

# Build an image
docker build -t my-app .
```

#### Docker Compose Commands
```bash
# Start all services
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs
docker-compose logs -f  # Follow logs

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up -d --build

# Stop and remove everything (including volumes)
docker-compose down -v
```

#### Cleanup Commands
```bash
# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a

# See disk usage
docker system df
```

---

## 🚀 Using Docker with This Project

### Step-by-Step Guide

#### 1. Open Terminal/Command Prompt
- **macOS**: Open Terminal (Cmd+Space, type "Terminal")
- **Windows**: Open PowerShell or Command Prompt
- **Linux**: Open your terminal

#### 2. Navigate to Project Directory
```bash
cd /Users/agalca/Downloads/CoursorProject/task-management-api
```

#### 3. Make Sure Docker is Running
- **macOS/Windows**: Check Docker Desktop is running (whale icon in system tray)
- **Linux**: Run `sudo systemctl status docker`

#### 4. Start the Application

**Option A: Automated Script (Recommended)**
```bash
./docker-start.sh
```

**Option B: Manual Start**
```bash
docker-compose up -d
```

#### 5. Verify Everything is Running
```bash
# Check service status
docker-compose ps

# Expected output:
# NAME                      STATUS    PORTS
# task-api-redis           Up        0.0.0.0:6379->6379/tcp
# task-api-flask           Up        0.0.0.0:5003->5003/tcp
# task-api-celery-worker   Up
# task-api-celery-beat     Up
```

#### 6. Test the API
```bash
# Health check
curl http://localhost:5003/api/auth/health

# Or open in browser:
# http://localhost:5003/api/auth/health
```

#### 7. View Logs (Optional)
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f celery-worker
```

#### 8. Stop When Done
```bash
docker-compose down
```

---

## 🎯 Common Workflows

### Development Workflow

```bash
# 1. Start services
docker-compose up -d

# 2. Make code changes in your editor
# Changes are automatically reflected (volume mounted)

# 3. View logs to see changes
docker-compose logs -f api

# 4. Run tests
docker-compose exec api pytest

# 5. Stop when done
docker-compose down
```

### Testing Workflow

```bash
# Start services
docker-compose up -d

# Run all tests
docker-compose exec api pytest

# Run with coverage
docker-compose exec api pytest --cov=app

# Run specific test file
docker-compose exec api pytest tests/test_tasks.py

# Stop services
docker-compose down
```

### Debugging Workflow

```bash
# Start services
docker-compose up -d

# Access container shell
docker-compose exec api bash

# Inside container, you can:
ls                    # List files
python                # Run Python
flask shell           # Flask shell
cat logs/app.log      # View logs

# Exit shell
exit

# View real-time logs
docker-compose logs -f api
```

---

## 🐛 Common Issues & Solutions

### Issue 1: "Cannot connect to Docker daemon"

**Problem**: Docker is not running

**Solution**:
- **macOS/Windows**: Start Docker Desktop application
- **Linux**: `sudo systemctl start docker`

**Verify**:
```bash
docker info
```

---

### Issue 2: "Port is already allocated"

**Problem**: Port 5003 or 6379 is already in use

**Solution**:
```bash
# Option 1: Stop the conflicting service
# Find what's using the port
lsof -i :5003  # macOS/Linux
netstat -ano | findstr :5003  # Windows

# Option 2: Change port in docker-compose.yml
# Edit docker-compose.yml:
services:
  api:
    ports:
      - "5004:5003"  # Use 5004 instead
```

---

### Issue 3: "Permission denied"

**Problem**: Don't have permission to run Docker

**Solution**:

**macOS/Windows**:
```bash
# Run Docker Desktop as administrator
```

**Linux**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker

# Or use sudo
sudo docker-compose up -d
```

---

### Issue 4: "No space left on device"

**Problem**: Docker is using too much disk space

**Solution**:
```bash
# Check disk usage
docker system df

# Clean up
docker system prune -a

# Remove specific items
docker container prune  # Remove stopped containers
docker image prune      # Remove unused images
docker volume prune     # Remove unused volumes
```

---

### Issue 5: "Container keeps restarting"

**Problem**: Service is crashing

**Solution**:
```bash
# Check logs
docker-compose logs api

# Check last 100 lines
docker-compose logs --tail=100 api

# Common causes:
# - Missing environment variables
# - Port conflict
# - Database connection issue
# - Code error

# Try rebuilding
docker-compose down
docker-compose up -d --build
```

---

### Issue 6: "Cannot find docker-compose"

**Problem**: docker-compose not installed or wrong command

**Solution**:

**Modern Docker (v2)**:
```bash
# Use 'docker compose' (space, not hyphen)
docker compose up -d
```

**Older Docker**:
```bash
# Install docker-compose separately
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

---

### Issue 7: "Services not accessible from browser"

**Problem**: Can't access http://localhost:5003

**Solution**:
```bash
# 1. Check services are running
docker-compose ps

# 2. Check if API is healthy
docker-compose logs api

# 3. Try 127.0.0.1 instead of localhost
curl http://127.0.0.1:5003/api/auth/health

# 4. Check firewall settings
# macOS: System Preferences → Security → Firewall
# Windows: Windows Defender Firewall

# 5. Restart Docker Desktop
```

---

## 📖 Learning Resources

### Official Documentation
- **Docker Docs**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **Docker Hub**: https://hub.docker.com/

### Tutorials
- **Docker Getting Started**: https://docs.docker.com/get-started/
- **Docker Compose Tutorial**: https://docs.docker.com/compose/gettingstarted/

### Video Tutorials
- **Docker in 100 Seconds**: https://www.youtube.com/watch?v=Gjnup-PuquQ
- **Docker Tutorial for Beginners**: https://www.youtube.com/watch?v=fqMOX6JJhGo

---

## 🎓 Quick Reference Card

### Installation Check
```bash
docker --version          # Check Docker version
docker-compose --version  # Check Compose version
docker info               # System information
docker run hello-world    # Test installation
```

### This Project
```bash
cd task-management-api    # Navigate to project
./docker-start.sh         # Start everything
docker-compose ps         # Check status
docker-compose logs -f    # View logs
docker-compose down       # Stop everything
```

### Useful Commands
```bash
docker ps                 # Running containers
docker images             # List images
docker-compose restart    # Restart services
docker system prune -a    # Clean up everything
```

### Get Help
```bash
docker --help             # Docker help
docker-compose --help     # Compose help
docker run --help         # Run command help
```

---

## ✅ Installation Checklist

Before using this project, verify:

- [ ] Docker Desktop installed (macOS/Windows) or Docker Engine (Linux)
- [ ] Docker is running (check system tray or `docker info`)
- [ ] Docker Compose is available (`docker-compose --version`)
- [ ] Test command works (`docker run hello-world`)
- [ ] You can access http://localhost after starting
- [ ] No port conflicts (5003, 6379 available)

---

## 🎯 Next Steps

Once Docker is installed:

1. **Navigate to project**:
   ```bash
   cd task-management-api
   ```

2. **Start everything**:
   ```bash
   ./docker-start.sh
   ```

3. **Access the API**:
   - Health: http://localhost:5003/api/auth/health
   - Swagger: http://localhost:5003/apidocs

4. **Read the guides**:
   - `DOCKER_GUIDE.md` - Detailed Docker usage
   - `DOCKER_DEPLOYMENT_READY.md` - Quick reference
   - `PERFORMANCE_OPTIMIZATION.md` - API features

---

## 💡 Tips for Beginners

### Do's ✅
- ✅ Start Docker Desktop before running commands
- ✅ Use `docker-compose down` to stop cleanly
- ✅ Check logs when something doesn't work
- ✅ Use `docker system prune` regularly to free space
- ✅ Read error messages carefully

### Don'ts ❌
- ❌ Don't force quit Docker Desktop
- ❌ Don't delete containers manually (use `docker-compose down`)
- ❌ Don't edit files inside containers (edit locally)
- ❌ Don't run multiple instances on same ports
- ❌ Don't ignore disk space warnings

---

## 🆘 Getting Help

### If You're Stuck

1. **Check logs**:
   ```bash
   docker-compose logs
   ```

2. **Restart everything**:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

3. **Clean and retry**:
   ```bash
   docker-compose down -v
   docker system prune -a
   docker-compose up -d --build
   ```

4. **Check Docker status**:
   ```bash
   docker info
   docker-compose ps
   ```

5. **Search error message** on Google or Stack Overflow

---

## 🎉 You're Ready!

Once Docker is installed, you can:

✅ Start the entire application with one command  
✅ No manual installation of Python, Redis, etc.  
✅ Consistent environment across all systems  
✅ Easy to start, stop, and restart  
✅ Clean removal when done  

**Just run:**
```bash
cd task-management-api
./docker-start.sh
```

**Your API will be live at:** http://localhost:5003 🚀

---

## 📞 Quick Help

**Installation Issues**: Check the troubleshooting section above  
**Usage Questions**: See `DOCKER_GUIDE.md`  
**API Questions**: See `PERFORMANCE_OPTIMIZATION.md`  

**Happy Dockering!** 🐳✨
