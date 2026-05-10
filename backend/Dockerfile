FROM rustlang/rust:nightly as builder
WORKDIR /app
COPY . .
RUN cargo build --release

FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/target/release/pontevpn-backend .
EXPOSE 3000
CMD ["./pontevpn-backend"]
