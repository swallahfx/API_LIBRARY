# ============================================================================
# deploy.sh - Deployment Script
# ============================================================================

# Create: deploy.sh
#!/bin/bash

# AI Knowledge Library - Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="AI Knowledge Library"
COMPOSE_FILE="docker-compose.yml"
HEALTH_CHECK_URL="http://localhost:8000/health/"
MAX_RETRIES=30
RETRY_INTERVAL=10

echo -e "${BLUE}🚀 Deploying ${PROJECT_NAME}...${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_info "Please edit .env file with your configuration before continuing."
            read -p "Press Enter to continue after editing .env file..."
        else
            print_error ".env.example file not found. Please create .env file manually."
            exit 1
        fi
    fi
    
    print_status "Prerequisites check completed"
}

# Stop existing containers
stop_existing() {
    print_info "Stopping existing containers..."
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans || true
    print_status "Existing containers stopped"
}

# Build and start containers
start_containers() {
    print_info "Building and starting containers..."
    docker-compose -f "$COMPOSE_FILE" build
    docker-compose -f "$COMPOSE_FILE" up -d
    print_status "Containers started"
}

# Wait for services to be ready
wait_for_services() {
    print_info "Waiting for services to be ready..."
    
    local retries=0
    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -f "$HEALTH_CHECK_URL" >/dev/null 2>&1; then
            print_status "Services are ready!"
            return 0
        fi
        
        retries=$((retries + 1))
        print_info "Attempt $retries/$MAX_RETRIES - Services not ready yet, waiting ${RETRY_INTERVAL}s..."
        sleep $RETRY_INTERVAL
    done
    
    print_error "Services failed to start within expected time"
    return 1
}

# Run health checks
run_health_checks() {
    print_info "Running health checks..."
    
    # API health check
    if curl -f "$HEALTH_CHECK_URL" >/dev/null 2>&1; then
        print_status "API health check passed"
    else
        print_error "API health check failed"
        return 1
    fi
    
    # MongoDB health check
    if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
        print_status "MongoDB health check passed"
    else
        print_error "MongoDB health check failed"
        return 1
    fi
    
    # Redis health check
    if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
        print_status "Redis health check passed"
    else
        print_error "Redis health check failed"
        return 1
    fi
    
    print_status "All health checks passed"
}

# Initialize database
initialize_database() {
    print_info "Initializing database..."
    
    # Wait a bit more for MongoDB to be fully ready
    sleep 10
    
    if docker-compose exec -T api python scripts/init_db.py; then
        print_status "Database initialized successfully"
    else
        print_warning "Database initialization failed or already initialized"
    fi
}

# Load sample data
load_sample_data() {
    print_info "Loading sample data..."
    
    if docker-compose exec -T api python scripts/load_sample_data.py; then
        print_status "Sample data loaded successfully"
    else
        print_warning "Sample data loading failed or already exists"
    fi
}

# Show deployment information
show_deployment_info() {
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📋 Service Information:${NC}"
    echo -e "  🌐 API: http://localhost:8000"
    echo -e "  📚 API Docs: http://localhost:8000/docs"
    echo -e "  🏥 Health Check: http://localhost:8000/health/"
    echo -e "  📊 MongoDB: localhost:27017"
    echo -e "  🔴 Redis: localhost:6379"
    echo ""
    echo -e "${BLUE}🔧 Useful Commands:${NC}"
    echo -e "  📊 View logs: docker-compose logs -f"
    echo -e "  ⏹️  Stop services: docker-compose down"
    echo -e "  🔄 Restart services: docker-compose restart"
    echo -e "  🧹 Clean up: make clean"
    echo ""
}

# Show logs on failure
show_logs_on_failure() {
    print_error "Deployment failed. Showing recent logs:"
    echo ""
    docker-compose logs --tail=50
}

# Main deployment function
main() {
    trap 'show_logs_on_failure' ERR
    
    check_prerequisites
    stop_existing
    start_containers
    
    if wait_for_services; then
        run_health_checks
        initialize_database
        load_sample_data
        show_deployment_info
    else
        print_error "Deployment failed - services did not start properly"
        show_logs_on_failure
        exit 1
    fi
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        print_info "Stopping all services..."
        docker-compose down
        print_status "All services stopped"
        ;;
    "restart")
        print_info "Restarting all services..."
        docker-compose restart
        print_status "All services restarted"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "health")
        print_info "Checking service health..."
        run_health_checks
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|health}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Deploy the application (default)"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  logs    - Show service logs"
        echo "  health  - Check service health"
        exit 1
        ;;
esac
