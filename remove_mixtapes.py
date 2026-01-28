#!/usr/bin/env python3
"""
Remove mixtapes from playlists.js that have been added to discography.
"""

def remove_mixtapes_from_playlists():
    """Remove playlist entries that have [mixtape] in the title"""

    playlists_path = '/Users/tyleretters/projects/nor.the-rn.info/src/data/playlists.js'

    # Read the file line by line
    with open(playlists_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Track state
    output_lines = []
    skip_until_closing = False
    current_entry_lines = []
    removed_titles = []

    for line in lines:
        # Check if this line starts a new object
        if line.strip() == '{':
            current_entry_lines = [line]
            skip_until_closing = False
        # Check if this line is a title with [mixtape]
        elif 'title:' in line and '[mixtape]' in line:
            skip_until_closing = True
            current_entry_lines.append(line)
            # Extract title for display
            import re
            title_match = re.search(r"title: '(.*?)'", line)
            if title_match:
                removed_titles.append(title_match.group(1))
        # Check if this line closes the object
        elif line.strip() == '},':
            current_entry_lines.append(line)
            if not skip_until_closing:
                # This wasn't a mixtape, keep it
                output_lines.extend(current_entry_lines)
            current_entry_lines = []
            skip_until_closing = False
        else:
            current_entry_lines.append(line)
            # If we're not skipping and not in an object, just add directly
            if not current_entry_lines[0].strip() == '{':
                output_lines.append(line)
                current_entry_lines = []

    # Write back to file
    with open(playlists_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)

    print(f"Found {len(removed_titles)} mixtape playlists to remove:")
    for title in removed_titles:
        print(f"  - {title}")
    print(f"\nRemoved {len(removed_titles)} mixtape playlists from playlists.js")


if __name__ == '__main__':
    remove_mixtapes_from_playlists()
