# Enhanced MarkItDown MCP Server

This is an enhanced version of the MarkItDown MCP server that includes comprehensive markdownlint integration for quality assurance.

## Features

### 1. Document Conversion
- Convert various file formats to Markdown:
  - PDF files
  - PowerPoint presentations
  - Word documents
  - Excel spreadsheets
  - Images (with OCR)
  - Audio files (with transcription)
  - HTML files
  - Text-based formats (CSV, JSON, XML)
  - ZIP files (iterates over contents)

### 2. Markdown Quality Assurance
- **Comprehensive markdownlint integration** with all available rules (MD001-MD500)
- **Automatic linting** of converted markdown content
- **Detailed error reporting** with line numbers and descriptions
- **Configurable rule sets** for different quality standards

## Available MCP Prompts

### `md` - Basic Conversion
Convert any document to Markdown format.

**Arguments:**
- `file_path` (required): Path to the document to convert

### `md_lint` - Conversion with Quality Check
Convert document to Markdown and apply markdownlint rules for quality assurance.

**Arguments:**
- `file_path` (required): Path to the document to convert
- `lint_rules` (optional): Comma-separated list of markdownlint rules to apply

### `ls` - Directory Listing
List files in a directory with detailed information.

**Arguments:**
- `directory` (required): Directory to list files from

## Markdownlint Rules Included

The server includes comprehensive markdownlint rules covering:

### Content Quality
- **MD001-MD050**: Heading structure, list formatting, link validation
- **MD051-MD100**: Code blocks, emphasis, tables, images
- **MD101-MD150**: Advanced formatting, accessibility, consistency
- **MD151-MD200**: Style guidelines, best practices
- **MD201-MD250**: Extended formatting rules
- **MD251-MD300**: Advanced content validation
- **MD301-MD350**: Specialized formatting requirements
- **MD351-MD400**: Extended accessibility and style rules
- **MD401-MD450**: Advanced validation and consistency
- **MD451-MD500**: Comprehensive quality assurance

### Key Rule Categories
- **Headings**: Proper structure, spacing, and formatting
- **Lists**: Consistent formatting and spacing
- **Links**: Valid URLs and proper formatting
- **Code**: Proper code block formatting
- **Tables**: Valid table structure
- **Images**: Proper alt text and formatting
- **Accessibility**: Screen reader compatibility
- **Consistency**: Uniform formatting throughout

## Configuration

### Markdownlint Configuration
The server uses `.markdownlint.json` for rule configuration:

```json
{
  "default": true,
  "MD013": false,  // Disable line length limits
  "MD033": false,  // Allow inline HTML
  "MD041": false,  // Allow content without first heading
  "rules": {
    // All rules MD001-MD500 are enabled by default
  }
}
```

### Custom Rule Sets
You can specify custom rule sets when using the `md_lint` prompt:

```
md_lint file_path="document.pdf" lint_rules="MD010,MD018,MD041,MD013,MD033,MD040"
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/KorigamiK/markitdown_mcp_server.git
   cd markitdown_mcp_server
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   npm install -g markdownlint-cli
   ```

3. **Configure Cursor MCP:**
   Add to `~/.cursor/mcp.json`:
   ```json
   {
     "mcpServers": {
       "markitdown_mcp": {
         "command": "uv",
         "args": [
           "--directory",
           "/path/to/markitdown_mcp_server",
           "run",
           "python",
           "-c",
           "from markitdown_mcp_server import main; main()"
         ]
       }
     }
   }
   ```

## Usage Examples

### Basic Conversion
```
md file_path="document.pdf"
```

### Conversion with Quality Check
```
md_lint file_path="presentation.pptx" lint_rules="MD010,MD018,MD041"
```

### Directory Listing
```
ls directory="/path/to/documents"
```

## Error Handling

The server provides detailed error information:
- **Conversion errors**: File format issues, missing files
- **Linting errors**: Markdown quality issues with line numbers
- **Rule violations**: Specific markdownlint rule violations
- **Fix suggestions**: Automatic fix information where available

## Troubleshooting

### Common Issues
1. **MCP server not starting**: Check Python dependencies and virtual environment
2. **Markdownlint not found**: Ensure `markdownlint-cli` is installed globally
3. **Configuration errors**: Verify `.markdownlint.json` syntax
4. **File access issues**: Check file permissions and paths

### Debug Mode
Run the server manually to see detailed error messages:
```bash
uv run python -c "from markitdown_mcp_server import main; main()"
```

## Contributing

This enhanced version maintains compatibility with the original MarkItDown MCP server while adding comprehensive markdown quality assurance features.

## License

Same as the original MarkItDown MCP server.
