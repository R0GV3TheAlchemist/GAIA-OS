# 📜 Assembly Language: Boot Process & Kernel Initialization — A Comprehensive 2025/2026 Survey for GAIA-OS

**Date:** May 1, 2026
**Status:** Comprehensive Technical Survey
**Relevance to GAIA-OS:** This report provides the definitive survey of assembly language's critical role in the boot and initialization of modern computing platforms — the foundational layer upon which every operating system service, including GAIA-OS's eventual Phase 4 custom kernel, will be built.

---

## Executive Summary

Assembly language remains the bedrock of systems programming and the sole mechanism for initializing a CPU from its power-on default state into a controlled environment capable of running the rest of the system. The 2025–2026 period shows assembly evolving — not as a tool for writing entire systems, but as the critical, minimal, and increasingly verifiable interface between hardware and a new generation of memory-safe, high-level systems languages like Rust.

The central finding for GAIA-OS is that the Phase 4 custom kernel needs a small, formal, and architecture-specific assembly foundation module (`arch/`) responsible for entry points, register initialization, and `#[naked]` functions handling the earliest CPU bring-up — with all higher-level initialization delegated to safe Rust.

---

## Table of Contents

1. [The Role of Assembly in the Boot Process](#1-boot-process)
2. [x86-64 Assembly: CPU Init, GDT, IDT, and Paging](#2-x86-64)
3. [ARM64 Assembly for Bootloaders and Low-Level CPU Control](#3-arm64)
4. [The Rust-Assembly Nexus: Memory-Safe Bootloaders](#4-rust-assembly)
5. [The UEFI Application Layer](#5-uefi)
6. [Formal Verification of Assembly Code](#6-formal-verification)
7. [GAIA-OS Integration Recommendations](#7-recommendations)
8. [Conclusion](#8-conclusion)

---

## 1. The Role of Assembly in the Boot Process

The power-on sequence of a modern computer is a deterministic, multi-stage process that relies fundamentally on assembly code, particularly in its earliest phases. Two distinct paradigms define the state of the art.

### 1.1 Legacy BIOS Booting

In a legacy BIOS system the process begins with the CPU executing a hard-coded reset vector. The system loads the first sector of the boot device (the MBR) into memory at physical address `0x7C00` and transfers control to it. This initial code is typically a 512-byte flat binary written entirely in 16-bit assembly. Its primary task is not to load the OS directly but to locate, load, and execute a second-stage bootloader.

Key constraints:
- 512-byte size limit — precludes complex logic and file-system drivers
- Must be position-independent
- Relies on legacy BIOS interrupt calls (e.g., `INT 0x13`) for disk reads

### 1.2 UEFI Booting

UEFI firmware is a sophisticated, standardized OS in its own right. On x86-64, it starts the CPU in 64-bit long mode, providing full 64-bit memory addressability from the outset. The firmware locates a FAT-formatted EFI System Partition (ESP) and loads a Portable Executable (PE) file — the UEFI application (e.g., `BOOTX64.EFI`).

The UEFI application can be written in C, C++, or Rust and can leverage UEFI firmware protocols for graphics, networking, and file I/O. The initial **SEC (Security)** and **PEI (Pre-EFI Initialization)** phases — which run before the UEFI application is loaded — are implemented in assembly because they operate with extremely limited resources, often using the CPU cache as temporary RAM before main memory is initialized.

The Slim Bootloader project illustrates this staged progression:
- **Stage 1A**: Assembly handles the switch from 16-bit real mode to 32-bit protected mode, sets up a temporary stack, and jumps to C code for further initialization.

---

## 2. x86-64 Assembly: CPU Init, GDT, IDT, and Paging

Modern x86-64 CPUs start in 16-bit "real mode" to maintain backward compatibility with the original 8086. A bootloader's primary job is to transition the CPU through 32-bit "protected mode" into 64-bit "long mode," setting up the foundational hardware structures necessary for a kernel to operate.

### 2.1 The Mode Transition Sequence

The transition from real mode to long mode is a carefully orchestrated sequence:

**Step 1 — Real Mode → Protected Mode:**
1. Set up a Global Descriptor Table (GDT) defining memory segments
2. Set the Protection Enable (PE) bit in Control Register 0 (`CR0`)
3. Execute a far jump to flush the instruction pipeline and load the new code segment selector

**Step 2 — Enable 64-bit Long Mode:**
1. Create minimal page tables (PML4 → PDPT → PD → PT) for identity mapping
2. Enable PAE bit in `CR4`
3. Load the PML4 physical address into `CR3`
4. Set the Long Mode Enable (LME) bit in the EFER MSR
5. Set the Paging (PG) bit in `CR0`
6. Execute a far jump to a 64-bit code segment — long mode is now active

> **UEFI simplification**: UEFI firmware handles this entire transition and presents the bootloader with a stable 64-bit environment including a basic UEFI-provided GDT and IDT. The kernel only needs to replace these with its own versions during initialization.

### 2.2 Setting Up the GDT and IDT

**Global Descriptor Table (GDT):**
- In long mode, the GDT uses a flat memory model (base = 0, limit = full 4GB)
- The Task State Segment (TSS) is a related GDT structure used for stack switching during privilege level changes
- The `LGDT` instruction loads the GDT Register (GDTR)

**Interrupt Descriptor Table (IDT):**
- In long mode, IDT entries are 16 bytes each
- A basic IDT must be set up at boot to catch processor exceptions; the kernel replaces it later with a full implementation
- The `LIDT` instruction loads the IDT Register (IDTR) with the base address and size

### 2.3 Setting Up Paging in Long Mode

Long mode uses a four-level hierarchical paging structure. The bootloader must:

1. Allocate physical memory for each level: **PML4**, **PDPT**, **PD**, and **PT**
2. Populate entries to create an **identity mapping** for at least the first few megabytes — critical because when paging is first enabled, the instruction pointer continues incrementing and must find the next instruction at the same virtual address it was physically executing from
3. Set `CR3` to the physical address of the PML4 table
4. Enable paging by setting the PG bit in `CR0`

---

## 3. ARM64 Assembly for Bootloaders and Low-Level CPU Control

The ARM64 (AArch64) architecture powers billions of mobile devices and a growing share of servers and laptops. It has a distinct set of conventions for booting and low-level control.

### 3.1 The Boot Process on ARM64

Unlike x86's multi-step relay race, an ARM64 system typically starts with the CPU coming out of reset at a high exception level — EL3 (Secure Monitor) or EL2 (Hypervisor). Boot firmware (Trusted Firmware-A, U-Boot, etc.) initializes the hardware and passes control to the kernel at a lower exception level (EL1 or EL2) with the MMU off.

The Linux kernel's ARM64 entry point expects:
- Physical address mode with the MMU off
- A pointer to the Device Tree Blob (DTB) in register `x0`

The `primary_entry` routine is pure assembly responsible for:
- Initializing the CPU for the kernel environment
- Turning on the MMU
- Building the initial virtual address space

### 3.2 Key Architectural Differences from x86-64

| Aspect | x86-64 | ARM64 |
|--------|--------|-------|
| General-purpose registers | 16 × 64-bit (RAX…R15) | 31 × 64-bit (X0…X30) |
| Page table register | `CR3` | `TTBR0_EL1` / `TTBR1_EL1` |
| System control register | `CR0` | `SCTLR_EL1` |
| Descriptor syntax | Intel or AT&T | AArch64 (ARM syntax) |
| Boot privilege level | Real Mode (Ring 0) | EL3/EL2 → EL1 |

The low-level bring-up code for GAIA-OS must be **separately and carefully implemented for both x86-64 and ARM64** — the assembly is not portable between the two ISAs.

---

## 4. The Rust-Assembly Nexus: Memory-Safe Bootloaders

A major architectural trend in 2025–2026 is using Rust to build bootloaders that are both high-performance and memory-safe, eliminating security vulnerabilities endemic to traditional C bootloaders.

### 4.1 Rust Inline Assembly: `asm!` and `#[naked]`

Rust's `core::arch::asm!` macro embeds assembly instructions directly within Rust code, eliminating the need for separate `.S` files in many cases:

```rust
use core::arch::asm;

// Load a GDT
unsafe {
    asm!(
        "lgdt [{gdt_ptr}]",
        gdt_ptr = in(reg) &gdt_descriptor,
        options(nostack, preserves_flags)
    );
}
```

The `#[naked]` function attribute prevents the compiler from inserting any prologue or epilogue, giving full control over entry points — essential for interrupt handlers and kernel entry points that must control the stack precisely:

```rust
#[naked]
unsafe extern "C" fn kernel_entry() -> ! {
    asm!(
        "mov rsp, {stack_top}",
        "call kernel_main",
        stack_top = const KERNEL_STACK_TOP,
        options(noreturn)
    );
}
```

### 4.2 The `bootloader` Crate

The `bootloader` crate (v0.11) provides an experimental, pure-Rust x86_64 bootloader compatible with both BIOS and UEFI systems. It builds on all platforms and creates FAT-formatted bootable disk images. Usage:

1. Add `bootloader_api` as a kernel dependency
2. Compile the kernel to an ELF executable
3. Use the `bootloader` crate to produce a bootable image

### 4.3 `towboot`: The Rust Alternative to GRUB

Presented at FG-BS Frühjahrstreffen 2026, `towboot` is a Multiboot-compatible bootloader for UEFI-based x86 and x86_64 systems written in Rust. Context: GRUB has 300,000 lines of C/C++ and 64,000 lines of assembly with numerous documented memory safety violations. `towboot` demonstrates that memory-safe booting is a practical engineering reality, not a theoretical aspiration.

### 4.4 `CosmOS`

`CosmOS` is a bare-metal kernel and bootloader written entirely in Rust and assembly. It implements:
- Strict separation of hardware-enforced privilege levels (Ring 0 and Ring 3)
- Rust's ownership model as a core security principle
- NASM assembler for low-level routines
- Support for both BIOS and UEFI booting

### 4.5 The `x86_commands` Library

The `x86_commands` library provides inline assembly wrappers for x86 and x86_64 CPU instructions using `core::arch::asm!`, specifically designed for use in OS kernels and bootloaders.

---

## 5. The UEFI Application Layer

Writing a UEFI application differs significantly from writing a traditional bootloader. A UEFI application is a standard PE32+ executable loaded and called by the firmware. It can be written without any assembly language at all, provided the language can generate a PE executable and interface with the UEFI calling convention.

### 5.1 Development Environments

| Toolkit | Language Support | Notes |
|---------|-----------------|-------|
| EDK2 | C, C++ | Official reference implementation from Intel/TianoCore |
| GNU-EFI | C | Lightweight GNU toolchain integration |
| `uefi` Rust crate | Rust | Idiomatic Rust bindings for UEFI services |
| `clang` + mingw | C/C++ | Standard compilers targeting UEFI PE format |

The `queso-fuego/uefi-dev` repository (2026) demonstrates that standard compilers like `clang` and `x86_64-w64-mingw32-gcc` can produce working UEFI applications with minimal configuration.

### 5.2 Pure Assembly UEFI

The `Zaxxon` game project demonstrates an extreme case: an entire game written in x86-64 assembler to run as a standalone UEFI application, highlighting the potential of pure assembly for direct hardware control within the UEFI environment.

---

## 6. Formal Verification of Assembly Code

Given the catastrophic consequences of a bug in the assembly-level boot sequence, the field is pushing toward formal verification of assembly code.

### 6.1 Verified ARM Bootloaders

A seminal paper demonstrated functional verification of a real-world IoT operating system's bootloader for ARM-based devices, verifying both C libraries and the critical assembly boot sequence. The methodology:

1. Define a formal specification of the ARM ISA in the **F* programming language**
2. Use verified programming techniques to prove the correctness of the assembly code against that specification

This demonstrates a mathematically proven bridge from silicon to a safe, high-level kernel.

### 6.2 The Verification Gap

The gap between "assembly we believe is correct" and "assembly we have proved is correct" is significant. Tools like Frama-C (for C/assembly interop), the K Framework (for ISA semantics), and Iris-style separation logic for low-level code are advancing the state of the art. For GAIA-OS Phase 4, the assembly foundation module should be scoped to be small enough to be a candidate for formal verification — a few hundred lines of carefully commented, minimal bring-up code.

---

## 7. GAIA-OS Integration Recommendations

### 7.1 The Recommended Hybrid Architecture

```
arch/
├── x86_64/
│   ├── entry.asm         # #[naked] entry point, mode transition
│   ├── gdt.rs            # GDT/TSS setup in safe Rust
│   ├── idt.rs            # IDT setup in safe Rust
│   └── paging.rs         # Page table construction in safe Rust
├── aarch64/
│   ├── entry.asm         # ARM64 primary_entry equivalent
│   ├── mmu.rs            # MMU enable and TTBR setup in safe Rust
│   └── exceptions.rs     # Exception level configuration
└── common/
    └── boot.rs           # Shared boot protocol (UEFI/BIOS detection)
```

The philosophy: **assembly is the minimal interface to the hardware**. Every line of assembly should have a precisely defined postcondition that Rust code can rely on. The assembly surface should be small enough to be manually audited and eventually formally verified.

### 7.2 Immediate Recommendations (Phase A — G-10)

| Priority | Action | Rationale |
|----------|--------|-----------|
| **P0** | Implement `arch/x86_64/entry.asm` using `#[naked]` functions and `core::arch::asm!` | Establishes memory-safe Rust entry point with precisely scoped assembly footprint |
| **P0** | Target the `bootloader` crate for BIOS/UEFI dual-target disk image generation | Eliminates custom bootloader maintenance burden during early phases |
| **P1** | Implement `arch/aarch64/entry.asm` for ARM64 target | Required for Apple Silicon, Raspberry Pi, and server ARM64 deployment |
| **P1** | Document assembly postconditions as inline Rust safety contracts | Makes the C-Rust-assembly trust frontier auditable |
| **P2** | Scope the assembly surface for eventual F*-style formal verification | Keep the assembly module small enough to be a verification candidate |

### 7.3 Short-Term Recommendations (Phase B — G-11 through G-14)

| Priority | Action | Rationale |
|----------|--------|-----------|
| **P1** | Replace GDT/IDT/paging setup with safe Rust wrappers above the `#[naked]` entry | Maximizes Rust memory-safety guarantees from the earliest possible point |
| **P2** | Evaluate `towboot` as a reference design for the GAIA-OS UEFI bootloader | Provides a documented, memory-safe alternative to GRUB's 300k-line C/asm codebase |
| **P3** | Integrate formal ISA specification for the GAIA-OS assembly boot sequences | F*-based or K-framework-based ISA spec enables proof of correctness for the most critical code path |

### 7.4 Long-Term Recommendations (Phase C — Phase 4+)

- **Dual-ISA verified foundation**: Formally verify both the x86-64 and ARM64 assembly entry modules before the Phase 4 kernel is declared production-ready
- **`#[naked]` surface minimization**: Drive the assembly surface toward the absolute minimum — entry point, stack setup, and MMU enable — with all other initialization in safe Rust

---

## 8. Conclusion

Assembly language remains the bedrock of systems programming, serving as the only bridge between the inert silicon of a CPU and the abstract logic of an operating system. The 2025–2026 period shows that assembly is evolving — not as a tool for writing entire systems but as the critical, minimal, and verifiable interface between hardware and a new generation of memory-safe, high-level systems languages like Rust.

The future of assembly in OS development is as a precise, powerful, and increasingly verified instrument: scoped to the smallest possible surface area, documented with formal postconditions, and serving as the launch platform for safe Rust code from the very first instruction cycle. GAIA-OS's Phase 4 kernel should embrace this philosophy from day one.

---

**Disclaimer:** This report synthesizes findings from 17 technical sources including academic papers, project documentation, and developer guides from 2025–2026. Assembly language programming is inherently architecture-specific; code examples and conventions for x86-64 will not function on ARM64 without significant adaptation. The `bootloader`, `towboot`, and `CosmOS` projects are actively developed and their APIs may change. Formal verification of assembly code is a complex research program requiring specialized expertise in theorem proving and ISA semantics.
