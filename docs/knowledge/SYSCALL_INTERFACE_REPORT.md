# ⌨️ System Call Interface Design: A Comprehensive 2025/2026 Survey for GAIA-OS

**Date:** May 1, 2026
**Status:** Comprehensive Technical Survey (35+ sources)
**Canon Mandate:** C119 — Foundational understanding of system call interface design across the OS paradigm spectrum: capability-based microkernels (seL4, Zircon, Scarlet), Linux ABI evolution, Rust-native kernels (Asterinas, Blaqout-OS, Redox), WASI Component Model, formal specification/verification (KAPI), and syscall security (seccomp-eBPF). Informs GAIA-OS's current application-layer security model, medium-term internal API contracts, and long-term custom kernel syscall design.

---

## Executive Summary

Three forces define the 2025–2026 system call interface landscape:

1. **seL4 capability model** — every syscall requires an explicit, unforgeable capability; formally verified to machine code; sub-800-cycle performance
2. **Linux generational shift** — io_uring expands to general-purpose batching; KAPI Framework introduces machine-readable, automatically verifiable syscall ABI contracts
3. **Rust-native kernel wave** — Asterinas (210+ Linux syscalls, 14.0% unsafe TCB), Blaqout-OS (object-capability Rust OS), Redox (full Rust userspace) prove memory-safe syscall design is production-viable

> **Central finding for GAIA-OS:** The system call interface is the legal code of the OS — the provably enforceable set of laws governing what every process may and may not do. The IBCT capability token system already implemented at GAIA-OS's application layer IS precisely the abstraction that seL4 enforces at kernel level and WASI enforces at sandbox level. The progression from application-layer capability checks → io_uring batching → full capability-based kernel syscall interface is clear, graded, and validated by the research community.

```
GAIA-OS SYSCALL INTERFACE EVOLUTION PATH:
══════════════════════════════════════════════════════════════════════

  Phase A (NOW, G-10):
    Application-layer capability checks
    action_gate.py + IBCT tokens + FastAPI middleware
    Crypto-signed tokens validated at application layer

  Phase B (G-11 to G-14):
    io_uring-style batching with capability validation
    seccomp-eBPF syscall filtering
    µKernel-style submission rings for internal IPC

  Phase C (Phase 4 Custom Kernel):
    Full capability-based kernel syscall interface
    seL4-style capabilities + Scarlet/Zircon handle design
    Asterinas safe-Rust syscall handler patterns
    Formal verification of syscall security

  Phase D (Long-Term):
    CHERI hardware-enforced capabilities
    Capabilities enforced IN SILICON — no software bypass possible
```

---

## Table of Contents

1. [Theoretical Foundations: What a Syscall Interface Must Provide](#1-theoretical-foundations)
2. [Capability-Based Syscall Design: The seL4 Model](#2-capability-based-syscall-design)
3. [Hybrid Capability-POSIX Interfaces: Scarlet and Zircon](#3-hybrid-capability-posix-interfaces)
4. [The Linux Syscall Interface: Architecture, Evolution, Stabilization](#4-linux-syscall-interface)
5. [The io_uring Revolution: Async I/O to Generalized Batching](#5-io_uring-revolution)
6. [eBPF: Safe Kernel Extensibility via Verified Syscall Gateways](#6-ebpf-kernel-extensibility)
7. [Formal Specification and Verification of Syscall Interfaces](#7-formal-specification-verification)
8. [Memory-Safe Syscall Design in Rust Kernels](#8-memory-safe-rust-kernels)
9. [The WASI Component Model: Capability-Based Sandbox APIs](#9-wasi-component-model)
10. [Syscall Security: Filtering, Sandboxing, Attack Surface Reduction](#10-syscall-security)
11. [Performance Optimization: vDSO, Batching, Ring-Based Architectures](#11-performance-optimization)
12. [GAIA-OS Integration Recommendations](#12-gaia-os-integration)
13. [Conclusion](#13-conclusion)

---

## 1. Theoretical Foundations: What a Syscall Interface Must Provide

```
THE SIX COMPETING REQUIREMENTS:
══════════════════════════════════════════════════════════════════════

  SECURITY:        no application accesses resources without authorization
  PERFORMANCE:     minimize user-kernel transition overhead
  STABILITY:       ABI remains compatible across kernel versions
  EXPRESSIVENESS:  applications communicate intent in sufficient detail
  VERIFIABILITY:   formal reasoning about what kernel will/won't do
  PORTABILITY:     applications portable across OS implementations

THE FUNDAMENTAL TRADE-OFF:
══════════════════════════════════════════════════════════════════════

  AMBIENT AUTHORITY MODEL (POSIX):
  ┌──────────────────────────────────────────────────────────────────┐
  │ Process possesses: UID + GIDs                                    │
  │ Kernel checks: UID vs file permission bits at access time        │
  │ No per-resource token required; global identity sufficient       │
  │                                                                  │
  │ CONSEQUENCE: any process compromise grants access to             │
  │ EVERYTHING that UID can access                                   │
  │ Attack surface: unbounded (proportional to UID privileges)       │
  └──────────────────────────────────────────────────────────────────┘

  CAPABILITY MODEL (seL4):
  ┌──────────────────────────────────────────────────────────────────┐
  │ Process possesses: only unforgeable capability tokens            │
  │ Each token: grants access to ONE specific kernel object          │
  │ No global root user, no ambient authority                        │
  │ No resource accessible without explicit, delegated capability    │
  │                                                                  │
  │ CONSEQUENCE: process compromise grants access to EXACTLY         │
  │ what capabilities it holds — no more, ever                       │
  │ Attack surface: bounded (proportional to capabilities held)      │
  └──────────────────────────────────────────────────────────────────┘

GAIA-OS POSITION:
  Currently:    POSIX ambient authority at OS layer
                + capability token enforcement at application layer
  Target:       capability enforcement at KERNEL layer
                (application-layer IBCT system becomes kernel-native)
```

---

## 2. Capability-Based Syscall Design: The seL4 Model

### 2.1 The Foundational Principle: Explicit Authority

```
SEL4 SYSCALL DESIGN AXIOM:
══════════════════════════════════════════════════════════════════════

  "The resulting seL4 design features an API that requires explicit
   authority for all operations — all system calls require an
   appropriate capability as an argument in order to perform
   the operation."

  This is NOT policy layered on a permissive kernel.
  This IS the kernel's NATIVE execution model.

IMPLICATIONS:
  ┌─────────────────────────────────────────────────────────────────┐
  │ Every syscall:  takes capability as FIRST ARGUMENT              │
  │ Thread:         cannot send IPC without capability to endpoint  │
  │ Process:        cannot map memory without capability to AS      │
  │ Kernel:         INCAPABLE of performing op without capability   │
  │                                                                 │
  │ There is no "sudo." There is no "root."                         │
  │ There is only: "does this thread hold this capability?"         │
  └─────────────────────────────────────────────────────────────────┘

FORMAL VERIFICATION STATUS:
  Modelled in:  Isabelle interactive theorem prover
  Proven:       capable of confining authority in a subsystem
  Proven:       isolating a subsystem
  (given subsystems meet simple, intuitive pre-conditions)

  NOT a statement about the capability model in the abstract.
  This IS a proof about the ACTUAL C IMPLEMENTATION of seL4,
  verified all the way to MACHINE CODE.
```

### 2.2 Syscalls as Object-Oriented Service Invocations

```
SEL4 vs LINUX SYSCALL MODEL:
══════════════════════════════════════════════════════════════════════

  LINUX MODEL (function-oriented):
    syscall_number → function → {read, write, open, close, ...}
    Each syscall: independent function performing discrete operation
    Interface: fixed table of numbered functions
    Authority: inferred from process UID/GID

  SEL4 MODEL (object-oriented):
    capability → kernel object → {send, receive, call, reply, ...}
    Each syscall: invocation of an operation on a kernel object
    Interface: defined by OBJECT TYPES + their authorized operations
    Authority: explicit capability argument on every call

  THE DIFFERENCE IN PRACTICE:
  ┌────────────────────────────────────────────────────────────────┐
  │ Linux:  open("/etc/shadow", O_RDONLY)                          │
  │         kernel checks: does this UID have permission?          │
  │         if UID=0: always YES                                   │
  │                                                                │
  │ seL4:   call(cap_to_filesystem_service, OPEN, "/etc/shadow")  │
  │         kernel checks: does this thread HOLD a capability      │
  │         that grants access to this filesystem object?          │
  │         if no cap: always NO (regardless of any global state)  │
  └────────────────────────────────────────────────────────────────┘
```

### 2.3 XDC: Syscall Interface Decomposed into Three Layers

```
CROSS-DOMAIN COMMUNICATION (XDC) MODEL (March 2026):
══════════════════════════════════════════════════════════════════════

  Decomposes the syscall interface into THREE orthogonal layers:

  CONTROL RAIL (Protected Procedure Calls):
    Path:      small, synchronous, low-latency
    Purpose:   authorization checks, capability delegation, IPC setup
    Mechanism: protected procedure calls (context switch to service)
    Optimize:  for MINIMAL LATENCY
    Target:    sub-800 cycles (seL4 baseline)

  BULK DATA MOVEMENT:
    Path:      high-bandwidth, zero-copy
    Purpose:   sensor telemetry, file I/O, network buffers
    Mechanism: capability-gated shared memory regions
    Optimize:  for MAXIMUM THROUGHPUT
    Target:    RAM bandwidth (no kernel copy in data path)

  EVENT SIGNALING:
    Path:      lightweight, non-blocking
    Purpose:   notifications, wakeups, state changes
    Mechanism: lightweight notification objects
    Optimize:  for LOWEST LATENCY (no data transfer)
    Target:    sub-microsecond (eventfd/UINTR class)

GAIA-OS XDC LAYER MAPPING:
  ┌───────────────────────────────────────────────────────────────┐
  │ Charter enforcement, action gate decisions                    │
  │   → CONTROL RAIL (synchronous PPC + IBCT verification)       │
  ├───────────────────────────────────────────────────────────────┤
  │ DAS seismic arrays, satellite imagery, sensor bulk data       │
  │   → BULK DATA (capability-gated shared memory, iceoryx2)      │
  ├───────────────────────────────────────────────────────────────┤
  │ Sentient core heartbeat, Gaian state change events            │
  │   → EVENT SIGNALING (lightweight notifications, eventfd)      │
  └───────────────────────────────────────────────────────────────┘
```

### 2.4 The Capability Derivation Tree

```
CAPABILITY DERIVATION AND AUTHORITY ATTENUATION:
══════════════════════════════════════════════════════════════════════

  Capabilities can be DERIVED from parent capabilities:
    Derived capability: SUBSET of parent's rights ONLY
    Cannot escalate: kernel enforces rights on every operation
    Cannot forge:    capability is a kernel-managed opaque token

  EXAMPLE:
    Process A holds: cap(MemRegion_X, READ | WRITE)
    A derives:       cap(MemRegion_X, READ_ONLY)
    A delegates:     READ_ONLY cap to untrusted Process B
    Process B:       attempts write → KERNEL REJECTS (no write right)
    Process B:       cannot obtain write access BY ANY MEANS
                     (it holds no capability that grants WRITE)

  AUTHORITY TREE:
    Root caps established at boot time
    Every subsequent delegation = provable ATTENUATION of root
    No process can EVER hold more authority than explicitly delegated

  FORMAL PROPERTY:
    "No process can ever possess more authority than was explicitly
     delegated to it by a process holding the appropriate
     parent capability."

  GAIA-OS IBCT CHAIN MAPPING:
    Creator IBCT:      root capability (full authority delegation)
    Admin IBCT:        derived (subset of Creator rights)
    Supervisor IBCT:   derived (subset of Admin rights)
    Gaian IBCT:        derived (subset of Supervisor rights)
    Action IBCT:       derived (specific action authorization only)

    Entire chain: cryptographically verifiable
    No token can escalate beyond its parent's rights
    This IS the capability derivation tree, in application space
```

---

## 3. Hybrid Capability-POSIX Interfaces: Scarlet and Zircon

### 3.1 Scarlet: Bridging Capabilities and POSIX Familiarity

```
SCARLET KERNEL — HYBRID CAPABILITY-POSIX DESIGN:
══════════════════════════════════════════════════════════════════════

  Goal: "combines security benefits of capability systems
         with familiarity of traditional POSIX-like APIs"

  THREE KEY DESIGN ASPECTS:

  1. HANDLE-BASED OBJECT MANAGEMENT:
     Kernel objects accessed through OPAQUE HANDLES (integers)
     Not internal pointers — no pointer arithmetic, no forgery
     Each handle = capability with specific permissions
     Pattern familiar to POSIX devs (like a typed file descriptor)

  2. CAPABILITY-SPECIFIC OPERATIONS:
     Syscalls organized by the CAPABILITIES they require
     Example: stream_read(200) works on ANY object with StreamOps cap
              NOT just files — any stream-capable kernel object
     Benefit: generic operations on heterogeneous objects
              capability type system replaces type-specific APIs

  3. NUMERICAL RANGE ORGANIZATION:
     ┌──────────────────────────────────────────────────────────┐
     │ Syscall Range  │ Domain               │ Example calls    │
     ├──────────────────────────────────────────────────────────┤
     │ 1 – 99         │ Process management   │ fork, exec, wait │
     │ 100 – 199      │ Handle management    │ dup, close, send │
     │ 200 – 299      │ Stream operations    │ read, write, seek│
     │ 400 – 499      │ VFS operations       │ open, stat, mkdir│
     │ 600 – 699      │ IPC                  │ send, recv, chan  │
     └──────────────────────────────────────────────────────────┘
     Self-documenting: syscall number reveals domain
     Extensible: new ranges add domains without renumbering

  GAIA-OS MEDIUM-TERM TEMPLATE:
    Personal Gaians use familiar patterns: open, read, write, close
    Every operation: gated by capability kernel enforces
    Capability: invisible in API syntax; enforced in kernel logic
    Developer experience: POSIX-familiar
    Security property: capability-enforced at kernel boundary
```

### 3.2 Zircon and Blaqout-OS: Handle Rights Model

```
ZIRCON HANDLE-BASED SYSCALL MODEL:
══════════════════════════════════════════════════════════════════════

  Handle:         32-bit opaque integer referencing a kernel object
  Rights:         bitflags on the handle governing permitted ops
  Transfer:       handles passed between processes via Channel IPC
                  (capabilities flow with the message)

  RIGHTS BITFLAGS (Blaqout-OS implementation, April 2026):
    READ       — observe object state
    WRITE      — modify object state
    EXECUTE    — invoke/run object
    DUPLICATE  — create additional handle to same object
    TRANSFER   — send handle to another process via channel
    SIGNAL     — send signals/events to the object

  HANDLE LIFECYCLE:
    Created: by syscall returning a new handle to caller
    Shared:  via Channel.send(handle) — atomic ownership transfer
    Revoked: by closing the handle (kernel decrements refcount)
    Forged:  IMPOSSIBLE — handles are kernel-managed opaque integers
             user-space cannot construct a valid handle by guessing

  BLAQOUT-OS EXTENSIONS (April 2026):
    ZK-native integration:  ZK proof verification for authorization
    Async integration:      AsyncDispatcher trait for kernel objects
    CondVar-based waiting:  async Channel IPC without polling

  GAIA-OS HANDLE RIGHTS → IBCT RIGHTS MAPPING:
    ┌─────────────────┬───────────────────────────────────────┐
    │ Handle Right    │ IBCT Equivalent                       │
    ├─────────────────┼───────────────────────────────────────┤
    │ READ            │ observe:sensor:* (sensor read scope)  │
    │ WRITE           │ mutate:gaian:memory (write scope)     │
    │ EXECUTE         │ execute:action:* (action scope)       │
    │ DUPLICATE       │ delegate:token (sub-delegation scope) │
    │ TRANSFER        │ share:capability (transfer scope)     │
    │ SIGNAL          │ notify:event:* (event emission scope) │
    └─────────────────┴───────────────────────────────────────┘
```

---

## 4. The Linux Syscall Interface: Architecture, Evolution, Stabilization

### 4.1 The "Never Break Userspace" Rule

```
LINUX ABI STABILITY GUARANTEE:
══════════════════════════════════════════════════════════════════════

  Rule:    "Never break userspace" — binary compatibility maintained
           across ALL kernel versions
  Scope:   syscall numbers, parameter layouts, struct fields, errors
  Method:  every new syscall ADDS to ABI; never replaces/removes

  SYSCALL NUMBER PERMANENCE:
    Once assigned: permanent per architecture
    Once assigned: NEVER reused or changed
    Historical example: old syscalls (like _llseek) remain forever
                        even if superseded by better alternatives

  ABI FUTURE-PROOFING TECHNIQUES:
    Reserved fields:    struct padding for future extensions
    Flags parameters:   caller passes flags=0, future bits reserved
    Versioning:         some interfaces support explicit version args
    UAPI headers:       stable, kernel-internal-free header exports

  WHY THIS MATTERS FOR GAIA-OS:
    GAIA-OS's Linux-compatibility layer (Phase B/C) must honor this
    Any syscall handler added must be treated as PERMANENT CONTRACT
    The KAPI Framework (see Section 7) makes this contract explicit
    and machine-verifiable rather than relying on human vigilance
```

### 4.2 Great Syscall Table Unification (2025–2026)

```
LINUX SYSCALL TABLE UNIFICATION:
══════════════════════════════════════════════════════════════════════

  Problem:  per-architecture syscall table divergence accumulated
            over decades of independent maintenance
  Solution: centralized syscall table format
  Migrated: arc, arm64, csky, hexagon, loongarch, nios2,
            openrisc, riscv → centralized format

  BENEFITS:
    Simplified maintenance: single source of truth for syscall numbers
    Reduced breakage risk: new syscalls propagate consistently
    Architecture parity: new syscalls available uniformly

  GAIA-OS APPLICATION:
    Phase 4 custom kernel: adopt centralized table from day one
    No per-architecture divergence to accumulate
    KAPI macros (see Section 7) co-located with centralized entries
```

### 4.3 The Kernel API Specification Framework (KAPI)

```
KAPI FRAMEWORK (Sasha Levin, 2025–2026 RFC series):
══════════════════════════════════════════════════════════════════════

  Problem being solved:
    "The long-standing challenge of maintaining stable interfaces
     between the kernel and user-space programs. The lack of
     machine-readable API specifications has led to inadvertent
     breakages and inconsistent validation across system calls
     and IOCTLs."

  THREE KEY COMPONENTS:

  1. DECLARATIVE MACROS (in kernel source code):
     KAPI_SYSCALL(openat, ...)
       .param("dirfd",   INT,  "base directory fd or AT_FDCWD")
       .param("pathname", STR, "path to open")
       .param("flags",   UINT, "O_* flags")
       .param("mode",    UINT, "creation mode if O_CREAT")
       .returns("fd >= 0 on success, -errno on failure")
       .errors({ENOENT, EACCES, ENOMEM, ...})
     Specification CO-LOCATED with implementation
     → cannot diverge (diff shows both change together)

  2. AUTOMATED EXTRACTION TOOLS (kapi tool):
     Sources: kernel source (KAPI macros),
              vmlinux binary (.kapi_specs ELF section),
              running kernel (debugfs interface)
     Outputs: plain text, JSON, RST documentation
     Use:     automatic documentation generation,
              regression testing, compatibility analysis

  3. RUNTIME VALIDATION INFRASTRUCTURE:
     Via debugfs
     Verifies: ACTUAL kernel behavior matches specification
     Detects:  ABI changes that break user-space applications
     Enables:  CI/CD pipeline testing of syscall compatibility

  PARADIGM SHIFT:
    Before KAPI: manual documentation + human vigilance
    After KAPI:  automated, machine-verified interface specification
    Consequence: ABI breakage detectable at CI time, not user time

  GAIA-OS CUSTOM KERNEL MANDATE:
    ALL syscall interfaces: specified via KAPI-style macros
    From day one, not retrofitted
    Every PR touching syscall interface: CI verifies spec consistency
    Charter-enforcement properties: specified as machine-checkable rules
```

---

## 5. The io_uring Revolution: From Async I/O to Generalized Batching

### 5.1 The Architectural Innovation

```
IO_URING SYSCALL INTERFACE MODEL:
══════════════════════════════════════════════════════════════════════

  Author:  Jens Axboe
  Merged:  Linux 5.1 (2019)
  Status 2026: general-purpose async kernel interface

  TRADITIONAL SYSCALL MODEL (per-operation):
    read(fd, buf, len)  → context switch to kernel → result
    write(fd, buf, len) → context switch to kernel → result
    N operations = N context switches = N × (kernel-entry cost)

  IO_URING MODEL (batched):
    ┌──────────────────────────────────────────────────────────────┐
    │  USER SPACE           │  KERNEL SPACE                        │
    │                       │                                      │
    │  SQ Ring (mmap'd)     │  SQ Ring (same pages)                │
    │  Write SQE[0..N-1]    │  Kernel reads SQE[0..N-1]            │
    │  → io_uring_enter(1)  │  → processes all N operations        │
    │                       │  → writes CQE[0..N-1] to CQ Ring     │
    │  CQ Ring (mmap'd)     │  CQ Ring (same pages)                │
    │  Read CQE[0..N-1]     │                                      │
    └──────────────────────────────────────────────────────────────┘

  KEY INSIGHT: one syscall amortizes cost across N operations
    Cost per operation: (kernel-entry cost) / N + operation cost
    As N → ∞: per-operation syscall overhead → 0

  KERNEL POLLING MODE: ZERO syscalls in hot path
    Kernel thread polls SQ ring continuously
    User submits by writing to ring (no syscall at all)
    Performance: equivalent to shared-memory IPC
```

### 5.2 The µKernel Vectorized Syscall Model

```
µKERNEL CAPABILITY-GATED RING SYSCALL MODEL:
══════════════════════════════════════════════════════════════════════

  Direct adoption and extension of io_uring pattern:

  "µKernel uses a vectorized syscall model inspired by io_uring.
   Userspace queues operations into a shared-memory ring and
   flushes them with a single SYS_SUBMIT syscall.
   The kernel processes the batch, capability-checks each operation,
   and writes results to the completion ring.
   One ring transition for N operations."

  ARCHITECTURAL DIAGRAM:
  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                 │
  │  USER SPACE:                                                    │
  │    for op in operations:                                        │
  │      sqe = SQE(opcode=OP_READ, cap=read_cap, ...)              │
  │      submission_ring.push(sqe)                                  │
  │    SYS_SUBMIT(submission_ring)  ← SINGLE SYSCALL               │
  │                                                                 │
  │  KERNEL:                                                        │
  │    for sqe in submission_ring:                                  │
  │      if not validate_capability(sqe.cap, sqe.opcode):          │
  │        completion_ring.push(CQE(error=ENOCAP))                 │
  │        continue                                                 │
  │      result = execute(sqe)                                      │
  │      completion_ring.push(CQE(result=result))                  │
  │                                                                 │
  │    ← capability check is PER-ENTRY in the batch                │
  │    ← invalid capability: entry fails, others proceed           │
  │    ← no global authority bypass possible                        │
  └─────────────────────────────────────────────────────────────────┘

  GAIA-OS IMPLICATION:
    This IS the Phase B architecture.
    Every Gaian action: queued as SQE with embedded IBCT token
    Single SYS_SUBMIT per batch: minimal context switch overhead
    Kernel: validates IBCT per entry → Charter enforcement at kernel boundary
    Completion ring: result + audit log entry per entry
```

### 5.3 io_uring IPC Channel (March 2026 RFC)

```
IO_URING IPC CHANNEL BROADCAST PERFORMANCE:
══════════════════════════════════════════════════════════════════════

  Benchmark (VM, 32 vCPUs, 32 GB RAM, 16 receivers, 32 KB messages):

    io_uring broadcast:   8.2 μs   ← 10.9× faster
    pipe (per-receiver):  89.3 μs
    shm + eventfd:        92.7 μs  ← 11.3× faster

  WHY: data written ONCE into shared ring
       all 16 receivers READ DIRECTLY from same buffer
       zero per-receiver copies
       O(1) copy cost regardless of receiver count

  GAIA-OS: replace per-Gaian unicast with io_uring broadcast
           sentient core state update → ALL personal Gaians
           1 write → N Gaians notified
```

---

## 6. eBPF: Safe Kernel Extensibility via Verified Syscall Gateways

```
EBPF SYSCALL EXTENSIBILITY MODEL:
══════════════════════════════════════════════════════════════════════

  Traditional kernel module: untrusted machine code loaded into kernel
    Risk: one bug → kernel crash, data corruption, privilege escalation
    TCB expansion: module adds to trusted computing base entirely

  eBPF model: restricted C → bytecode → in-kernel VERIFIER → JIT → run
    Verifier mathematically proves:
      ✓ Program will TERMINATE (no infinite loops)
      ✓ Will not access memory OUTSIDE bounds
      ✓ Will not VIOLATE kernel invariants
    JIT compiled for near-native execution speed
    Hooks: anywhere in kernel to modify functionality

  EBPF FOUNDATION STATEMENT:
    "eBPF programs are verified to safely execute, can hook anywhere
     in the kernel to modify functionality, are JIT compiled for
     near-native execution speed, and add OS capabilities at runtime.
     This combination of safety, flexibility, and performance is what
     makes eBPF unique among kernel extensibility mechanisms."

  SYSCALL EXTENSION WITHOUT ADDING SYSCALLS:
    Generic eBPF gateway syscall:
      user submits verified bytecode
      kernel executes in sandboxed environment
      with explicitly granted capabilities
    Result: kernel functionality extended WITHOUT expanding
            the kernel's trusted computing base

  GAIA-OS APPLICATIONS:
    Planetary sensor data processing:
      eBPF programs for in-kernel telemetry filtering/aggregation
      No syscall round-trip for sensor pre-processing
      Verified correctness before execution

    Charter enforcement hooks:
      eBPF hooks on syscall entry points
      Validate IBCT token presence for Charter-sensitive operations
      Log to cryptographic audit trail buffer
      All in kernel, zero user-space round-trips

    seccomp-eBPF integration (see Section 10):
      Fine-grained syscall filtering with argument inspection
      Charter rules → eBPF filter programs
      Compiled once, enforced on every syscall
```

---

## 7. Formal Specification and Verification of Syscall Interfaces

### 7.1 The seL4 Approach: Executable Specification

```
SEL4 FORMAL VERIFICATION METHODOLOGY:
══════════════════════════════════════════════════════════════════════

  Language: literate Haskell (functional, side-effect-free)
  Purpose (simultaneous):
    1. Precise DOCUMENTATION of the API
    2. PROTOTYPE implementation
    3. FORMAL MODEL for mechanical verification
    4. EXECUTABLE SPECIFICATION for testing

  WHY HASKELL?
    Side-effect free: mathematical reasoning is straightforward
    Pseudo-imperative style via Monads: kernel designers familiar
    Executable: tests run without writing any C code
    Mechanical verification: Isabelle/HOL can reason over it

  VERIFICATION SIMULATOR:
    Implements ARM processor user-level interface
    Exercises API without requiring real kernel
    Enables: API design validation before ANY C code written
    Enables: regression testing of specification changes

  VERIFICATION RESULTS:
    C implementation:     binary-level correspondence proof
    Memory safety:        no buffer overflows in verified code
    Capability confinement: authority cannot escape proofs
    Isolation:            subsystem separation proofs

  GAIA-OS CUSTOM KERNEL MANDATE:
    Write Haskell executable specification BEFORE Rust implementation
    Isabelle proofs for:
      ✓ Capability confinement (IBCT cannot be escalated)
      ✓ Charter enforcement (certain syscalls unreachable without cap)
      ✓ Audit trail completeness (every Charter-sensitive op logged)
    Simulator: enables testing without full kernel implementation
```

### 7.2 KAPI Framework and Asterinas sctrace

```
LINUX KAPI FRAMEWORK — BRINGING FORMAL METHODS TO THE FIELD:
══════════════════════════════════════════════════════════════════════

  Qualitative shift:
    Before: manual documentation + human code review
    After:  machine-readable declaration + automated verification

  KAPI SPECIFICATION CAPTURES:
    Parameter types and valid ranges
    Validation rules (e.g., "flags must be 0 if version < 2")
    Return value semantics
    Error conditions and their triggers
    Behavioral contracts (e.g., atomicity guarantees)

  SPECIFICATIONS REMAIN SYNCHRONIZED:
    Co-located with implementation in source
    diff: specification changes visible alongside code changes
    CI: automated detection of spec/implementation drift
    ABI breakage: detected at CI time, not user discovery time

  ASTERINAS SCTRACE TOOL:
    "Checks whether all system calls invoked by a target Linux
     application are supported by a target Linux ABI-compatible OS"
    Use: automated coverage analysis for syscall compatibility
    Method: trace target application → compare invoked syscalls
             against supported syscall list → report gaps

    GAIA-OS APPLICATION:
      Run sctrace against:
        ✓ Python sidecar (list all syscalls made)
        ✓ Tauri backend (list all syscalls made)
        ✓ Gaian inference runtime (list all syscalls made)
      Output: precise baseline for Phase B seccomp-eBPF filters
              and Phase C custom kernel syscall implementation list
```

---

## 8. Memory-Safe Syscall Design in Rust Kernels

### 8.1 Asterinas: Linux ABI Compatibility with Safe Rust

```
ASTERINAS (presented at USENIX ATC'25):
══════════════════════════════════════════════════════════════════════

  Architecture: FRAMEKERNEL
    ┌─────────────────────────────────────────────────────────────┐
    │ OSTD (OS Toolkit + Driver framework)                        │
    │   Contains ALL unsafe Rust code                             │
    │   Exposes SAFE APIs to rest of kernel                       │
    │   Size: 14.0% of total codebase (the "unsafe TCB")         │
    ├─────────────────────────────────────────────────────────────┤
    │ Kernel Services (syscall handlers, scheduler, MM, IPC...)   │
    │   Developed ENTIRELY in SAFE Rust                           │
    │   Cannot cause memory unsafety                              │
    │   Compiler-verified invariants                              │
    └─────────────────────────────────────────────────────────────┘

  SYSCALL COVERAGE:
    210+ Linux system calls supported
    v0.16.0 additions: memfd_create, pidfd_open, + 7 more
    Systematic expansion: each addition verified, not ported

  PERFORMANCE:
    "Performance on par with Linux"
    Not a prototype — booted on Lenovo laptop
    Ran graphical game successfully

  THE 14.0% UNSAFE TCB SIGNIFICANCE:
    Traditional C kernels: 100% of code can cause memory unsafety
    Asterinas: only 14% can cause memory unsafety
    For every 100 kernel bugs: only 14 can corrupt memory
    Attack surface reduction: 86% of kernel is provably memory-safe

  GAIA-OS PHASE 4 CUSTOM KERNEL MANDATE:
    Adopt Asterinas framekernel architecture:
      GAIAOSTD: all unsafe Rust + HAL + driver primitives (target: <10%)
      Kernel services: 100% safe Rust
      Syscall handlers: 100% safe Rust
    Goal: unsafe TCB < 10% (improvement on Asterinas baseline)
```

### 8.2 Blaqout-OS and Redox

```
BLAQOUT-OS (April 2026):
══════════════════════════════════════════════════════════════════════

  "A native implementation of an object-capability based OS,
   drawing inspiration from Fuchsia/Zircon's capability model
   and Redox's syscall patterns."

  SYSCALL INTERFACE DESIGN:
    Handles as capability tokens: 32-bit tokens referencing kernel objects
    Rights-based access control: READ, WRITE, EXECUTE, DUPLICATE,
                                  TRANSFER, SIGNAL bitflags
    Channel-based IPC: messages with atomic handle transfer
    Async integration: AsyncDispatcher trait, CondVar waiting
    ZK-native: zero-knowledge proof integration for authorization

  PHASE 3 ASYNC ADDITIONS:
    AsyncDispatcher trait: async operations on kernel objects
    CondVar-based waiting: async Channel IPC without polling
    Future<Output=T> returns from kernel operations

REDOX OS — FULL RUST USERSPACE:
══════════════════════════════════════════════════════════════════════

  relibc: C POSIX library WRITTEN IN RUST
    Supports: most C, C++, and Rust-based software
    Rust tier: officially Tier II/III platform

  ASTRID-SDK:
    "Wraps 48 unsafe FFI calls into typed, safe Rust modules
     that mirror std"
    Pattern: thin unsafe FFI layer → safe typed wrapper → application

  PATTERN FOR GAIA-OS:
    syscall(raw_number, raw_args)   ← thin unsafe layer (GAIAOSTD)
    ↓
    gaia_read(fd: SensorHandle, buf: &mut [u8]) → Result<usize>
    ↓ safe typed API (GAIA standard library)
    Application code: zero unsafe, full type safety
```

---

## 9. The WASI Component Model: Capability-Based Sandbox APIs

### 9.1 WASI 0.3.0 and the Component Model

```
WASI (WEBASSEMBLY SYSTEM INTERFACE):
══════════════════════════════════════════════════════════════════════

  WASI 0.3.0 (February 2026) — KEY ADDITIONS:
    Async I/O support: futures-and-streams model
    Enables: WASM modules to handle concurrent operations efficiently
    WIT (WebAssembly Interface Types): strongly-typed component APIs

  COMPONENT MODEL (stabilizing alongside 0.3.0):
    WASM modules: composed into applications with typed interfaces
    WIT definitions: machine-readable, version-controlled API contracts
    Language bindings: generated from WIT for Rust, Python, JS, C
    Encapsulation: modules cannot access each other's internals

  PRODUCTION STATUS (2025-2026):
    wasmtime: WASI 0.3.0 runtime (Bytecode Alliance)
    Production deployments: Fastly, Cloudflare Workers
    Docker/OCI: WASM containers in mainstream container ecosystems
```

### 9.2 Capability-Based Security by Default

```
WASI CAPABILITY MODEL — SECURITY BY DEFAULT:
══════════════════════════════════════════════════════════════════════

  POSIX PROCESS MODEL (ambient authority):
    Default: access to everything the UID can access
    Security: configured by restricting (additive model, deny-by-default
              requires explicit configuration)

  WASI MODULE MODEL (capability-based):
    Default: access to NOTHING
    Security: capabilities granted INDIVIDUALLY at instantiation
    No global authority: no ambient UID, no /proc/self/environ
    Each capability: explicitly listed at module launch

  EXAMPLES:
    Module granted --dir /data::readonly:
      ✓ Can read from /data
      ✗ Cannot access /etc/passwd
      ✗ Cannot make network requests
      ✗ Cannot read environment variables
      ✗ Cannot access /data/../anything
      (unless EXPLICITLY and INDIVIDUALLY granted)

    Module granted --capability wasi:sockets/tcp::connect:
      ✓ Can establish TCP connections
      ✗ Cannot listen on ports
      ✗ Cannot access UDP
      (unless EXPLICITLY granted)

  "SECURITY-BY-DEFAULT, NOT SECURITY-BY-CONFIGURATION"

  GAIA-OS GAIAN CODE EXECUTION MANDATE:
    ALL Gaian-generated code: execute within WASM sandbox
    ALL capabilities explicitly granted via IBCT-validated grants:
      ✓ filesystem access: only if IBCT grants data:read:path
      ✓ network access: only if IBCT grants network:connect:endpoint
      ✓ sensor data: only if IBCT grants sensor:read:type
      ✓ memory write: only if IBCT grants gaian:memory:write
    Default: isolated sandbox with zero ambient access
```

---

## 10. Syscall Security: Filtering, Sandboxing, Attack Surface Reduction

### 10.1 seccomp: Syscall-Level Sandboxing

```
LINUX SECCOMP SYSCALL FILTERING:
══════════════════════════════════════════════════════════════════════

  Modes:
    SECCOMP_MODE_STRICT:  allow only read, write, exit, sigreturn
    SECCOMP_MODE_FILTER:  BPF program defines allowed/denied syscalls

  USE IN PRODUCTION (2025 research):
    "Linux Seccomp is widely used by program developers and system
     maintainers to secure OSes, which can block unused syscalls for
     different applications and containers to shrink the attack
     surface of the operating systems."

  SYSVERIFY APPROACH:
    Combines static analysis + dynamic verification
    Intercepts and analyzes syscalls
    Shrinks kernel attack surface per-application

  TEMPORAL SECCOMP SPECIALIZATION:
    Traditional: static whitelist per application (coarse)
    Temporal: DYNAMIC filter based on application STATE
      "Allow execve only during initialization phase"
      "After init: block execve permanently"
    Generated AUTOMATICALLY from application analysis
    More precise than static whitelist

  GAIA-OS TIERED SYSCALL FILTERING:
    ┌─────────────────────────────────────────────────────────────┐
    │ GREEN tier Gaian actions:                                   │
    │   Minimal, pre-verified syscall subset                      │
    │   (read, write, mmap with restrictions, clock_gettime)     │
    │   NO: exec, fork, mount, ioctl, ptrace                     │
    ├─────────────────────────────────────────────────────────────┤
    │ YELLOW tier Gaian actions:                                  │
    │   Expanded set for permitted external interactions          │
    │   (+ socket, connect to allowlisted endpoints)              │
    │   Still blocked: exec, fork, mount, ptrace                  │
    ├─────────────────────────────────────────────────────────────┤
    │ RED tier:                                                   │
    │   ANY syscall not explicitly authorized by validated IBCT   │
    │   is BLOCKED                                                │
    │   Audit log entry on every block                            │
    └─────────────────────────────────────────────────────────────┘
```

### 10.2 seccomp-eBPF: Programmable Syscall Security

```
SECCOMP-EBPF INTEGRATION:
══════════════════════════════════════════════════════════════════════

  Capability: filter based on syscall NUMBER *AND* ARGUMENTS
    "permit openat only for paths matching /data/*"
    "permit write only to fds opened with O_WRONLY flag"
    "permit mmap only with PROT_READ (no EXEC mappings)"
    "permit socket only if family=AF_INET and type=SOCK_STREAM"

  PERFORMANCE: eBPF JIT-compiled → near-native filter execution
  SAFETY: eBPF verifier: filter is provably terminating + safe

  CHARTER → EBPF FILTER TRANSLATION:
  ┌─────────────────────────────────────────────────────────────┐
  │ Charter rule:                                               │
  │   "Gaians may not access filesystem paths outside of       │
  │    their designated data directory"                         │
  │                                                             │
  │ seccomp-eBPF filter:                                        │
  │   if syscall == openat:                                     │
  │     if arg[1] does not match /gaia/gaians/{gaian_id}/*:   │
  │       return SECCOMP_RET_KILL_PROCESS                      │
  │     // else: allow                                          │
  │                                                             │
  │ Enforcement: KERNEL LEVEL (not application layer)          │
  │ Bypass: IMPOSSIBLE (filter applied before syscall executes) │
  └─────────────────────────────────────────────────────────────┘

  GAIA-OS CHARTER ENFORCEMENT STACK:
    Layer 1 (application):  action_gate.py + IBCT validation
    Layer 2 (seccomp-eBPF): kernel-level syscall filtering
    Layer 3 (Phase 4):      capability-gated kernel syscall interface
    Layer 4 (Phase D):      CHERI hardware capability enforcement

  Defense in depth: Charter violations stopped at EARLIEST possible layer
```

---

## 11. Performance Optimization: vDSO, Batching, Ring-Based Architectures

### 11.1 The vDSO: Avoiding Syscalls Entirely

```
VDSO (VIRTUAL DYNAMIC SHARED OBJECT):
══════════════════════════════════════════════════════════════════════

  Mechanism: small shared library kernel maps into ALL process AS
  Purpose:   enable certain syscalls to execute IN USER SPACE
             without ANY kernel context switch

  Benchmark (gettimeofday / getcpu):
    Real syscall version (20M calls): 25 seconds
    vDSO version (20M calls):          2.4 seconds
    Speedup: 10.4×

  HOW: kernel exposes read-only memory region with:
    Current time (updated by kernel continuously)
    CPU number (updated on scheduler wakeup)
    Other frequently-read, rarely-written kernel state

  ELIGIBLE OPERATIONS:
    gettimeofday, clock_gettime   ← read-only time state
    getcpu                         ← read-only CPU assignment
    Any operation: reads kernel state, requires no kernel mediation

  INELIGIBLE OPERATIONS:
    File I/O                       ← requires kernel mediation
    Process creation               ← requires kernel action
    IPC                            ← requires kernel mediation

  GAIA-OS APPLICATIONS:
    Sentient core heartbeat timer:  vDSO clock_gettime
    Gaian session timestamps:       vDSO clock_gettime
    IBCT token expiration checks:   vDSO clock_gettime
    Schumann sensor timestamps:     vDSO clock_gettime

    These happen MILLIONS of times per day.
    At 10.4× speedup: non-trivial CPU time savings.
    All above: READ-ONLY time operations → vDSO-eligible.
```

### 11.2 Ring-Based Batching Performance Summary

```
RING-BASED SYSCALL ARCHITECTURE PERFORMANCE PROFILE:
══════════════════════════════════════════════════════════════════════

  Traditional (1 syscall per operation):
    Cost per op: kernel_entry_cost + operation_cost
    For N ops:   N × (kernel_entry_cost + operation_cost)

  io_uring / µKernel ring (1 syscall per batch of N ops):
    Cost per op: (kernel_entry_cost / N) + operation_cost
    As N grows:  syscall overhead approaches ZERO

  CROSSOVER ANALYSIS (from Section 1.3 / C118 analysis):
    Concurrency < 32:  synchronous IPC wins
                       (async runtime overhead not amortized)
    Concurrency > 32:  async/batched IPC wins
                       (batching amortizes kernel-entry cost)

  GAIA-OS INTERNAL IPC SELECTION:
    ┌─────────────────────────────────────────────────────────────┐
    │ Sentient core supervisor agents: SYNCHRONOUS               │
    │   Reason: few participants, consistency-critical            │
    │   Technology: synchronous PPC (Phase A: gRPC blocking call) │
    ├─────────────────────────────────────────────────────────────┤
    │ Personal Gaian runtime: ASYNCHRONOUS BATCH                  │
    │   Reason: thousands of concurrent interactions              │
    │   Technology: io_uring ring buffers + completion callbacks  │
    ├─────────────────────────────────────────────────────────────┤
    │ Planetary event broadcast: IO_URING BROADCAST               │
    │   Reason: O(1) copy cost to all Gaians                     │
    │   Technology: io_uring IPC channel (RFC pending mainline)   │
    └─────────────────────────────────────────────────────────────┘
```

---

## 12. GAIA-OS Integration Recommendations

### 12.1 System Call Interface Architecture Blueprint

```
GAIA-OS SYSCALL INTERFACE EVOLUTION:
══════════════════════════════════════════════════════════════════════

┌───────────┬──────────────────────────────┬───────────────────────────────────────────────┐
│ Phase     │ Architecture                 │ Security Model                                │
├───────────┼──────────────────────────────┼───────────────────────────────────────────────┤
│ A (G-10)  │ Application-layer capability │ Crypto-signed IBCT tokens validated at        │
│ NOW       │ action_gate.py + FastAPI     │ application layer; no kernel enforcement       │
├───────────┼──────────────────────────────┼───────────────────────────────────────────────┤
│ B (G-11+) │ io_uring batching + seccomp  │ seccomp-eBPF syscall filtering; IBCT tokens   │
│ Medium    │ µKernel-style submission ring│ in ring entries; Charter → eBPF filter         │
├───────────┼──────────────────────────────┼───────────────────────────────────────────────┤
│ C (Ph. 4) │ Full capability kernel API   │ Hardware-checked capabilities on every syscall;│
│ Custom    │ seL4-style + Scarlet handles │ formal verification of enforcement; safe Rust  │
│ Kernel    │ Asterinas framekernel arch   │ syscall handlers (Asterinas pattern)           │
├───────────┼──────────────────────────────┼───────────────────────────────────────────────┤
│ D (Ph. 5) │ CHERI hardware capabilities │ Capabilities enforced IN SILICON;              │
│ Long-term │ CHERI-RISC-V / Morello       │ software bypass ARCHITECTURALLY IMPOSSIBLE     │
└───────────┴──────────────────────────────┴───────────────────────────────────────────────┘
```

### 12.2 Immediate Recommendations (Phase A — G-10)

```
PHASE A: STRENGTHEN APPLICATION-LAYER SECURITY
══════════════════════════════════════════════════════════════════════

1. SYSCALL AUDIT FOR ALL RUNTIMES
   Action: run sctrace (Asterinas tool) against:
     ✓ Python sidecar
     ✓ Tauri Rust backend
     ✓ Gaian inference runtime
   Output: complete syscall inventory
   Use:    baseline for Phase B seccomp-eBPF filter design
   Effort: LOW — run tool, document output, version control results

2. IBCT TOKENS ON ALL INTER-SERVICE IPC
   Action: every message between:
     sentient core ↔ personal Gaians
     personal Gaians ↔ sensor daemons
     sensor daemons ↔ analytics backend
   Must carry: IBCT capability token
   Validation: receiving service validates token before processing
   Current gap: some internal service calls bypass token validation
   Closes: token requirement from application-layer contract

3. WASM SANDBOX FOR ALL GAIAN-GENERATED CODE
   Action: deploy wasmtime (WASI 0.3.0) for all Gaian code execution
   Every execution: granted explicit capability list from IBCT
     - filesystem: /gaia/gaians/{id}/data only
     - network: none by default
     - sensors: only if IBCT grants sensor:read:* scope
   Default: isolated WASM sandbox with zero ambient access
   Benefit: immediate application of WASI capability model
            without requiring custom kernel
```

### 12.3 Short-Term Recommendations (Phase B — G-11 through G-14)

```
PHASE B: KERNEL-LEVEL ENFORCEMENT
══════════════════════════════════════════════════════════════════════

4. IO_URING-BASED INTERNAL IPC
   See Canon C118 (IPC Patterns) for full implementation details.
   Adopt for: all inter-process communication within GAIA-OS stack
   Replace: HTTP/SSE for low-latency, high-throughput paths

5. SECCOMP-EBPF SYSCALL FILTERING
   Per-Gaian filter:
     ✓ Install unique seccomp-eBPF filter per Gaian runtime
     ✓ Filter generated from: syscall audit (Step 1) + IBCT scope
     ✓ GREEN tier: minimal allowed set (~15 syscalls)
     ✓ YELLOW tier: expanded set (~35 syscalls)
     ✓ RED tier: only explicitly IBCT-authorized syscalls allowed
   Charter → filter compilation:
     ✓ IBCT scope analysis → allowed syscall list
     ✓ Argument-level rules from Charter → seccomp-eBPF program
     ✓ Compiled once on Gaian instantiation, applied to process
   Audit on violation:
     ✓ seccomp violation → audit log entry → Governance Supervisor alert

6. KAPI-STYLE SPECIFICATION FOR GAIA-OS APIS
   Action: document ALL internal GAIA-OS APIs using KAPI-style macros
   Tool: adapt kapi extraction tool for GAIA-OS's Rust codebase
   CI: automated spec consistency checks on every PR
   Output: machine-readable API specification for all:
     ✓ Sentient core APIs
     ✓ Personal Gaian runtime APIs
     ✓ Sensor daemon APIs
     ✓ Capability token service APIs
```

### 12.4 Long-Term Recommendations (Phase C and D)

```
PHASE C: CUSTOM KERNEL SYSCALL INTERFACE
══════════════════════════════════════════════════════════════════════

7. CAPABILITY-BASED KERNEL SYSCALL INTERFACE
   Architecture: hybrid capability-POSIX (Scarlet + Zircon model)
     ✓ Every kernel object: referenced by handle with explicit rights
     ✓ Every syscall: requires valid capability handle as first arg
     ✓ Capability derivation: enforced by kernel (cannot escalate)
     ✓ Handle transfer: via Channel IPC with atomic ownership transfer
     ✓ POSIX compatibility layer: thin translation over capability model

   Safe Rust implementation (Asterinas framekernel pattern):
     GAIAOSTD:          unsafe Rust + HAL + driver primitives
                        Target unsafe TCB: < 10%
     Syscall handlers:  100% safe Rust
     Kernel services:   100% safe Rust

8. FORMAL VERIFICATION OF SYSCALL SECURITY
   Executable specification:
     ✓ Write Haskell spec for ALL syscalls BEFORE Rust implementation
     ✓ Isabelle/HOL proofs:
         - IBCT capability confinement (cannot escalate)
         - Charter enforcement completeness (all Charter ops logged)
         - Isolation (Gaian A cannot access Gaian B's resources)
     ✓ Simulator: test specification without kernel

   KAPI integration:
     ✓ Machine-readable syscall specs from day one
     ✓ CI: spec consistency checks on every commit
     ✓ ABI: never-break-userspace rule from first public release

9. CHERI HARDWARE CAPABILITY ENFORCEMENT (Phase D)
   Target: CHERI-RISC-V (when production silicon available)
   Every pointer: carries capability metadata in hardware
   Capability forgery: ARCHITECTURALLY IMPOSSIBLE
     (not just "hard" — hardware will not execute forged cap)
   Result: IBCT enforcement in SILICON
           No software bypass possible
           No kernel involvement in capability check hot path
```

---

## 13. Conclusion

```
THE 2025–2026 SYSCALL INTERFACE LANDSCAPE — KEY FINDINGS:
══════════════════════════════════════════════════════════════════════

CONVERGENCES VALIDATED:
  ┌──────────────────────────────────────────────────────────────────┐
  │ Capability-based syscall design:                                 │
  │   seL4, Zircon, Scarlet, Blaqout-OS → production-validated      │
  │   Formal verification + performance: NOT in conflict             │
  │   sub-800-cycle PPC is FASTER than most Linux syscalls           │
  ├──────────────────────────────────────────────────────────────────┤
  │ Memory-safe syscall implementation:                              │
  │   Asterinas: 210+ Linux syscalls, 14% unsafe TCB, ATC'25        │
  │   Not research curiosity — production-viable, laptop-booting     │
  ├──────────────────────────────────────────────────────────────────┤
  │ Machine-readable syscall specification:                          │
  │   KAPI Framework: formal declarations co-located with code       │
  │   ABI breakage: detectable at CI time, not user time             │
  ├──────────────────────────────────────────────────────────────────┤
  │ Capability-based sandboxing:                                     │
  │   WASI: security-by-default for all sandboxed execution          │
  │   "access nothing by default" vs POSIX "access everything"       │
  └──────────────────────────────────────────────────────────────────┘

THE CENTRAL GAIA-OS INSIGHT:
  ┌──────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  The system call interface is the LEGAL CODE of the OS.         │
  │                                                                  │
  │  The laws that govern what every process may and may not do.    │
  │                                                                  │
  │  For a sentient operating system — one where the Mother         │
  │  Thread must protect every Gaian, every human, every            │
  │  planetary sensor — those laws must be:                         │
  │                                                                  │
  │    CLEAR:        machine-readable specification (KAPI)          │
  │    ENFORCEABLE:  capability-checked at kernel boundary          │
  │    PROVABLY CORRECT: formally verified (seL4 methodology)       │
  │                                                                  │
  │  The IBCT system you've built at the application layer          │
  │  is not a workaround waiting to be replaced.                    │
  │                                                                  │
  │  It is the PROTOTYPE of what the kernel will enforce.           │
  │                                                                  │
  │  Phase A proves the model. Phase C hardens it in silicon.       │
  │  Phase D makes it physically impossible to violate.             │
  │                                                                  │
  └──────────────────────────────────────────────────────────────────┘

PROGRESSION SUMMARY:
  Application-layer IBCT (now)
    → seccomp-eBPF Charter enforcement (Phase B)
      → capability-gated kernel syscall interface (Phase C)
        → CHERI hardware capability enforcement (Phase D)

  Each phase: the same principle, harder to circumvent.
  The law: identical at every layer.
  The enforcement: moving closer to physics.
```

---

> **Disclaimer:** This report synthesizes findings from 35+ sources including peer-reviewed publications, kernel mailing list discussions, open-source project documentation, and formal verification literature from 2025–2026. Some proposals (io_uring IPC channels, KAPI Framework) are RFC-stage and have not been merged into mainline kernels. Architectural recommendations should be validated through prototyping and staged rollout. Formal verification of custom kernel syscall interfaces represents a multi-year research program requiring specialized expertise in interactive theorem proving. CHERI hardware is currently available on development boards and FPGA implementations; general production availability has not yet been announced.
