#!/bin/bash
# Security Analysis Script for SaltaDev Website
# Runs SonarQube, Semgrep, and Bandit for comprehensive SAST coverage
#
# Usage:
#   ./scripts/security-scan.sh              # Full analysis
#   SONAR_TOKEN=xxx ./scripts/security-scan.sh  # With SonarQube authentication

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== SaltaDev Security Analysis ==="
echo ""

# 1. Generate coverage report for SonarQube
echo "[1/5] Running tests with coverage..."
uv run pytest tests/ --cov=saltadev --cov-report=xml:coverage.xml -q || {
    echo "Warning: Tests failed, continuing with security analysis..."
}

# 2. Generate Bandit JSON report
echo "[2/5] Running Bandit security scan..."
uv run bandit -r saltadev/ -f json -o bandit-report.json -ll || true

# 3. Start SonarQube if not running
echo "[3/5] Starting SonarQube..."
docker compose -f docker/docker-compose.sonarqube.yml up -d sonarqube

echo "Waiting for SonarQube to be ready (this may take 1-2 minutes on first run)..."
until curl -s http://localhost:9000/api/system/status 2>/dev/null | grep -q '"status":"UP"'; do
    printf "."
    sleep 5
done
echo " Ready!"

# 4. Run SonarQube scanner
echo "[4/5] Running SonarQube analysis..."
if [ -n "$SONAR_TOKEN" ]; then
    docker compose -f docker/docker-compose.sonarqube.yml --profile scan run --rm sonar-scanner \
        -Dsonar.token="$SONAR_TOKEN"
else
    echo "Note: SONAR_TOKEN not set. Using anonymous access (default admin/admin on first run)."
    docker compose -f docker/docker-compose.sonarqube.yml --profile scan run --rm sonar-scanner
fi

# 5. Run Semgrep
echo "[5/5] Running Semgrep SAST..."
docker compose -f docker/docker-compose.sonarqube.yml --profile scan run --rm semgrep

echo ""
echo "=== Analysis Complete ==="
echo ""
echo "Results:"
echo "  - SonarQube Dashboard: http://localhost:9000 (login: admin/admin on first run)"
echo "  - Semgrep Report:      semgrep-report.json"
echo "  - Bandit Report:       bandit-report.json"
echo "  - Coverage Report:     coverage.xml"
echo ""
echo "To stop SonarQube:"
echo "  docker compose -f docker/docker-compose.sonarqube.yml down"
