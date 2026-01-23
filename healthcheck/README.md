# Healthcheck - Service Watcher

A real-time, concurrent service monitor that provides a live dashboard of your endpoints.

## Summary
`healthcheck` pings a list of URLs and displays their status, latency, and uptime in a clean, self-refreshing terminal UI.

## Installation
Requires [Go](https://go.dev/).
```bash
# Compile the binary
go build healthcheck.go
```

## Usage
Run the tool with a list of URLs to monitor:
```bash
./healthcheck https://google.com https://github.com http://localhost:8080
```
The dashboard refreshes every 3 seconds. Press `Ctrl+C` to exit.
