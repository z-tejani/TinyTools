package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <filename.md>\n", os.Args[0])
		os.Exit(1)
	}

	inputFile := os.Args[1]

	if !strings.HasSuffix(inputFile, ".md") {
		fmt.Fprintln(os.Stderr, "Error: Input file must be a .md file.")
		os.Exit(1)
	}

	if _, err := os.Stat(inputFile); os.IsNotExist(err) {
		fmt.Fprintf(os.Stderr, "Error: File not found: %s\n", inputFile)
		os.Exit(1)
	}

	baseName := strings.TrimSuffix(inputFile, filepath.Ext(inputFile))
	
	// Define paths for the intermediate and final files
	htmlFile := baseName + "-temp.html"
	pdfFile := baseName + ".pdf"

	defer func() {
		fmt.Println("Cleaning up temporary files...")
		os.Remove(htmlFile)
	}()

	fmt.Println("Converting", inputFile, "to HTML...")
	// Create the command: python3 -m markdown -x "extra" [input] -o [output]
	mdCmd := exec.Command("python3", "-m", "markdown", "-x", "extra", inputFile, "-o", htmlFile)
	
	if output, err := mdCmd.CombinedOutput(); err != nil {
		fmt.Fprintf(os.Stderr, "Error converting to HTML: %v\n%s", err, string(output))
		os.Exit(1)
	}

	fmt.Println("Converting HTML to PDF...")
	// Create the command: textutil -convert pdf [input] -output [output]
	pdfCmd := exec.Command("textutil", "-convert", "pdf", htmlFile, "-output", pdfFile)

	// Run the command and check for errors
	if output, err := pdfCmd.CombinedOutput(); err != nil {
		fmt.Fprintf(os.Stderr, "Error converting to PDF: %v\n%s", err, string(output))
		os.Exit(1)
	}


	fmt.Println("Successfully created", pdfFile)
}