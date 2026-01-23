package main

import (
	"fmt"
	"io"
	"os"
	"unicode"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: wc <filename>")
		os.Exit(1)
	}

	filename := os.Args[1]
	file, err := os.Open(filename)
	if err != nil {
		fmt.Printf("Error opening file: %v\n", err)
		os.Exit(1)
	}
	defer file.Close()

	var lines, words, chars int64
	inWord := false

	// Reading byte by byte (or buffering)
	// For performance, bufio.Reader is better, but let's just read chunks.
	buf := make([]byte, 4096)
	
	for {
		n, err := file.Read(buf)
		if n > 0 {
			chars += int64(n)
			for i := 0; i < n; i++ {
				b := buf[i]
				
				if b == '\n' {
					lines++
				}

				if unicode.IsSpace(rune(b)) {
					inWord = false
				} else if !inWord {
					inWord = true
					words++
				}
			}
		}
		if err == io.EOF {
			break
		}
		if err != nil {
			fmt.Printf("Error reading file: %v\n", err)
			os.Exit(1)
		}
	}

	fmt.Printf(" Lines: %d\n Words: %d\n Chars: %d\n File:  %s\n", lines, words, chars, filename)
}