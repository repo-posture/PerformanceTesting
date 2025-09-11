#!/usr/bin/env python3

import os
import subprocess
import csv
import time
from tqdm import tqdm

def get_file_size_kb(file_path):
    """Get file size in kilobytes"""
    size_bytes = os.path.getsize(file_path)
    size_kb = size_bytes / 1024  # Convert to KB
    return round(size_kb, 2)

def run_sbom_generator(format_type, component_count):
    """Run the SBOM generator with specified parameters and return file path and size"""
    timestamp = int(time.time())
    expected_filename = f"synthetic_{format_type}_{component_count}_c1_{timestamp}.json"
    
    # Run the SBOM generator command
    cmd = ["python3", "SBOM_Generator.py", "--format", format_type, "--count", str(component_count)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Extract the generated filename from the output
    output_line = result.stdout.strip().split('\n')[-1]
    filepath = output_line.split(': ')[-1]
    
    # Get file size
    file_size = get_file_size_kb(filepath)
    
    return filepath, file_size

def main():
    # Parameters
    format_type = "cyclonedx"  # Change to "cyclonedx" if needed
    start_count = 20001
    end_count = 20100
    step = 1
    
    # File to store results
    csv_filename = f"sbom_file_sizes_{format_type}.csv"
    
    # Create/overwrite CSV file with headers
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Component Count", "File Size (KB)", "File Size (MB)", "Filename"])
    
    print(f"Collecting file sizes for {format_type} SBOMs from {start_count} to {end_count} components...")
    
    # Generate SBOMs with different component counts
    for count in tqdm(range(start_count, end_count + 1, step)):
        try:
            filepath, file_size_kb = run_sbom_generator(format_type, count)
            file_size_mb = round(file_size_kb / 1024, 2)  # Convert KB to MB
            
            # Append results to CSV
            with open(csv_filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([count, file_size_kb, file_size_mb, os.path.basename(filepath)])
                
            print(f"Components: {count}, Size: {file_size_kb} KB ({file_size_mb} MB)")
            
            # Optional: remove generated file to save space
            # os.remove(filepath)
            
        except Exception as e:
            print(f"Error processing component count {count}: {e}")
    
    print(f"Data collection complete. Results saved to {csv_filename}")

if __name__ == "__main__":
    main()
