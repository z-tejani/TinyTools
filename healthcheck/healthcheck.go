package main

import (
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"runtime"
	"sort"
	"strings"
	"sync"
	"text/tabwriter"
	"time"
)

// Result holds the status of a single check
type Result struct {
	URL     string
	Status  string
	Latency time.Duration
	Up      bool
	Error   error
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: healthcheck <url1> <url2> ...")
		fmt.Println("Example: healthcheck https://google.com http://localhost:8080")
		os.Exit(1)
	}

	urls := os.Args[1:]
	// Validate URLs (rudimentary)
	for i, u := range urls {
		if !strings.HasPrefix(u, "http") {
			urls[i] = "http://" + u
		}
	}

	fmt.Printf("Starting healthcheck for %d services...\n", len(urls))
	time.Sleep(1 * time.Second)

	// Create a ticker for the refresh loop
	ticker := time.NewTicker(3 * time.Second)
	defer ticker.Stop()

	// Initial run
	checkAndPrint(urls)

	for range ticker.C {
		checkAndPrint(urls)
	}
}

func checkAndPrint(urls []string) {
	var wg sync.WaitGroup
	results := make([]Result, len(urls))

	for i, u := range urls {
		wg.Add(1)
		go func(index int, url string) {
			defer wg.Done()
			results[index] = check(url)
		}(i, u)
	}

	wg.Wait()

	// Clear screen
	clearScreen()

	// Print Header
	fmt.Printf("Health Check Dashboard - %s\n", time.Now().Format("15:04:05"))
	fmt.Println(strings.Repeat("-", 60))

	// Setup tab writer
	w := tabwriter.NewWriter(os.Stdout, 0, 0, 3, ' ', 0)
	fmt.Fprintln(w, "STATUS\tURL\tLATENCY\tMSG")

	// Sort results to keep order consistent if we wanted, but index preservation is enough
	// Actually, preserving the input order is better for the user
	
	for _, r := range results {
		statusIcon := "🟢" // Green circle
		if !r.Up {
			statusIcon = "🔴" // Red circle
		} else if r.Latency > 500*time.Millisecond {
			statusIcon = "🟡" // Yellow circle for slow
		}

		msg := r.Status
		if r.Error != nil {
			msg = fmt.Sprintf("Error: %v", r.Error)
			// Truncate long errors
			if len(msg) > 30 {
				msg = msg[:27] + "..."
			}
		}

		fmt.Fprintf(w, "%s\t%s\t%s\t%s\n", statusIcon, r.URL, r.Latency.Round(time.Millisecond), msg)
	}
	w.Flush()
	fmt.Println(strings.Repeat("-", 60))
	fmt.Println("Press Ctrl+C to exit")
}

func check(url string) Result {
	start := time.Now()
	client := http.Client{
		Timeout: 2 * time.Second,
	}
	
	resp, err := client.Get(url)
	latency := time.Since(start)

	if err != nil {
		return Result{
			URL:     url,
			Up:      false,
			Latency: latency,
			Error:   err,
		}
	}
	defer resp.Body.Close()

	up := resp.StatusCode >= 200 && resp.StatusCode < 400
	
	return Result{
		URL:     url,
		Status:  resp.Status,
		Latency: latency,
		Up:      up,
	}
}

func clearScreen() {
	if runtime.GOOS == "windows" {
		cmd := exec.Command("cmd", "/c", "cls")
		cmd.Stdout = os.Stdout
		cmd.Run()
	} else {
		fmt.Print("\033[H\033[2J")
	}
}
