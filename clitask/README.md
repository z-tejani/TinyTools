# Clitask - The Context Manager

A simple CLI task manager that stores everything in a standard `TODO.md` file.

## Summary
`clitask` lets you manage your to-do list without leaving the terminal. Because it saves to `TODO.md`, your tasks stay inside your project and are easily readable by any text editor or Git.

## Installation
Requires [Go](https://go.dev/).
```bash
# Compile the binary
go build clitask.go
```

## Usage
### Add a task
```bash
./clitask add "Review pull request"
```

### List tasks
```bash
./clitask ls
```

### Mark a task as done
```bash
./clitask done 1
```

### Clear completed tasks
```bash
./clitask clear
```
This removes all items marked with `[x]` from the file.
