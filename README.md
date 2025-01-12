# Quantum Factoring Implementation for N=77

This repository contains a Python implementation of Shor's algorithm to factor N=77 using IBM's quantum computers via Qiskit. The implementation specifically uses a=43, which has a known period of 2 modulo 77, allowing for a simplified and more efficient circuit design.

## Overview

The code demonstrates quantum factoring by:
1. Implementing controlled modular multiplication
2. Using the quantum Fourier transform
3. Running on real IBM quantum hardware
4. Finding the factors of 77 (7 × 11)

## Requirements

- Python 3.7+
- Qiskit
- IBM Quantum account and API token
- NumPy
- Math library

## Installation

1. Install the required packages:
```bash
pip install qiskit qiskit-ibm-runtime numpy
```

2. Set up your IBM Quantum account at [IBM Quantum](https://quantum-computing.ibm.com/)

3. Replace the API token in the code with your own token

## Usage

Run the script using Python:
```bash
python quantum_factoring.py
```

The code will:
1. Connect to IBM Quantum
2. Find the least busy quantum computer
3. Run the factoring circuit
4. Display the top 10 measurement results with corresponding phases
5. Analyze the results to find the factors of 77

## Technical Details

### Circuit Implementation
- Uses 4 counting qubits (N_COUNT = 4)
- Uses 7 additional qubits for modular arithmetic
- Implements controlled multiplication by 43 mod 77
- Applies inverse QFT to the counting register

### Key Features
- Optimized for period 2 (since 43² ≡ 1 mod 77)
- Direct implementation of controlled modular multiplication
- Full state vector manipulation
- Real quantum hardware execution

### Output Format
The code outputs:
Top 10 measurement results, each showing:
   - Quantum state (binary and decimal)
   - Probability
   - Phase
   - Period analysis
   - Factor checking

## Example Output

```
===== Top 10 Measurement Results =====

1. State |0000⟩ (0):
   Probability: 0.2500
   Phase: 0.0000
   Fraction: 0/1
   Period r=1:
   ...

[Additional results follow]
```
