#!/bin/bash

# Test Flask App Directly - Bypass nginx to test the Flask application

echo "🧪 Testing Flask App Directly"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)
INSTALL_DIR="$USER_HOME/rss_aggregator"

if [ ! -d "$INSTALL_DIR" ]; then
    print_error "Installation directory not found: $INSTALL_DIR"
    exit 1
fi

cd "$INSTALL_DIR"

print_status "Testing Python environment..."
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found"
    exit 1
fi

source venv/bin/activate

print_status "Testing Python imports..."
PYTHONPATH="$INSTALL_DIR" python3 -c "
import sys
print(f'Python version: {sys.version}')
print(f'Python path: {sys.path}')

try:
    import flask
    print(f'✓ Flask version: {flask.__version__}')
except ImportError as e:
    print(f'✗ Flask import failed: {e}')
    sys.exit(1)

try:
    from app.main import app
    print('✓ App imports successfully')
except ImportError as e:
    print(f'✗ App import failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from app.models import get_db_connection
    conn = get_db_connection()
    conn.close()
    print('✓ Database connection works')
except Exception as e:
    print(f'✗ Database connection failed: {e}')
    sys.exit(1)

print('✓ All imports successful')
"

if [ $? -ne 0 ]; then
    print_error "Python import test failed"
    exit 1
fi

print_success "Python environment is working"

print_status "Starting Flask in test mode..."
echo "This will start Flask on port 5001 for testing"
echo "Press Ctrl+C to stop"
echo ""

PYTHONPATH="$INSTALL_DIR" python3 -c "
from app.main import app
import sys

if __name__ == '__main__':
    try:
        print('Starting Flask test server on http://localhost:5001')
        print('Press Ctrl+C to stop')
        app.run(host='0.0.0.0', port=5001, debug=True)
    except KeyboardInterrupt:
        print('\nTest server stopped')
    except Exception as e:
        print(f'Error starting Flask: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
"