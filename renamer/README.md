# Renamer.py - The Mass Labeler

A robust bulk file renaming tool with Regex support and safety previews.

## Summary
`renamer.py` allows you to rename hundreds of files at once using simple string replacement or complex Regular Expressions. To prevent accidental data loss, it defaults to a **Dry Run** mode, showing you exactly what will happen before any changes are made.

## Features
- **Dry Run by Default:** Always see a preview first.
- **Regex Support:** Use powerful patterns for complex renaming tasks.
- **Conflict Awareness:** Warns you if a rename would overwrite an existing file.
- **Case Sensitivity Toggle:** Option to ignore case during search.

## Usage

### Simple Replace (Dry Run)
Replace "draft" with "final" in the current directory:
```bash
python3 renamer.py "draft" "final"
```

### Apply Changes (--commit)
Actually perform the rename:
```bash
python3 renamer.py "draft" "final" --commit
```

### Regex Renaming
Convert files like `img_001.jpg` to `001-vacation.jpg`:
```bash
python3 renamer.py "img_(\d+)\.jpg" "\1-vacation.jpg" --regex --commit
```

### Target a Specific Directory
```bash
python3 renamer.py "old-prefix" "new-prefix" ./my_folder/
```

## Flags
| Flag | Description |
|------|-------------|
| `-r`, `--regex` | Use Regular Expressions for search and replace. |
| `-c`, `--commit` | Actually apply the changes (requires 'y' confirmation). |
| `-i`, `--ignore-case` | Search without case sensitivity. |
| `--hidden` | Include hidden files (starting with `.`) in the process. |
