#!/bin/bash

# Run tests for CMS Compliance Assistant

echo "================================="
echo "Running CMS Compliance Tests"
echo "================================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run pytest with coverage
echo "Running tests..."
pytest tests/ -v --tb=short

# Check exit code
if [ $? -eq 0 ]; then
    echo "================================="
    echo "All tests passed!"
    echo "================================="
else
    echo "================================="
    echo "Some tests failed. Check output above."
    echo "================================="
fi
