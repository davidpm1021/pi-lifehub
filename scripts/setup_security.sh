#\!/bin/bash
# Security Setup Script for Pi Life Hub
# Sets up secure environment and credential management

set -e  # Exit on any error

echo "🔐 Pi Life Hub Security Setup"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Project root: $PROJECT_ROOT"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if .env file exists
if [ \! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status "Created .env from .env.example"
        echo
        print_warning "IMPORTANT: You must edit .env with your actual credentials\!"
        echo "Required variables to update:"
        echo "  - GOOGLE_CLIENT_ID"
        echo "  - GOOGLE_CLIENT_SECRET"
        echo "  - SECRET_KEY"
        echo
    else
        print_error ".env.example not found. Cannot create .env file."
        exit 1
    fi
else
    print_status ".env file already exists"
fi

# Create secure directories
echo
echo "Creating secure directories..."

# Token storage directory
TOKEN_DIR="$HOME/.config/lifehub"
mkdir -p "$TOKEN_DIR"
chmod 700 "$TOKEN_DIR"
print_status "Created secure token directory: $TOKEN_DIR"

# Log directory
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
chmod 755 "$LOG_DIR"
print_status "Created log directory: $LOG_DIR"

# Set file permissions
echo
echo "Setting secure file permissions..."

# Make .env readable only by owner
if [ -f ".env" ]; then
    chmod 600 .env
    print_status "Set .env permissions to 600 (owner read/write only)"
fi

# Make credential files secure if they exist
find . -name "*credentials*.json" -exec chmod 600 {} \; 2>/dev/null || true
find . -name "*token*.json" -exec chmod 600 {} \; 2>/dev/null || true
print_status "Secured credential files"

# Make scripts executable
find scripts/ -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
print_status "Made scripts executable"

# Generate secret key if needed
echo
echo "Checking SECRET_KEY..."

if [ -f ".env" ]; then
    if grep -q "SECRET_KEY=your_very_long_random_secret_key_here" .env; then
        print_warning "SECRET_KEY is using default value. Generating secure key..."
        
        # Generate a secure random key
        SECRET_KEY=$(python3 -c "
import secrets
import string
alphabet = string.ascii_letters + string.digits + '\!@#$%^&*'
print(''.join(secrets.choice(alphabet) for _ in range(64)))
")
        
        # Replace the default key in .env
        sed -i "s/SECRET_KEY=your_very_long_random_secret_key_here/SECRET_KEY=$SECRET_KEY/" .env
        print_status "Generated and set secure SECRET_KEY"
    else
        print_status "SECRET_KEY is already configured"
    fi
fi

# Install python-dotenv if not installed
echo
echo "Checking Python dependencies..."

if \! python3 -c "import dotenv" 2>/dev/null; then
    print_warning "python-dotenv not found. Installing..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        pip install python-dotenv
        print_status "Installed python-dotenv in virtual environment"
    else
        print_warning "Virtual environment not found. Please install python-dotenv manually:"
        echo "  pip install python-dotenv"
    fi
else
    print_status "python-dotenv is available"
fi

# Validate configuration
echo
echo "Validating configuration..."

if [ -f "config/env_config.py" ]; then
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        python3 config/env_config.py
    else
        python3 config/env_config.py
    fi
else
    print_warning "env_config.py not found. Skipping validation."
fi

# Git security check
echo
echo "Checking Git security..."

# Check if sensitive files are staged
STAGED_SECRETS=$(git diff --cached --name-only  < /dev/null |  grep -E "\.(env|json)$|credentials|token" || true)
if [ ! -z "$STAGED_SECRETS" ]; then
    print_error "Sensitive files are staged for commit:"
    echo "$STAGED_SECRETS"
    echo
    echo "Unstage them with: git reset HEAD <file>"
fi

# Check if .gitignore is comprehensive
if [ -f ".gitignore" ]; then
    if grep -q "\.env" .gitignore && grep -q "credentials\.json" .gitignore; then
        print_status ".gitignore includes sensitive files"
    else
        print_warning ".gitignore may not be comprehensive enough"
    fi
else
    print_error ".gitignore not found!"
fi

echo
echo "🔐 Security Setup Summary"
echo "========================"
print_status "Secure directories created"
print_status "File permissions configured"
print_status "Environment template ready"

echo
if [ -f ".env" ]; then
    echo "Next steps:"
    echo "1. Edit .env with your actual Google OAuth credentials"
    echo "2. Run: python3 config/env_config.py (to validate)"
    echo "3. Test authentication: python3 complete_auth_secure.py"
    echo "4. Never commit .env or credential files to Git!"
else
    print_error "Please create and configure .env file before proceeding"
fi

echo
print_status "Security setup complete!"
