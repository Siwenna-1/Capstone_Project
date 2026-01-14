# GUI User Guide

## How to Run the GUI

```bash
python src/gui/main_gui.py
```

## GUI Overview

The GUI provides an interactive interface to demonstrate and monitor the distributed telecommunication system. Here's what each part does:

### Main Interface Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Carrier-Grade Edge-Core-Cloud Distributed System           │
│  [Start System] [Stop System]                                │
├─────────────────┬───────────────────────────────────────────┤
│                 │                                           │
│  System         │  System Metrics                           │
│  Topology       │  - Timestamp                              │
│  (Visual)       │  - Edge Nodes                             │
│                 │  - Core Nodes                             │
│  Transaction    │  - Cloud Nodes                            │
│  Controls       │  - Active Transactions                    │
│  [Execute Txn]  │  - CPU Usage                              │
│  [Abort Txn]    │  - Memory Usage                           │
│                 │  - Network Latency                        │
│  Fault          │  - Throughput                             │
│  Injection      │                                           │
│  [Inject Fault] │  Transaction Log                          │
│                 │  - All system events                      │
│                 │  - Transaction status                     │
│                 │  - Fault events                           │
└─────────────────┴───────────────────────────────────────────┘
```

## Step-by-Step Usage Guide

### Step 1: Start the System

1. **Click "Start System"** button (top right, green button)
   - This initializes the distributed system
   - The system topology will be displayed on the left panel
   - System metrics will start updating in real-time

### Step 2: Understanding the Display

#### **Left Panel - System Topology**

**Visual Representation:**
- **Blue circles (top row)**: Edge nodes (edge-1, edge-2, edge-3)
  - These are low-latency nodes for user-facing services
  - They handle requests and cache data locally
  
- **Red circles (middle row)**: Core nodes (core-1, core-2)
  - These are coordination nodes
  - They manage transactions (2PC protocol)
  - They handle load balancing decisions
  
- **Green rectangles (bottom row)**: Cloud nodes (cloud-1, cloud-2)
  - These are persistent storage nodes
  - They store data permanently
  - They maintain transaction logs

**Connections:**
- Dashed gray lines show the communication paths between nodes
- Edge nodes connect to Core nodes
- Core nodes connect to Cloud nodes

#### **Right Panel - Metrics and Logs**

**Top Section - System Metrics:**
- **Timestamp**: Current system time
- **Edge Nodes**: Number of active edge nodes (3)
- **Core Nodes**: Number of active core nodes (2)
- **Cloud Nodes**: Number of active cloud nodes (2)
- **Active Transactions**: Number of currently executing transactions
- **CPU Usage**: Current CPU utilization (simulated, updates every second)
- **Memory Usage**: Current memory utilization (simulated, updates every second)
- **Network Latency**: Simulated network latency in milliseconds
- **Throughput**: Requests per second (simulated, updates every second)

**Bottom Section - Transaction Log:**
- Shows all system events in real-time
- Color-coded messages:
  - **Blue**: Information messages
  - **Green**: Success messages (committed transactions)
  - **Red**: Error messages (aborted transactions, failures)
  - **Yellow**: Warning messages (fault injection)

### Step 3: Execute Transactions

1. **Click "Execute Transaction"** button
   - This simulates a distributed transaction using the 2PC protocol
   - You'll see in the log:
     - "Executing transaction: TXN-[timestamp]"
     - "Phase 1: PREPARE sent to participants" (blue)
     - "Phase 1: All participants voted COMMIT" (green)
     - "Phase 2: COMMIT sent to participants" (blue)
     - "Transaction TXN-[timestamp] COMMITTED successfully" (green)
   
   **What's happening:**
   - The system is demonstrating the Two-Phase Commit protocol
   - Phase 1: Coordinator sends PREPARE to all participants
   - Phase 1: All participants vote COMMIT
   - Phase 2: Coordinator sends COMMIT to all participants
   - All participants execute and acknowledge
   - Transaction is committed atomically (all-or-nothing)

2. **Click multiple times** to execute multiple transactions
   - Watch the "Active Transactions" count increase
   - Each transaction is logged with a unique ID

### Step 4: Abort Transactions

1. **Click "Abort Transaction"** button
   - This simulates a transaction that gets aborted
   - You'll see in the log:
     - "Aborting transaction: TXN-[timestamp]" (yellow)
     - "Phase 1: PREPARE sent to participants" (blue)
     - "Phase 1: Participant voted ABORT" (red)
     - "Phase 2: ABORT sent to participants" (blue)
     - "Transaction TXN-[timestamp] ABORTED" (red)
   
   **What's happening:**
   - This demonstrates atomicity: if any participant cannot commit, the entire transaction is aborted
   - All participants roll back their changes
   - This is the ACID property of Atomicity in action

### Step 5: Inject Faults (Fault Tolerance Demo)

1. **Click "Inject Node Failure"** button
   - This simulates a node failure in the system
   - A random node (edge, core, or cloud) is selected
   - You'll see in the log:
     - "Injecting failure in node: [node-id]" (yellow)
     - "Node [node-id] failed" (red)
     - "Failover triggered, replacement node selected" (blue)
     - "System recovered" (green)
   
   **What's happening:**
   - The system detects the failure (heartbeat timeout)
   - A replacement node is selected automatically
   - Traffic is redirected to the replacement
   - The system recovers without manual intervention
   - This demonstrates fault tolerance and automatic failover

2. **Click multiple times** to test different failure scenarios

### Step 6: Stop the System

1. **Click "Stop System"** button (top right, red button)
   - This stops the system simulation
   - Metrics stop updating
   - System is shut down gracefully

## Demonstration Scenarios

### Scenario 1: Normal Operation
1. Start the system
2. Execute 3-5 transactions (click "Execute Transaction" multiple times)
3. Observe the logs showing successful commits
4. Watch metrics update in real-time

**What to explain:**
- "The system is processing transactions normally"
- "All transactions are committing successfully"
- "The 2PC protocol ensures atomicity - all participants commit together"

### Scenario 2: Transaction Abort
1. Start the system
2. Click "Abort Transaction"
3. Observe the red error messages in the log

**What to explain:**
- "This demonstrates transaction atomicity"
- "If any participant cannot commit, the entire transaction is aborted"
- "All changes are rolled back - this is the ACID property"

### Scenario 3: Fault Tolerance
1. Start the system
2. Execute a few transactions
3. Click "Inject Node Failure"
4. Observe the failover process

**What to explain:**
- "The system detects the failure automatically"
- "A replacement node is selected"
- "Traffic is redirected automatically"
- "The system recovers without manual intervention"
- "This demonstrates fault tolerance and high availability"

### Scenario 4: System Monitoring
1. Start the system
2. Let it run for a while
3. Observe the metrics updating
4. Execute transactions and watch metrics change

**What to explain:**
- "The metrics show real-time system performance"
- "CPU and memory usage are monitored"
- "Network latency and throughput are tracked"
- "This enables dynamic load balancing"

## Key Concepts to Explain

### 1. Three-Tier Architecture
- **Edge**: Low-latency, user-facing services
- **Core**: Coordination and transaction management
- **Cloud**: Persistent storage

### 2. Two-Phase Commit (2PC)
- **Phase 1 (Voting)**: Coordinator asks all participants to prepare
- **Phase 2 (Decision)**: Coordinator commits or aborts based on votes
- **Atomicity**: All participants commit together or all abort

### 3. Fault Tolerance
- **Failure Detection**: Heartbeat monitoring
- **Failover**: Automatic selection of replacement nodes
- **Recovery**: System continues operating despite failures

### 4. Load Balancing
- Metrics are collected for each node
- Load is distributed based on node capacity
- System optimizes resource utilization

## Tips for Presentations

1. **Start with the topology visualization** - Explain the three tiers
2. **Execute a transaction** - Show normal operation
3. **Abort a transaction** - Demonstrate atomicity
4. **Inject a fault** - Show fault tolerance
5. **Show the metrics** - Explain real-time monitoring

## Troubleshooting

- **GUI not responding**: Make sure you clicked "Start System" first
- **No metrics showing**: Wait a moment - metrics update every second
- **Buttons grayed out**: Click "Start System" to enable them
