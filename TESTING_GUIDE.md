# Testing Guide

## Running Performance Tests

### Where to Run Tests

**On Windows:**
- Open a **new terminal/command prompt** or **PowerShell window**
- Navigate to the project directory
- Run the test command

**On Linux:**
- Open a **new terminal window**
- Navigate to the project directory
- Run the test command

### Step-by-Step Instructions

#### 1. Open a New Terminal

**Windows:**
- Press `Win + R`, type `cmd` or `powershell`, press Enter
- OR right-click in File Explorer → "Open in Terminal"
- OR use your IDE's terminal (VS Code, PyCharm, etc.)

**Linux:**
- Press `Ctrl + Alt + T` (most Linux distributions)
- OR use your IDE's integrated terminal

#### 2. Navigate to Project Directory

```bash
# On Windows
cd C:\Users\okuth\distributed-telecom-system\distributed-telecom-system

# On Linux (after cloning)
cd ~/Capstone_Project
# OR
cd /path/to/Capstone_Project
```

#### 3. Activate Virtual Environment (Optional but Recommended)

If you're using a virtual environment:

```bash
# On Windows
venv\Scripts\activate

# On Linux
source venv/bin/activate
```

#### 4. Install Dependencies (If Not Already Installed)

```bash
pip install -r requirements.txt
```

#### 5. Run Performance Tests

```bash
python tests/performance_tests.py
```

**OR using Python module syntax:**

```bash
python -m tests.performance_tests
```

## What the Performance Tests Do

The performance tests will:

1. **Test Latency** - Measures response time for 100 requests
2. **Test Throughput** - Measures requests per second over 5 seconds
3. **Test Transaction Performance** - Measures 2PC transaction execution time for 50 transactions
4. **Test Failover Performance** - Measures failover time for 10 failovers

### Expected Output

```
Starting performance tests...
Testing latency with 100 requests...
Latency test completed
Testing throughput for 5.0 seconds...
Throughput: 987.45 requests/second
Testing transaction performance with 50 transactions...
Transaction performance test completed
Testing failover performance with 10 failovers...
Failover performance test completed

==================================================
Performance Test Results
==================================================
{
  "latency": {
    "mean": 8.5,
    "median": 7.2,
    "min": 5.1,
    "max": 52.3,
    "p95": 32.1,
    "p99": 48.7
  },
  "throughput": {
    "mean": 987.45,
    "median": 985.2,
    "min": 850.3,
    "max": 1023.7
  },
  "transaction_time": {
    "mean": 0.045,
    "min": 0.040,
    "max": 0.052
  },
  "failover_time": {
    "mean": 0.320,
    "min": 0.280,
    "max": 0.380
  }
}
==================================================

Results saved to performance_results.json
Performance tests completed
```

### Results File

The tests also save results to `performance_results.json` in the project root directory. This file contains detailed metrics in JSON format.

## Running Unit Tests

### Communication Tests

```bash
python tests/test_communication.py
```

**OR using unittest:**

```bash
python -m unittest tests.test_communication
```

### Transaction Tests

```bash
python tests/test_transactions.py
```

**OR using unittest:**

```bash
python -m unittest tests.test_transactions
```

### Run All Tests

```bash
# Using pytest (if installed)
pytest tests/

# OR using unittest
python -m unittest discover tests
```

## Running Tests While GUI is Running

**Yes, you can run tests while the GUI is running!**

The tests and GUI are independent:
- GUI: Runs on its own (one terminal)
- Tests: Run in a separate terminal

### Example Setup

**Terminal 1 (GUI):**
```bash
cd /path/to/project
python src/gui/main_gui.py
```

**Terminal 2 (Tests):**
```bash
cd /path/to/project
python tests/performance_tests.py
```

Both can run simultaneously without interfering with each other.

## Understanding Test Results

### Latency Metrics
- **mean**: Average response time
- **median**: Middle value (50th percentile)
- **p95**: 95% of requests completed in this time
- **p99**: 99% of requests completed in this time
- **Target**: Edge < 10ms, Core < 50ms, Cloud < 200ms

### Throughput Metrics
- **mean**: Average requests per second
- **Target**: Edge 10k req/s, Core 5k txn/s, Cloud 1k ops/s

### Transaction Time
- **mean**: Average 2PC transaction execution time
- **Target**: < 50ms for core coordination

### Failover Time
- **mean**: Average time to recover from a failure
- **Target**: < 5 seconds (MTTR - Mean Time To Recovery)

## Troubleshooting

### Import Errors

If you get import errors:

```bash
# Make sure you're in the project root directory
pwd  # Linux/Mac
cd   # Windows

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Install dependencies
pip install -r requirements.txt
```

### Module Not Found

```bash
# Try running from project root
cd /path/to/project
python -m tests.performance_tests
```

### Permission Errors (Linux)

```bash
# Make scripts executable
chmod +x deployment/scripts/*.sh
```

### No Output

Make sure the tests are actually running:
- Check for error messages
- Verify you're in the correct directory
- Check Python version: `python --version` (should be 3.8+)

## Integration with Documentation

After running tests, you can:
1. Compare results with targets in `ARCHITECTURE.md`
2. Update `docs/performance_analysis.md` with your results

