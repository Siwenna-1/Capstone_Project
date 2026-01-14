# Carrier-Grade Edge-Core-Cloud Distributed Telecommunication System

A comprehensive distributed system implementation for high-throughput telecom services with fault tolerance, distributed transactions, and dynamic load optimization.

## Project Overview

This project implements a carrier-grade distributed telecommunication system that spans edge, core, and cloud nodes. The system supports:

- **High-throughput telecom services** with optimized latency and resource utilization
- **Distributed transactions** with ACID compliance and 2PC protocols
- **Fault tolerance** including crash, omission, and Byzantine fault handling
- **Dynamic load balancing** and optimization across edge-core-cloud nodes
- **Real-time monitoring** and performance evaluation

## Quick Start

```bash
pip install -r requirements.txt
python src/gui/main_gui.py
```

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed system architecture documentation
- [Performance Analysis](docs/performance_analysis.md) - Quantitative evaluation results

## Features

### Communication
- **RPC**: JSON-RPC over TCP for service-to-service communication
- **Messaging**: Reliable message queue with acknowledgments
- **DSM**: Distributed shared memory with multiple consistency levels
- **Event Ordering**: Vector clocks for causal ordering

### Transactions
- **2PC Protocol**: Two-phase commit for distributed transactions
- **ACID Compliance**: Atomicity, consistency, isolation, durability
- **Recovery**: Write-ahead logging and transaction recovery

### Fault Tolerance
- **Replication**: Active-passive and active-active replication
- **Failover**: Automatic failover with < 5s recovery time
- **Byzantine Fault Tolerance**: PBFT for critical decisions

### Load Balancing
- **Dynamic Load Balancing**: Weighted round-robin with health checks
- **Process Migration**: Automatic process migration for optimization
- **Resource Allocation**: CPU, memory, and network allocation

## Quick Start

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the GUI application**:
```bash
python src/gui/main_gui.py
```

3. **Run performance tests**:
```bash
python tests/performance_tests.py
```

## Project Structure

```
.
├── README.md                  # This file
├── ARCHITECTURE.md            # Detailed architecture documentation
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Docker deployment configuration
├── Dockerfile                 # Docker image definition
├── config/                    # Configuration files
│   ├── edge_config.json
│   ├── core_config.json
│   └── cloud_config.json
├── src/                       # Source code
│   ├── common/               # Common utilities
│   ├── communication/        # RPC, messaging, DSM, event ordering
│   ├── transactions/         # Transaction management (2PC, ACID)
│   ├── fault_tolerance/      # Replication, failover, Byzantine
│   ├── load_balancing/       # Load balancer and migration
│   ├── nodes/                # Edge, core, cloud node implementations
│   └── gui/                  # GUI application
├── deployment/               # Deployment scripts
│   └── scripts/
├── tests/                    # Tests and performance evaluation
└── docs/                     # Additional documentation
```

## Performance Targets

| Metric | Edge | Core | Cloud |
|--------|------|------|-------|
| Latency (p50) | < 10ms | < 50ms | < 200ms |
| Latency (p99) | < 50ms | < 100ms | < 500ms |
| Throughput | 10k req/s | 5k txn/s | 1k ops/s |
| Availability | 99.9% | 99.95% | 99.99% |

## License

Educational use only
