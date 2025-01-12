import numpy as np
from math import gcd
from fractions import Fraction

from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qiskit.circuit.library import QFT

print("Imports Successful")

service = QiskitRuntimeService(
    channel="ibm_quantum",
    token='Token'
)

print("QiskitRuntimeService loaded and authenticated!")

N = 77  # Number to factor
a = 43  # New value with period 2
N_COUNT = 4  # Reduced number of counting qubits since period is 2

def c_amod77(a, power):
    """
    Controlled multiplication by a mod 77 raised to specified power
    For a=43, the sequence is just: 1->43->1
    """
    # Create circuit with control qubit + 7 target qubits
    qc = QuantumCircuit(8)  # Still need 8 qubits total (1 control + 7 register)
    
    # Define controlled state transitions
    transitions = {
        0b0000001: 0b0101011,  # 1 -> 43
        0b0101011: 0b0000001,  # 43 -> 1
    }
    
    # Create the transformation circuit
    # First qubit (index 0) will be the control qubit
    for input_state in transitions:
        # Create state detection
        pattern = bin(input_state)[2:].zfill(7)
        for i, bit in enumerate(pattern):
            if bit == '0':
                qc.x(i + 1)  # Offset by 1 for control qubit
                
        # Create controlled transformation
        output_state = transitions[input_state]
        output_pattern = bin(output_state)[2:].zfill(7)
        
        # Apply controlled-X gates where input and output differ
        for i in range(7):
            if pattern[i] != output_pattern[i]:
                qc.cx(0, i + 1)  # Control from control qubit (0) to target (i+1)
                
        # Uncompute the state detection
        for i, bit in enumerate(pattern):
            if bit == '0':
                qc.x(i + 1)
    
    # Return the gate without adding another control
    base_gate = qc.to_gate()
    base_gate.name = f"{a}^{power} mod 77"
    return base_gate

def qft_dagger(n):
    """Inverse quantum Fourier transform"""
    qc = QuantumCircuit(n)
    
    # Swap qubits
    for qubit in range(n//2):
        qc.swap(qubit, n-qubit-1)
    
    # Apply controlled-phase and Hadamard
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi/float(2**(j-m)), m, j)
        qc.h(j)
        
    qc.name = "QFT†"
    return qc

# Create main quantum circuit
qc = QuantumCircuit(N_COUNT + 7, N_COUNT)

# Initialize counting qubits in superposition
for i in range(N_COUNT):
    qc.h(i)

# Initialize target register to |1⟩
qc.x(N_COUNT)

# Apply controlled modular multiplications
for i in range(N_COUNT):
    qc.append(c_amod77(a, 2**i), [i] + list(range(N_COUNT, N_COUNT + 7)))

# Apply inverse QFT to counting register
qc.append(qft_dagger(N_COUNT), range(N_COUNT))

# Measure counting qubits
qc.measure(range(N_COUNT), range(N_COUNT))

qc.name = "Shor77"
backend = service.least_busy(simulator=False)
print("Using backend:", backend.name)

transpiled_circ = transpile(qc, backend=backend)
sampler = Sampler(mode=backend)
print("Sampler is ready.")

job = sampler.run([transpiled_circ], shots=4096)
print(f"Submitted job. Job ID: {job.job_id()}")

result = job.result()
pub_result = result[0]  # The single-circuit result
counts_dict = pub_result.data.c.get_counts()  # 'c' is the auto-named classical register
shots_used = sum(counts_dict.values())
counts_prob = {bitstring: c / shots_used for bitstring, c in counts_dict.items()}

print("\n===== Top 10 Measurement Results =====")
sorted_counts = sorted(counts_prob.items(), key=lambda x: x[1], reverse=True)[:10]

for i, (bitstring, prob) in enumerate(sorted_counts, 1):
    decimal = int(bitstring, 2)
    phase = decimal / (2**N_COUNT)
    print(f"\n{i}. State |{bitstring}⟩ ({decimal}):")
    print(f"   Probability: {prob:.4f}")
    print(f"   Phase: {phase:.4f}")
    
    frac = Fraction(phase).limit_denominator(N)
    r = frac.denominator
    s = frac.numerator
    print(f"   Fraction: {s}/{r}")
    
    if r % 2 == 0:  # Only check even periods
        guess1 = gcd(a**(r//2) - 1, N)
        guess2 = gcd(a**(r//2) + 1, N)
        print(f"   Period r={r}:")
        print(f"    - gcd({a}^({r//2}) - 1, {N}) = {guess1}")
        print(f"    - gcd({a}^({r//2}) + 1, {N}) = {guess2}")
        if guess1 not in [1, N] or guess2 not in [1, N]:
            print(f"   Found factors! {guess1} and {guess2}")
    else:
        print(f"   Skipping period r={r} (not even)")
    print("   " + "-" * 40)

print("\nDone!")