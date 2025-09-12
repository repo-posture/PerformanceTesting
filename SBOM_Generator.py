import json
import subprocess
import hashlib
import argparse
from packageurl import PackageURL
from cyclonedx.model.bom import Bom
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.factory.license import LicenseFactory
from cyclonedx.output import make_outputter
from cyclonedx.schema import OutputFormat, SchemaVersion

def get_installed_packages():
    result = subprocess.run(['pip', 'list', '--format', 'json'], capture_output=True, text=True)
    installed = json.loads(result.stdout)
    return {pkg['name'].lower(): pkg['version'] for pkg in installed}

def get_package_license_and_path(package_name):
    result = subprocess.run(['pip', 'show', package_name], capture_output=True, text=True)
    data = {}
    for line in result.stdout.splitlines():
        if line.startswith('License:'):
            data['license'] = line.split('License:')[1].strip()
        if line.startswith('Location:'):
            data['location'] = line.split('Location:')[1].strip()
    return data

def compute_package_hash(package_location, package_name):
    # Very basic hashing: hash the top-level __init__.py file (if exists)
    try:
        import os
        pkg_path = f"{package_location}/{package_name.replace('-', '_')}/__init__.py"
        with open(pkg_path, 'rb') as f:
            file_bytes = f.read()
            return hashlib.sha256(file_bytes).hexdigest()
    except Exception:
        return None

def load_component_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)

def generate_sbom(component_configs, installed_packages):
    components = []
    lc_factory = LicenseFactory()

    for entry in component_configs:
        comp_type = entry.get('type')
        name = entry.get('name')
        license_str = entry.get('license')

        if comp_type == 'installed':
            version = installed_packages.get(name.lower())
            if not version:
                print(f"[Warning] Package '{name}' not installed. Skipping.")
                continue

            pkg_info = get_package_license_and_path(name)
            location = pkg_info.get('location')
            detected_license = pkg_info.get('license') or 'UNKNOWN'
            hash_value = compute_package_hash(location, name) if location else None

            component = Component(
                name=name,
                version=version,
                type=ComponentType.LIBRARY,
                licenses=[lc_factory.make_from_string(detected_license)]
            )
            if hash_value:
                component.hashes.sha256 = hash_value

        elif comp_type == 'custom':
            version = entry.get('version')
            if not version:
                print(f"[Error] Custom component '{name}' must specify version. Skipping.")
                continue

            component = Component(
                name=name,
                version=version,
                type=ComponentType.LIBRARY,
                licenses=[lc_factory.make_from_string(license_str or 'UNKNOWN')]
            )
        else:
            print(f"[Error] Unknown type '{comp_type}' for '{name}'. Skipping.")
            continue

        components.append(component)

    bom = Bom()
    for component in components:
        bom.components.add(component)
    
    return bom

def write_sbom(bom, output_file, output_format):
    format_enum = OutputFormat.JSON if output_format == 'cyclonedx' else OutputFormat.JSON_SPDX_2_3
    outputter = make_outputter(bom, format_enum, SchemaVersion.V1_5)
    sbom_str = outputter.output_as_string(indent=2)

    with open(output_file, 'w') as f:
        f.write(sbom_str)
    print(f"\n✅ SBOM written to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='SBOM Generator')
    parser.add_argument('--config', default='components.json', help='Path to components config file')
    parser.add_argument('--output', default='sbom.json', help='SBOM output file path')
    parser.add_argument('--format', choices=['cyclonedx', 'spdx'], default='cyclonedx', help='SBOM output format')
    args = parser.parse_args()

    print("[*] Loading components config...")
    component_configs = load_component_config(args.config)

    print("[*] Fetching installed pip packages...")
    installed_packages = get_installed_packages()

    print("[*] Generating SBOM...")
    bom = generate_sbom(component_configs, installed_packages)

    write_sbom(bom, args.output, args.format)

if __name__ == '__main__':
    main()
