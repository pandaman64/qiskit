# -*- coding: utf-8 -*-

# Copyright 2018, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

"""Test the Unroller pass"""

import os
from sympy import pi

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.transpiler.passes import Unroller
from qiskit.converters import circuit_to_dag
import qiskit
from qiskit.dagcircuit import DAGCircuit
from qiskit.circuit import QuantumRegister
from qiskit.extensions.standard.u1 import U1Gate
from qiskit.extensions.standard.cx import CnotGate


class UnrollerBench:
    """Tests the Unroller pass."""

    def setup(self):
        self.setup_basic()
        self.setup_toffoli()
        self.setup_1q_chain_conditional()

    def setup_basic(self):
        qr = QuantumRegister(1, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.h(qr[0])
        self.basic = circuit_to_dag(circuit)

    def setup_toffoli(self):
        qr1 = QuantumRegister(2, 'qr1')
        qr2 = QuantumRegister(1, 'qr2')
        circuit = QuantumCircuit(qr1, qr2)
        circuit.ccx(qr1[0], qr1[1], qr2[0])
        self.tofolli = circuit_to_dag(circuit)

    def setup_1q_chain_conditional(self):
        qr = QuantumRegister(1, 'qr')
        cr = ClassicalRegister(1, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.h(qr)
        circuit.tdg(qr)
        circuit.z(qr)
        circuit.t(qr)
        circuit.ry(0.5, qr)
        circuit.rz(0.3, qr)
        circuit.rx(0.1, qr)
        circuit.measure(qr, cr)
        circuit.x(qr).c_if(cr, 1)
        circuit.y(qr).c_if(cr, 1)
        circuit.z(qr).c_if(cr, 1)
        self.chain_conditional = circuit_to_dag(circuit)

    def time_basic_unroll(self):
        """Test decompose a single H into u2.
        """
        pass_ = Unroller(['u2'])
        unrolled_dag = pass_.run(self.basic)

    def time_unroll_toffoli(self):
        """Test unroll toffoli on multi regs to h, t, tdg, cx.
        """
        pass_ = Unroller(['h', 't', 'tdg', 'cx'])
        unrolled_dag = pass_.run(self.tofolli)

    def time_unroll_1q_chain_conditional(self):
        """Test unroll chain of 1-qubit gates interrupted by conditional.
        """
        pass_ = Unroller(['u1', 'u2', 'u3'])
        unrolled_dag = pass_.run(self.chain_conditional)

class UnrollLargeFile:
    def setup(self):
        version_parts = qiskit.__version__.split('.')
        self.qasm_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'qasm'))
        large_qasm_path = os.path.join(self.qasm_path, 'prime6_pkrm.qasm')

        if hasattr(qiskit, 'load_qasm_file'):
            self.large_qasm = qiskit.load_qasm_file(large_qasm_path)
        elif version_parts[0] == '0' and int(version_parts[1]) < 5:
            self.large_qasm = qiskit.QuantumProgram()
            self.large_qasm.load_qasm_file(large_qasm_path,
                                           name='large_qasm')
        else:
            self.large_qasm = qiskit.QuantumCircuit.from_qasm_file(
                large_qasm_path)
        self.large_qasm_dag = circuit_to_dag(self.large_qasm)

    def time_large_qasm(self):
        pass_ = Unroller(['u1', 'u2', 'u3'])
        unrolled_dag = pass_.run(self.large_qasm_dag)

