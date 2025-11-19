# Dockerfile for Hyperbolic Semantic Networks
# Provides reproducible environment for all analyses

FROM julia:1.9

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /workspace

# Copy project files
COPY julia/Project.toml julia/Manifest.toml julia/
COPY rust/Cargo.toml rust/
COPY rust/*/Cargo.toml rust/*/

# Install Julia dependencies
RUN julia --project=julia -e 'using Pkg; Pkg.instantiate()'

# Install Rust dependencies
WORKDIR /workspace/rust
RUN cargo fetch

# Copy source code
WORKDIR /workspace
COPY . .

# Build Rust libraries
WORKDIR /workspace/rust
RUN cargo build --release

# Set default command
WORKDIR /workspace
CMD ["julia", "--project=julia"]

