# FastAPI Base Project Ansible Deployment

This directory contains the Ansible automation for deploying the FastAPI Base Project application using enterprise-grade deployment practices.

## Overview

The Ansible deployment system provides:

- **Zero-downtime deployments** with automatic backup and rollback
- **Multi-environment support** (production, staging)
- **Health monitoring** and verification
- **Docker-based containerized deployment**
- **GitHub Actions integration** for CI/CD automation

## 🎉 Recent Updates

**✅ Sudo Password Issue Fix**: The deployment system now properly handles sudo/privilege escalation requirements with support for passwordless sudo configuration.

## Quick Start

### Prerequisites

1. **Ansible installed** (version 2.9+)
2. **Target server access** via SSH with deployment user
3. **Passwordless sudo configured** on target server (recommended)
4. **GitHub Container Registry access** for image pulls

### Server Setup (First Time)

Before running deployments, set up your server with proper sudo configuration:

```bash
# Run the server setup playbook (requires initial root/sudo access)
ansible-playbook -i inventory/production.yml scripts/setup-server.yml --ask-become-pass

# Or for staging
ansible-playbook -i inventory/staging.yml scripts/setup-server.yml --ask-become-pass
```

This will:

- Configure passwordless sudo for the deployment user
- Set up firewall rules
- Install essential packages
- Create deployment directories
- Configure security (fail2ban)

### Deployment

```bash
# Production deployment
ansible-playbook -i inventory/production.yml playbooks/deploy.yml \
  -e "target_environment=production" \
  -e "app_version=v1.0.0"

# Staging deployment
ansible-playbook -i inventory/staging.yml playbooks/deploy.yml \
  -e "target_environment=staging" \
  -e "app_version=v1.0.0-beta.1"
```

## Sudo/Privilege Escalation Configuration

### Production Setup (Recommended)

Configure passwordless sudo on your server:

```bash
# On the target server, create sudoers file for deployment user
echo "your-deploy-user ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/your-deploy-user
sudo chmod 440 /etc/sudoers.d/your-deploy-user
```

### Alternative: Prompted Sudo

If you prefer prompted sudo, you can run deployments with `--ask-become-pass`:

```bash
ansible-playbook -i inventory/production.yml playbooks/deploy.yml \
  -e "target_environment=production" \
  -e "app_version=v1.0.0" \
  --ask-become-pass
```

### Why Sudo is Required

The deployment process needs sudo privileges for:

- **Docker installation and management**
- **System service control** (starting/stopping services)
- **User management** (adding deployment user to docker group)
- **File permissions** (setting proper ownership and permissions)

## Structure

```
ansible/
├── ansible.cfg              # Ansible configuration
├── inventory/               # Server inventories
│   ├── production.yml       # Production servers
│   ├── staging.yml          # Staging servers
│   └── dynamic.yml          # Runtime-generated inventory
├── group_vars/              # Environment variables
│   ├── all.yml             # Common variables
│   ├── production.yml      # Production settings
│   └── staging.yml         # Staging settings
├── roles/                   # Ansible roles
│   ├── docker/             # Docker installation
│   ├── app-deploy/         # Application deployment
│   ├── health-check/       # Health verification
│   └── rollback/           # Rollback procedures
├── playbooks/               # Main playbooks
│   ├── deploy.yml          # Main deployment
│   ├── rollback.yml        # Manual rollback
│   └── health-check.yml    # Health verification
└── templates/               # Configuration templates
    └── .env.j2             # Environment file template
```

## Prerequisites

### Local Requirements

- **Ansible 2.9+**
- **Python 3.8+**
- **Docker Python library**: `pip install docker`

### Server Requirements

- **Ubuntu 20.04+ / Debian 11+**
- **SSH access** with sudo privileges
- **Python 3** installed on target servers

### GitHub Secrets

Configure the following secrets in your GitHub repository:

#### Connection Secrets

```yaml
DEPLOY_HOST          # Server hostname/IP
DEPLOY_USER          # SSH username
DEPLOY_SSH_PORT      # SSH port (optional, defaults to 22)
DEPLOY_SSH_KEY       # SSH private key
```

#### Application Secrets

```yaml
# Project Configuration
COMPOSE_PROJECT_NAME # Docker Compose project name
APP__NAME           # Application name
APP__TIMEZONE       # Application timezone
APP__PORT           # Application port
APP__CORS_ORIGINS   # CORS origins

# Database Configuration
POSTGRES__USER      # PostgreSQL username
POSTGRES__PASSWORD  # PostgreSQL password
POSTGRES__DB        # PostgreSQL database name
POSTGRES__HOST      # PostgreSQL host (optional)
POSTGRES__PORT      # PostgreSQL port (optional)

# RabbitMQ Configuration
RABBITMQ__USER      # RabbitMQ username
RABBITMQ__PASS      # RabbitMQ password

# Monitoring
SENTRY__DSN         # Sentry DSN (optional)

# PgAdmin Configuration
PGADMIN__EMAIL      # PgAdmin email
PGADMIN__PASSWORD   # PgAdmin password

# API Configuration
API__CONCURRENCY    # API worker count (optional)
```

## Usage

### GitHub Actions Deployment

The deployment is automatically triggered through GitHub Actions:

1. **Manual Deployment**:

   ```yaml
   # Trigger via GitHub Actions UI
   - Choose environment (production/staging)
   - Specify version (e.g., v1.2.3)
   - Optional: Skip health checks
   - Optional: Force deployment
   ```

2. **Automatic Deployment**:
   - Triggered after successful production releases
   - Uses the release tag as version

### Manual Deployment

For manual deployment using Ansible directly:

```bash
# Navigate to ansible directory
cd ansible

# Deploy to production
ansible-playbook \
  -i inventory/production.yml \
  -e "app_version=v1.2.3" \
  playbooks/deploy.yml

# Deploy to staging
ansible-playbook \
  -i inventory/staging.yml \
  -e "app_version=v1.2.3" \
  playbooks/deploy.yml

# Skip health checks
ansible-playbook \
  -i inventory/production.yml \
  -e "app_version=v1.2.3" \
  -e "health_check_skip=true" \
  playbooks/deploy.yml
```

### Health Check

Verify deployment health:

```bash
# Check production health
ansible-playbook \
  -i inventory/production.yml \
  playbooks/health-check.yml

# Check staging health
ansible-playbook \
  -i inventory/staging.yml \
  playbooks/health-check.yml
```

### Rollback

Perform manual rollback:

```bash
# Rollback production (interactive)
ansible-playbook \
  -i inventory/production.yml \
  playbooks/rollback.yml

# Force rollback (non-interactive)
ansible-playbook \
  -i inventory/production.yml \
  -e "ANSIBLE_FORCE_ROLLBACK=true" \
  playbooks/rollback.yml
```

## Roles

### Docker Role

Installs and configures Docker and Docker Compose:

- Adds Docker repository
- Installs Docker CE and Docker Compose
- Configures user permissions
- Verifies installation

### App Deploy Role

Handles application deployment:

- Creates deployment directories
- Generates environment configuration
- Manages Docker login to GitHub Container Registry
- Creates backups before deployment
- Pulls Docker images with retry logic
- Deploys services with zero-downtime strategy

### Health Check Role

Verifies deployment health:

- Waits for containers to start
- Monitors health check status
- Checks for failed/unhealthy containers
- Tests API endpoints
- Provides comprehensive status reporting

### Rollback Role

Handles deployment rollbacks:

- Finds most recent backup
- Stops failed deployment
- Restores previous configuration
- Starts rollback deployment
- Verifies rollback success

## Configuration

### Environment Variables

All configuration is managed through environment variables that map to Ansible variables:

```yaml
# In group_vars/production.yml
environment: production
app_port: "{{ lookup('env', 'APP__PORT') | default('8000') }}"
postgres_user: "{{ lookup('env', 'POSTGRES__USER') }}"
# ... other variables
```

### Inventory Management

Inventories define target servers and environment-specific variables:

```yaml
# inventory/production.yml
all:
  children:
    production:
      hosts:
        host-prod:
          ansible_host: '{{ deploy_host }}'
          ansible_user: '{{ deploy_user }}'
          # ... connection details
      vars:
        environment: production
        # ... environment variables
```

### Templates

Jinja2 templates generate configuration files:

```jinja2
# templates/.env.j2
APP__VERSION={{ app_version }}
POSTGRES__USER={{ postgres_user }}
POSTGRES__PASSWORD={{ postgres_password }}
# ... other environment variables
```

## Features

### Zero-Downtime Deployment

1. **Backup Creation**: Current deployment backed up automatically
2. **Image Pulling**: New Docker images pulled with retry logic
3. **Rolling Update**: Services updated with minimal downtime
4. **Health Verification**: Comprehensive health checks before completion

### Automatic Rollback

1. **Failure Detection**: Automatic detection of deployment failures
2. **Backup Restoration**: Previous configuration restored automatically
3. **Service Recovery**: Previous version restarted and verified
4. **Status Reporting**: Complete rollback status and summary

### Health Monitoring

1. **Container Status**: Monitor container startup and health
2. **API Testing**: Verify API endpoints are responding
3. **Service Dependencies**: Check database and cache connectivity
4. **Comprehensive Reporting**: Detailed health status summary

### Security

1. **SSH Key Management**: Secure SSH key handling
2. **Secret Protection**: Environment variables marked as no_log
3. **Container Registry**: Secure login to GitHub Container Registry
4. **File Permissions**: Proper file permissions for sensitive files

## Troubleshooting

### Common Issues

1. **SSH Connection Failed**:

   ```bash
   # Test SSH connection manually
   ssh -i ~/.ssh/deploy_key user@server

   # Check SSH key permissions
   chmod 600 ~/.ssh/deploy_key
   ```

2. **Docker Login Failed**:

   ```bash
   # Verify GitHub token has registry permissions
   # Check if GITHUB_TOKEN secret is properly set
   ```

3. **Health Check Timeout**:

   ```bash
   # Check service logs
   ansible all -i inventory/production.yml -a "docker-compose logs"

   # Verify port accessibility
   ansible all -i inventory/production.yml -a "netstat -tlnp | grep 8000"
   ```

4. **Rollback Failed**:

   ```bash
   # Check available backups
   ansible all -i inventory/production.yml -a "ls -la ~/deployments/fastapi-base-project/backup-*"

   # Manual rollback
   ansible all -i inventory/production.yml -a "cd ~/deployments/fastapi-base-project && docker-compose down"
   ```

### Debug Mode

Enable verbose output for troubleshooting:

```bash
# Run with maximum verbosity
ansible-playbook -vvv -i inventory/production.yml playbooks/deploy.yml

# Check specific tasks
ansible-playbook --start-at-task="Deploy services" -i inventory/production.yml playbooks/deploy.yml
```

### Log Files

Check deployment logs on the server:

```bash
# Deployment log
tail -f ~/deployments/fastapi-base-project/deployment.log

# Docker Compose logs
cd ~/deployments/fastapi-base-project && docker-compose logs -f

# Service-specific logs
cd ~/deployments/fastapi-base-project && docker-compose logs -f api
```

## Best Practices

1. **Testing**: Always test deployments in staging before production
2. **Backups**: Verify backups are created before each deployment
3. **Monitoring**: Monitor health checks and service status
4. **Rollback Plan**: Have a rollback strategy ready
5. **Documentation**: Keep deployment procedures documented
6. **Security**: Regularly rotate SSH keys and secrets

## Debug Mode

For local debugging and development of Ansible playbooks:

### Prerequisites

1. **Install python-dotenv**:

   ```bash
   pip install python-dotenv
   ```

2. **Create environment file**:
   Create a `.env` file in the ansible directory with the following template:

   ```bash
   # Connection variables
   DEPLOY_HOST=your-server-ip
   DEPLOY_USER=your-username
   DEPLOY_SSH_PORT=22
   DEPLOY_SSH_KEY_FILE=~/.ssh/id_rsa

   GITHUB_ACTOR=your-github-username
   GITHUB_REPOSITORY=your-repo/fastapi-base-project
   TARGET_ENVIRONMENT=staging
   health_check_skip=false

   # Application Configuration
   COMPOSE_PROJECT_NAME=fastapi-base-project
   APP__NAME=fastapi-base-project
   APP__VERSION=v0.0.1-beta.1
   APP__TIMEZONE=Asia/Ho_Chi_Minh
   APP__PORT=11111
   APP__CORS_ORIGINS=http://localhost,http://localhost:3000,http://localhost:5173
   APP__BASIC_AUTH=admin:$$2y$$05$$kSD2hpolZf0isSgIS6Pte.X3MSlf.kgnfPf4De1IA2VgUahLKue6u

   # API Configuration
   API__CONCURRENCY=1

   # Database Configuration
   POSTGRES__USER=postgres_user
   POSTGRES__PASSWORD=postgres_password
   POSTGRES__DB=app
   POSTGRES__HOST=pgbouncer
   POSTGRES__PORT=5432

   # PgAdmin Configuration
   PGADMIN__EMAIL=admin@gmail.com
   PGADMIN__PASSWORD=admin

   # RabbitMQ Configuration
   RABBITMQ__USER=admin
   RABBITMQ__PASS=mypass

   # GitHub Token for container registry
   GITHUB_TOKEN=your-github-token
   ```

### Debug Deployment

Run deployment with verbose output and environment variables:

```bash
dotenv run -- ansible-playbook -vv \
  -i inventory/staging.yml \
  -i inventory/runtime.yml \
  -e "target_environment=staging" \
  -e "deployment_id=deploy-$(date +%Y%m%d-%H%M%S)" \
  -e "health_check_skip=false" \
  -e "app_environment=staging" \
  playbooks/deploy.yml
```

### Debug Options

- **-vv**: Verbose output for debugging
- **-vvv**: Maximum verbosity
- **--check**: Dry run mode (no changes made)
- **--diff**: Show file differences
- **--start-at-task**: Start from specific task

Example with additional debug options:

```bash
dotenv run -- ansible-playbook -vvv --check --diff \
  -i inventory/staging.yml \
  -i inventory/runtime.yml \
  -e "target_environment=staging" \
  -e "deployment_id=debug-$(date +%Y%m%d-%H%M%S)" \
  playbooks/deploy.yml
```

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review deployment logs on the server
3. Verify GitHub Actions workflow logs
4. Check service health status
5. Use the debug mode for local testing
6. Contact the development team
