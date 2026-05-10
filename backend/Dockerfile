FROM rust:latest as builder
WORKDIR /app
COPY . .
# Pin problematic dependencies to versions compatible with Rust 1.84/1.85
RUN cargo update -p time --precise 0.3.36 || true
RUN cargo update -p home --precise 0.5.11 || true
RUN cargo build --release

FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/target/release/pontevpn-backend .
EXPOSE 3000
CMD ["./pontevpn-backend"]
