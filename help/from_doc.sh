#!/bin/bash

# Generate txt files from md sources

for md in $(ls ../docsrc/docs/*.md); do
    pandoc -i "$md" --to plain -o $(basename "$md").txt
done

