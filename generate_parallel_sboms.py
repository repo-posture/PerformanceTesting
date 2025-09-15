#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import datetime
import shutil
import multiprocessing
import tempfile
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

# Default configuration
DEFAULT_COMPONENT_COUNT = 1000
DEFAULT_OUTPUT_DIR = "sboms"
COMPONENTS_FILE = "components.json"
SBOM_OUTPUT = "sbom.json"

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate random SBOMs in parallel and store them in the sboms directory"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_COMPONENT_COUNT,
        help=f"Number of components to generate (default: {DEFAULT_COMPONENT_COUNT})",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to store generated SBOMs (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--sboms",
        type=int,
        default=1,
        help="Number of SBOMs to generate (default: 1)",
    )
    parser.add_argument(
        "--installed-ratio",
        type=float,
        default=0.7,
        help="Ratio of installed components (vs. custom) (default: 0.7)",
    )
    parser.add_argument(
        "--format",
        choices=["cyclonedx", "spdx"],
        default="cyclonedx",
        help="SBOM format (default: cyclonedx)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=multiprocessing.cpu_count(),
        help=f"Number of worker processes to use (default: {multiprocessing.cpu_count()})",
    )
    return parser.parse_args()


def ensure_output_directory(output_dir):
    """Ensure the output directory exists."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"✅ Output directory: {output_dir}")


def generate_components(count, installed_ratio=0.7, temp_dir=None):
    """Generate random components using the generate_components.py script."""
    components_file = os.path.join(temp_dir, COMPONENTS_FILE) if temp_dir else COMPONENTS_FILE
    try:
        result = subprocess.run(
            [
                "python3",
                "generate_components.py",
                "--count",
                str(count),
                "--installed-ratio",
                str(installed_ratio),
                "--output",
                components_file,
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        return True, components_file, result.stdout
    except subprocess.CalledProcessError as e:
        return False, None, f"❌ Error generating components: {e}\nError output: {e.stderr}"


def generate_sbom(components_file, output_file, sbom_format="cyclonedx"):
    """Generate SBOM using the sbom_generator.py script."""
    try:
        result = subprocess.run(
            [
                "python3",
                "SBOM_Generator.py",
                "--config",
                components_file,
                "--format",
                sbom_format,
                "--output",
                output_file,
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        # Extract just the last few lines of output
        last_lines = "\n".join(result.stdout.splitlines()[-5:])
        return True, last_lines
    except subprocess.CalledProcessError as e:
        return False, f"❌ Error generating SBOM: {e}\nError output: {e.stderr}"


def generate_unique_filename(output_dir, sbom_format, component_count, sequential_number):
    """Generate a sequential filename for the SBOM in format: sbom_{format}_{count}_{sequential}."""
    filename = f"sbom_{sbom_format}_{component_count}_{sequential_number}.json"
    return os.path.join(output_dir, filename)


def process_sbom(sequential_number, total_sboms, count, installed_ratio, sbom_format, output_dir):
    """Process a single SBOM generation task."""
    start_time = time.time()
    
    # Create a temporary directory for this worker
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_sbom_output = os.path.join(temp_dir, SBOM_OUTPUT)
        
        # Generate filename for this SBOM
        output_file = generate_unique_filename(output_dir, sbom_format, count, sequential_number)
        
        result = {
            "sequential_number": sequential_number,
            "success": False,
            "message": f"Processing SBOM {sequential_number}/{total_sboms}",
            "output_file": output_file,
            "elapsed_time": 0
        }
        
        # Generate components
        success, components_file, component_message = generate_components(count, installed_ratio, temp_dir)
        result["component_message"] = component_message
        
        if not success:
            result["message"] = f"Failed to generate components for SBOM {sequential_number}/{total_sboms}"
            return result
        
        # Generate SBOM
        success, sbom_message = generate_sbom(components_file, temp_sbom_output, sbom_format)
        result["sbom_message"] = sbom_message
        
        if not success:
            result["message"] = f"Failed to generate SBOM {sequential_number}/{total_sboms}"
            return result
        
        # Copy the generated SBOM to the output directory
        try:
            if os.path.exists(temp_sbom_output):
                shutil.copy2(temp_sbom_output, output_file)
                result["success"] = True
                result["message"] = f"Successfully generated SBOM {sequential_number}/{total_sboms}"
            else:
                result["message"] = f"SBOM file not found for {sequential_number}/{total_sboms}"
        except Exception as e:
            result["message"] = f"Error copying SBOM {sequential_number}/{total_sboms}: {e}"
    
    # Calculate elapsed time
    result["elapsed_time"] = time.time() - start_time
    return result


def main():
    args = parse_arguments()
    
    # Ensure output directory exists
    ensure_output_directory(args.output_dir)
    
    print(f"\n{'=' * 50}")
    print(f"Generating {args.sboms} SBOMs in parallel using {args.workers} workers")
    print(f"Each SBOM will have {args.count} components ({int(args.count * args.installed_ratio)} installed, {int(args.count * (1-args.installed_ratio))} custom)")
    print(f"{'=' * 50}\n")
    
    start_time = time.time()
    successful_sboms = 0
    
    # Use process pool to parallelize SBOM generation
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        # Submit all tasks
        futures = []
        for i in range(1, args.sboms + 1):
            futures.append(executor.submit(
                process_sbom, 
                i, args.sboms, args.count, args.installed_ratio, args.format, args.output_dir
            ))
        
        # Process results as they complete
        for future in as_completed(futures):
            result = future.result()
            if result["success"]:
                successful_sboms += 1
                print(f"✅ SBOM {result['sequential_number']}/{args.sboms} completed in {result['elapsed_time']:.2f}s")
                print(f"   Output saved to {result['output_file']}")
            else:
                print(f"❌ SBOM {result['sequential_number']}/{args.sboms} failed: {result['message']}")
            
            if "component_message" in result:
                # Print a condensed version of the component message
                if "Generated" in result["component_message"]:
                    for line in result["component_message"].splitlines():
                        if "Generated" in line:
                            print(f"   {line}")
            
            if "sbom_message" in result:
                # Print just the final line about SBOM generation
                for line in result["sbom_message"].splitlines():
                    if "SBOM written" in line:
                        print(f"   {line}")
    
    total_time = time.time() - start_time
    
    print(f"\n{'=' * 50}")
    print(f"✅ Generated {successful_sboms}/{args.sboms} SBOMs successfully in {total_time:.2f} seconds!")
    if args.sboms > 1:
        print(f"   Average time per SBOM: {total_time / args.sboms:.2f} seconds")
    print(f"📁 Check the {args.output_dir} directory for your SBOM files")


if __name__ == "__main__":
    main()
# Usage: python3 generate_parallel_sboms.py --count 100000 --sboms 1 --workers 4
