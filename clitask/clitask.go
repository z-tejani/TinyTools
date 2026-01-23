package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

const todoFile = "TODO.md"

func main() {
	if len(os.Args) < 2 {
		printUsage()
		return
	}

	command := os.Args[1]

	switch command {
	case "add":
		if len(os.Args) < 3 {
			fmt.Println("Usage: clitask add <task description>")
			return
		}
		task := strings.Join(os.Args[2:], " ")
		addTask(task)
	case "ls", "list":
		listTasks()
	case "done", "check":
		if len(os.Args) < 3 {
			fmt.Println("Usage: clitask done <task number>")
			return
		}
		index, err := strconv.Atoi(os.Args[2])
		if err != nil {
			fmt.Println("Error: Task number must be an integer.")
			return
		}
		markTask(index, true)
	case "undo":
		if len(os.Args) < 3 {
			fmt.Println("Usage: clitask undo <task number>")
			return
		}
		index, err := strconv.Atoi(os.Args[2])
		if err != nil {
			fmt.Println("Error: Task number must be an integer.")
			return
		}
		markTask(index, false)
	case "rm", "remove", "del":
		if len(os.Args) < 3 {
			fmt.Println("Usage: clitask rm <task number>")
			return
		}
		index, err := strconv.Atoi(os.Args[2])
		if err != nil {
			fmt.Println("Error: Task number must be an integer.")
			return
		}
		removeTask(index)
	case "clear":
		// Remove completed tasks
		clearCompleted()
	default:
		printUsage()
	}
}

func printUsage() {
	fmt.Println("Usage: clitask <command> [arguments]")
	fmt.Println("Commands:")
	fmt.Println("  add <text>   Add a new task")
	fmt.Println("  ls           List all tasks")
	fmt.Println("  done <id>    Mark task as done")
	fmt.Println("  rm <id>      Delete task")
	fmt.Println("  clear        Remove all completed tasks")
}

func getLines() ([]string, error) {
	file, err := os.Open(todoFile)
	if os.IsNotExist(err) {
		return []string{}, nil
	}
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var lines []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		lines = append(lines, scanner.Text())
	}
	return lines, scanner.Err()
}

func saveLines(lines []string) error {
	file, err := os.Create(todoFile)
	if err != nil {
		return err
	}
	defer file.Close()

	w := bufio.NewWriter(file)
	for _, line := range lines {
		fmt.Fprintln(w, line)
	}
	return w.Flush()
}

func addTask(text string) {
	lines, err := getLines()
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		return
	}
	
	// Format: - [ ] Task text
	newLine := fmt.Sprintf("- [ ] %s", text)
	lines = append(lines, newLine)
	
	if err := saveLines(lines); err != nil {
		fmt.Printf("Error writing file: %v\n", err)
	} else {
		fmt.Printf("Added: %s\n", text)
	}
}

func listTasks() {
	lines, err := getLines()
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		return
	}

	if len(lines) == 0 {
		fmt.Println("No tasks found in TODO.md")
		return
	}

	fmt.Println("Tasks:")
	for i, line := range lines {
		// Basic parsing to make it look nice
		status := " "
		content := line
		if strings.HasPrefix(line, "- [ ] ") {
			status = " "
			content = line[6:]
		} else if strings.HasPrefix(line, "- [x] ") {
			status = "x"
			content = line[6:]
		}
		
		fmt.Printf("%3d. [%s] %s\n", i+1, status, content)
	}
}

func markTask(index int, done bool) {
	lines, err := getLines()
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		return
	}

	if index < 1 || index > len(lines) {
		fmt.Printf("Error: Invalid task number %d\n", index)
		return
	}

	line := lines[index-1]
	// Toggle state
	if done {
		if strings.HasPrefix(line, "- [ ] ") {
			lines[index-1] = strings.Replace(line, "- [ ] ", "- [x] ", 1)
		}
	} else {
		if strings.HasPrefix(line, "- [x] ") {
			lines[index-1] = strings.Replace(line, "- [x] ", "- [ ] ", 1)
		}
	}

	if err := saveLines(lines); err != nil {
		fmt.Printf("Error writing file: %v\n", err)
	} else {
		state := "done"
		if !done { state = "incomplete" }
		fmt.Printf("Marked task %d as %s\n", index, state)
	}
}

func removeTask(index int) {
	lines, err := getLines()
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		return
	}

	if index < 1 || index > len(lines) {
		fmt.Printf("Error: Invalid task number %d\n", index)
		return
	}

	// Remove element at index-1
	// Go slice trick: append(a[:i], a[i+1:]...)
	removed := lines[index-1]
	lines = append(lines[:index-1], lines[index:]...)

	if err := saveLines(lines); err != nil {
		fmt.Printf("Error writing file: %v\n", err)
	} else {
		fmt.Printf("Removed: %s\n", removed)
	}
}

func clearCompleted() {
	lines, err := getLines()
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		return
	}
	
	var newLines []string
	count := 0
	for _, line := range lines {
		if !strings.HasPrefix(line, "- [x] ") {
			newLines = append(newLines, line)
		} else {
			count++
		}
	}
	
	if err := saveLines(newLines); err != nil {
		fmt.Printf("Error writing file: %v\n", err)
	} else {
		fmt.Printf("Cleared %d completed tasks.\n", count)
	}
}
