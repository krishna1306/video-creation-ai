#!/usr/bin/env python3
"""
HTML Validation Script
Validates HTML files for proper formatting and structure.
Checks for:
- Balanced tags
- Proper nesting
- Malformed tags
- Unclosed tags
"""

import sys
from pathlib import Path
from html.parser import HTMLParser
from typing import List, Tuple


class HTMLValidator(HTMLParser):
    """Custom HTML parser that validates structure and formatting."""
    
    def __init__(self):
        super().__init__()
        self.tag_stack: List[Tuple[str, int, int]] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.line_num = 1
        self.self_closing_tags = {
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'
        }
        
    def handle_starttag(self, tag, attrs):
        """Handle opening tags."""
        # Skip self-closing tags
        if tag.lower() not in self.self_closing_tags:
            self.tag_stack.append((tag, self.getpos()[0], self.getpos()[1]))
    
    def handle_endtag(self, tag):
        """Handle closing tags and check for balance."""
        if tag.lower() in self.self_closing_tags:
            return
            
        if not self.tag_stack:
            self.errors.append(
                f"Line {self.getpos()[0]}: Closing tag </{tag}> has no matching opening tag"
            )
            return
        
        # Check if the closing tag matches the most recent opening tag
        expected_tag, open_line, open_col = self.tag_stack[-1]
        if tag.lower() != expected_tag.lower():
            # Look for the matching tag in the stack
            found = False
            for i in range(len(self.tag_stack) - 1, -1, -1):
                if self.tag_stack[i][0].lower() == tag.lower():
                    # Found matching tag, but it's not the most recent
                    self.errors.append(
                        f"Line {self.getpos()[0]}: Closing tag </{tag}> doesn't match "
                        f"most recent opening tag <{expected_tag}> at line {open_line}"
                    )
                    found = True
                    break
            
            if not found:
                self.errors.append(
                    f"Line {self.getpos()[0]}: Closing tag </{tag}> has no matching opening tag"
                )
        else:
            # Proper match, pop from stack
            self.tag_stack.pop()
    
    def handle_data(self, data):
        """Handle text data - check for malformed tags."""
        # Check for incomplete/malformed tags
        if '<' in data and '>' in data:
            # Potential malformed tag in text content
            parts = data.split('<')
            for part in parts[1:]:
                if '>' in part:
                    tag_content = part.split('>')[0]
                    # Check for malformed patterns
                    if ' ' in tag_content and not any(c in tag_content for c in ['=', '"', "'"]):
                        self.warnings.append(
                            f"Line {self.getpos()[0]}: Possible malformed tag: <{tag_content}>"
                        )
    
    def error(self, message):
        """Handle parsing errors."""
        self.errors.append(f"Line {self.getpos()[0]}: Parse error - {message}")
    
    def get_unclosed_tags(self) -> List[str]:
        """Return list of unclosed tags."""
        return [
            f"Line {line}: Unclosed tag <{tag}>"
            for tag, line, col in self.tag_stack
        ]


def validate_html_file(filepath: Path) -> Tuple[bool, List[str], List[str]]:
    """
    Validate an HTML file.
    
    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, [f"Failed to read file: {e}"], []
    
    validator = HTMLValidator()
    
    try:
        validator.feed(content)
    except Exception as e:
        validator.errors.append(f"Critical parsing error: {e}")
    
    # Check for unclosed tags
    unclosed = validator.get_unclosed_tags()
    validator.errors.extend(unclosed)
    
    is_valid = len(validator.errors) == 0
    
    return is_valid, validator.errors, validator.warnings


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python validate_html.py <html_file>")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    
    if not filepath.exists():
        print(f"Error: File '{filepath}' does not exist")
        sys.exit(1)
    
    if not filepath.suffix.lower() in ['.html', '.htm']:
        print(f"Warning: File '{filepath}' does not have .html or .htm extension")
    
    print(f"Validating: {filepath}")
    print("-" * 60)
    
    is_valid, errors, warnings = validate_html_file(filepath)
    
    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"  {warning}")
    
    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for error in errors:
            print(f"  {error}")
        print("\n" + "=" * 60)
        print("❌ HTML validation FAILED")
        sys.exit(1)
    else:
        print("\n" + "=" * 60)
        print("✅ HTML validation PASSED")
        if warnings:
            print(f"   (with {len(warnings)} warnings)")
        sys.exit(0)


if __name__ == "__main__":
    main()
