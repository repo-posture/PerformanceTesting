import json
import random
import hashlib
import argparse
import time
import uuid
import os
import xml.dom.minidom
from datetime import datetime, timezone
from tqdm import tqdm

# Expanded license list with real OSS licenses
LICENSES = [
    'MIT', 'Apache-2.0', 'GPL-3.0', 'GPL-2.0', 'LGPL-2.1', 'BSD-3-Clause', 'BSD-2-Clause', 
    'MPL-2.0', 'EPL-2.0', 'AGPL-3.0', 'Unlicense', 'ISC', 'WTFPL', 'CC0-1.0', 
    'CC-BY-4.0', 'CC-BY-SA-4.0', 'Artistic-2.0', 'Proprietary', 'Custom'
]

# Realistic component ecosystems with actual package names
ECOSYSTEMS = {
    'npm': ['react', 'axios', 'lodash', 'express', 'moment', 'chalk', 'redux', 'vue', 'webpack', 'jquery'],
    'maven': ['org.springframework:spring-core', 'com.fasterxml.jackson.core:jackson-databind', 
              'org.apache.commons:commons-lang3', 'org.hibernate:hibernate-core',
              'com.google.guava:guava', 'junit:junit', 'log4j:log4j', 'ch.qos.logback:logback-classic'],
    'pypi': ['requests', 'numpy', 'pandas', 'flask', 'django', 'pytest', 'scikit-learn', 
             'tensorflow', 'sqlalchemy', 'beautifulsoup4', 'matplotlib', 'pillow'],
    'golang': ['github.com/stretchr/testify', 'github.com/gin-gonic/gin', 'github.com/gorilla/mux',
               'github.com/spf13/cobra', 'github.com/prometheus/client_golang', 'go.uber.org/zap'],
    'nuget': ['Newtonsoft.Json', 'Microsoft.AspNetCore', 'Serilog', 'AutoMapper', 
              'Dapper', 'Microsoft.EntityFrameworkCore', 'xunit', 'NLog']
}

# Common vulnerability data
CVE_PATTERNS = [
    {'id': 'CVE-2021-{0}', 'description': 'Buffer overflow in {1} versions before {2} allows attackers to execute arbitrary code.',
     'severity': 'HIGH', 'cvss_score': (7.0, 9.5)},
    {'id': 'CVE-2022-{0}', 'description': 'Cross-site scripting vulnerability in {1} version {2} allows attackers to inject malicious code.',
     'severity': 'MEDIUM', 'cvss_score': (4.0, 6.9)},
    {'id': 'CVE-2023-{0}', 'description': 'Information disclosure in {1} before {2} allows attackers to access sensitive data.',
     'severity': 'MEDIUM', 'cvss_score': (3.0, 6.5)},
    {'id': 'CVE-2020-{0}', 'description': 'SQL injection vulnerability in {1} version {2} allows attackers to modify database queries.',
     'severity': 'CRITICAL', 'cvss_score': (8.0, 10.0)},
    {'id': 'CVE-2019-{0}', 'description': 'Denial of service vulnerability in {1} affects versions {2} and earlier.',
     'severity': 'LOW', 'cvss_score': (2.0, 3.9)}
]

def generate_purl(ecosystem, name, version):
    """Generate Package URL (PURL) for a component"""
    if ecosystem == 'maven':
        group, artifact = name.split(':')
        return f"pkg:maven/{group}/{artifact}@{version}"
    elif ecosystem == 'npm':
        return f"pkg:npm/{name}@{version}"
    elif ecosystem == 'pypi':
        return f"pkg:pypi/{name}@{version}"
    elif ecosystem == 'golang':
        return f"pkg:golang/{name}@{version}"
    elif ecosystem == 'nuget':
        return f"pkg:nuget/{name}@{version}"
    else:
        return f"pkg:generic/{name}@{version}"

def generate_checksum():
    """Generate a random SHA-256 checksum"""
    data = str(random.random()).encode('utf-8')
    return hashlib.sha256(data).hexdigest()

def generate_version():
    """Generate a realistic version string"""
    patterns = [
        f"{random.randint(0,10)}.{random.randint(0,20)}.{random.randint(0,99)}",
        f"{random.randint(0,5)}.{random.randint(0,15)}",
        f"{random.randint(1,3)}.{random.randint(0,10)}.{random.randint(0,30)}-beta.{random.randint(1,5)}",
        f"{random.randint(0,2)}.{random.randint(0,9)}.{random.randint(0,20)}-rc.{random.randint(1,3)}",
        f"{random.randint(20,23)}.{random.randint(1,12)}.{random.randint(1,30)}"
    ]
    return random.choice(patterns)

def generate_cpe(ecosystem, name, version):
    """Generate a CPE (Common Platform Enumeration) string"""
    vendor = name.split(':')[0] if ':' in name else name
    product = name.split(':')[1] if ':' in name else name
    return f"cpe:2.3:a:{vendor}:{product}:{version}:*:*:*:*:*:*:*"

def generate_vulnerability():
    """Generate a random vulnerability"""
    if random.random() > 0.7:  # 30% chance of having a vulnerability
        pattern = random.choice(CVE_PATTERNS)
        cve_id = pattern['id'].format(random.randint(1000, 9999))
        vuln = {
            "id": cve_id,
            "description": pattern['description'].format(
                random.randint(1000, 9999), 
                "the component", 
                f"{random.randint(0,5)}.{random.randint(0,10)}.{random.randint(0,20)}"
            ),
            "severity": pattern['severity'],
            "cvssScore": round(random.uniform(pattern['cvss_score'][0], pattern['cvss_score'][1]), 1),
            "references": [
                f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={cve_id}"
            ]
        }
        return vuln
    return None

def get_random_component(component_list, existing_components=None, complexity_level=1):
    """Get a random component with ecosystem information"""
    if existing_components is None:
        existing_components = []
    
    # Choose ecosystem and component name
    ecosystem = random.choice(list(ECOSYSTEMS.keys()))
    name = random.choice(ECOSYSTEMS[ecosystem])
    
    # Ensure uniqueness in complex mode
    if complexity_level > 1:
        attempts = 0
        while f"{ecosystem}:{name}" in existing_components and attempts < 10:
            ecosystem = random.choice(list(ECOSYSTEMS.keys()))
            name = random.choice(ECOSYSTEMS[ecosystem])
            attempts += 1
    
    version = generate_version()
    existing_components.append(f"{ecosystem}:{name}")
    
    return {
        "ecosystem": ecosystem,
        "name": name,
        "version": version,
        "purl": generate_purl(ecosystem, name, version),
        "cpe": generate_cpe(ecosystem, name, version)
    }

def generate_spdx_sbom(component_count, complexity_level=1):
    """Generate an SPDX SBOM with the specified number of components"""
    components = []
    relationships = []
    existing_components = []
    
    # First pass: create all components
    for i in tqdm(range(component_count), desc="Generating SPDX components", disable=(component_count < 500)):
        comp_info = get_random_component(ECOSYSTEMS, existing_components, complexity_level)
        
        # More or fewer details based on complexity
        external_refs = []
        external_refs.append({
            "referenceCategory": "PACKAGE-MANAGER",
            "referenceType": "purl",
            "referenceLocator": comp_info["purl"]
        })
        
        if complexity_level > 1:
            external_refs.append({
                "referenceCategory": "SECURITY",
                "referenceType": "cpe23Type",
                "referenceLocator": comp_info["cpe"]
            })
            
            # Add website reference
            external_refs.append({
                "referenceCategory": "OTHER",
                "referenceType": "website",
                "referenceLocator": f"https://{comp_info['ecosystem']}.example.org/package/{comp_info['name']}"
            })
        
        comp = {
            "SPDXID": f"SPDXRef-Package-{i}",
            "name": comp_info["name"],
            "versionInfo": comp_info["version"],
            "supplier": f"Organization: {random.choice(['Example Inc', 'Open Source Foundation', 'Tech Corp', 'Community Project'])}",
            "licenseConcluded": random.choice(LICENSES),
            "licenseDeclared": random.choice(LICENSES),
            "downloadLocation": f"https://{comp_info['ecosystem']}.example.org/download/{comp_info['name']}/{comp_info['version']}",
            "filesAnalyzed": False,
            "externalRefs": external_refs,
            "checksums": [{
                "algorithm": "SHA256",
                "checksumValue": generate_checksum()
            }]
        }
        
        # Add description for higher complexity
        if complexity_level >= 2:
            comp["description"] = f"This is a synthetic {comp_info['ecosystem']} package for {comp_info['name']}."
            comp["copyrightText"] = f"Copyright {random.randint(2010, 2023)} Example Organization"
            comp["attributionTexts"] = [f"Attribution for {comp_info['name']} goes to its original authors."]
        
        components.append(comp)
    
    # Second pass: create relationships (only for complexity > 1)
    if complexity_level > 1 and component_count > 1:
        # Create a simple tree structure for dependencies
        for i in range(1, component_count):
            # Each component might depend on one or more previous components
            dependency_count = random.randint(1, min(3, i)) if complexity_level > 2 else 1
            for _ in range(dependency_count):
                dependent_idx = random.randint(0, i-1)
                relationship = {
                    "spdxElementId": f"SPDXRef-Package-{i}",
                    "relatedSpdxElement": f"SPDXRef-Package-{dependent_idx}",
                    "relationshipType": "DEPENDS_ON"
                }
                relationships.append(relationship)
    
    # Create the SBOM
    document_uuid = str(uuid.uuid4())
    sbom = {
        "spdxVersion": "SPDX-2.2",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "Synthetic SPDX SBOM",
        "documentNamespace": f"http://spdx.org/spdxdocs/synthetic-sbom-{document_uuid}",
        "creationInfo": {
            "created": datetime.now(timezone.utc).isoformat(),
            "creators": ["Tool: SBOM-Generator", "Organization: Performance Testing Team"],
            "comment": "This SBOM was generated for performance testing purposes"
        },
        "packages": components
    }
    
    # Add relationships for higher complexity
    if complexity_level > 1 and relationships:
        sbom["relationships"] = relationships
    
    return sbom

def generate_cyclonedx_sbom(component_count, complexity_level=1):
    """Generate a CycloneDX SBOM with the specified number of components"""
    components = []
    existing_components = []
    dependencies = []
    
    # First pass: create all components
    for i in tqdm(range(component_count), desc="Generating CycloneDX components", disable=(component_count < 500)):
        comp_info = get_random_component(ECOSYSTEMS, existing_components, complexity_level)
        
        # Extract group from name for maven packages
        group = None
        name = comp_info["name"]
        if comp_info["ecosystem"] == "maven" and ":" in name:
            group, name = name.split(":")
        
        # Generate a package-id
        package_id = hashlib.md5(f"{comp_info['name']}:{comp_info['version']}".encode()).hexdigest()[:16]
        
        # Create proper purl format
        purl = comp_info["purl"]
        
        # Create bom-ref with package-id
        bom_ref = f"{purl}?package-id={package_id}"
        
        # Basic component properties
        comp = {
            "bom-ref": bom_ref,
            "type": "library",
            "name": name,
            "version": comp_info["version"],
            "purl": purl,
        }
        
        # Add group for maven packages
        if group:
            comp["group"] = group
        
        # Add CPE
        comp["cpe"] = comp_info["cpe"]
        
        # Add licenses for higher complexity
        if complexity_level >= 2:
            comp["licenses"] = [{
                "license": {"id": random.choice(LICENSES)}
            }]
        
        # Add external references
        comp["externalReferences"] = [
            {
                "url": "",
                "hashes": [
                    {
                        "alg": "SHA-1",
                        "content": generate_checksum()
                    }
                ],
                "type": "build-meta"
            }
        ]
        
        # Add properties
        comp["properties"] = [
            {
                "name": "syft:package:foundBy",
                "value": f"{comp_info['ecosystem']}-cataloger"
            },
            {
                "name": "syft:package:language",
                "value": comp_info['ecosystem'] if comp_info['ecosystem'] != 'maven' else 'java'
            },
            {
                "name": "syft:package:type",
                "value": comp_info['ecosystem']
            },
            {
                "name": "syft:package:metadataType",
                "value": comp_info['ecosystem']
            }
        ]
        
        # Add CPE properties
        comp["properties"].append({
            "name": "syft:cpe23",
            "value": comp_info["cpe"]
        })
        
        # Add path property
        comp["properties"].append({
            "name": "syft:location:0:path",
            "value": f"/packages/{comp_info['ecosystem']}/{comp_info['name']}/{comp_info['version']}"
        })
        
        components.append(comp)
    
    # Second pass: create dependencies (for complexity > 1)
    if complexity_level > 1 and component_count > 1:
        for i in range(component_count):
            # Each component might depend on others
            if i > 0:  # Skip the first component to avoid circular dependencies
                dependency_count = random.randint(1, min(3, i)) if complexity_level > 2 else 1
                deps = []
                for _ in range(dependency_count):
                    dependent_idx = random.randint(0, i-1)
                    deps.append({"ref": components[dependent_idx]["bom-ref"]})
                
                if deps:
                    dependencies.append({
                        "ref": components[i]["bom-ref"],
                        "dependsOn": [d["ref"] for d in deps]
                    })
    
    # Create the SBOM
    document_uuid = uuid.uuid4()
    
    # Generate root component reference
    root_component_ref = hashlib.md5(b"root-component").hexdigest()[:16]
    
    sbom = {
        "$schema": "http://cyclonedx.org/schema/bom-1.6.schema.json",
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{document_uuid}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tools": {
                "components": [
                    {
                        "type": "application",
                        "author": "Performance Testing Team",
                        "name": "SBOM-Generator",
                        "version": "2.0.0"
                    }
                ]
            },
            "component": {
                "bom-ref": root_component_ref,
                "type": "application",
                "name": "Synthetic Application",
                "version": "1.0.0"
            }
        },
        "components": components
    }
    
    # Add dependencies for higher complexity
    if complexity_level > 1 and dependencies:
        sbom["dependencies"] = dependencies
    
    return sbom

def save_sbom(sbom, filename, format_type="json"):
    """Save the SBOM to a file in the specified format"""
    os.makedirs("sboms", exist_ok=True)
    filepath = os.path.join("sboms", filename)
    
    if format_type == "json":
        with open(filepath, 'w') as f:
            json.dump(sbom, f, indent=2)
    elif format_type == "xml" and "bomFormat" in sbom:  # XML only for CycloneDX
        # Convert to XML (simplified approach)
        xml_doc = cyclonedx_json_to_xml(sbom)
        with open(filepath, 'w') as f:
            f.write(xml_doc.toprettyxml(indent="  "))
    else:
        raise ValueError(f"Unsupported format: {format_type}")
    
    return filepath

def cyclonedx_json_to_xml(sbom_json):
    """Convert CycloneDX JSON to XML format (simplified)"""
    doc = xml.dom.minidom.getDOMImplementation().createDocument(None, "bom", None)
    root = doc.documentElement
    
    # Set attributes on root element
    root.setAttribute("xmlns", "http://cyclonedx.org/schema/bom/1.4")
    root.setAttribute("serialNumber", sbom_json.get("serialNumber", ""))
    root.setAttribute("version", str(sbom_json.get("version", "1")))
    
    # Add metadata
    if "metadata" in sbom_json:
        metadata_elem = doc.createElement("metadata")
        
        # Add timestamp
        if "timestamp" in sbom_json["metadata"]:
            timestamp_elem = doc.createElement("timestamp")
            timestamp_elem.appendChild(doc.createTextNode(sbom_json["metadata"]["timestamp"]))
            metadata_elem.appendChild(timestamp_elem)
        
        # Add tools
        if "tools" in sbom_json["metadata"]:
            tools_elem = doc.createElement("tools")
            for tool in sbom_json["metadata"]["tools"]:
                tool_elem = doc.createElement("tool")
                
                for key, value in tool.items():
                    elem = doc.createElement(key)
                    elem.appendChild(doc.createTextNode(str(value)))
                    tool_elem.appendChild(elem)
                    
                tools_elem.appendChild(tool_elem)
            metadata_elem.appendChild(tools_elem)
        
        # Add component metadata
        if "component" in sbom_json["metadata"]:
            comp_elem = create_component_element(doc, sbom_json["metadata"]["component"])
            metadata_elem.appendChild(comp_elem)
            
        root.appendChild(metadata_elem)
    
    # Add components
    components_elem = doc.createElement("components")
    for comp in sbom_json.get("components", []):
        comp_elem = create_component_element(doc, comp)
        components_elem.appendChild(comp_elem)
    
    root.appendChild(components_elem)
    
    # Add dependencies
    if "dependencies" in sbom_json:
        deps_elem = doc.createElement("dependencies")
        
        for dep in sbom_json["dependencies"]:
            dep_elem = doc.createElement("dependency")
            dep_elem.setAttribute("ref", dep["ref"])
            
            if "dependsOn" in dep:
                for depends in dep["dependsOn"]:
                    dep_on_elem = doc.createElement("dependsOn")
                    dep_on_elem.appendChild(doc.createTextNode(depends))
                    dep_elem.appendChild(dep_on_elem)
                    
            deps_elem.appendChild(dep_elem)
            
        root.appendChild(deps_elem)
    
    return doc

def create_component_element(doc, component):
    """Helper function to create a component element"""
    comp_elem = doc.createElement("component")
    comp_elem.setAttribute("type", component.get("type", ""))
    
    if "bom-ref" in component:
        comp_elem.setAttribute("bom-ref", component["bom-ref"])
    
    # Add simple text elements
    for key in ["name", "version", "description", "purl", "cpe"]:
        if key in component:
            elem = doc.createElement(key)
            elem.appendChild(doc.createTextNode(str(component[key])))
            comp_elem.appendChild(elem)
    
    # Add licenses
    if "licenses" in component:
        licenses_elem = doc.createElement("licenses")
        
        for license_obj in component["licenses"]:
            license_elem = doc.createElement("license")
            
            if "license" in license_obj and "id" in license_obj["license"]:
                id_elem = doc.createElement("id")
                id_elem.appendChild(doc.createTextNode(license_obj["license"]["id"]))
                license_elem.appendChild(id_elem)
                
            licenses_elem.appendChild(license_elem)
        
        comp_elem.appendChild(licenses_elem)
    
    # Add hashes
    if "hashes" in component:
        hashes_elem = doc.createElement("hashes")
        
        for hash_obj in component["hashes"]:
            hash_elem = doc.createElement("hash")
            hash_elem.setAttribute("alg", hash_obj["alg"])
            hash_elem.appendChild(doc.createTextNode(hash_obj["content"]))
            hashes_elem.appendChild(hash_elem)
            
        comp_elem.appendChild(hashes_elem)
    
    return comp_elem

# Command line argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate synthetic SBOM files for performance testing')
    parser.add_argument('--format', choices=['spdx', 'cyclonedx'], default='spdx',
                        help='SBOM format to generate (spdx or cyclonedx)')
    parser.add_argument('--count', type=int, default=100,
                        help='Number of components to include in the SBOM')
    parser.add_argument('--complexity', type=int, choices=[1, 2, 3], default=1,
                        help='Complexity level (1=basic, 2=standard, 3=advanced)')
    parser.add_argument('--output', choices=['json', 'xml'], default='json',
                        help='Output format (JSON or XML, XML only available for CycloneDX)')
    args = parser.parse_args()
    
    # Generate a timestamp to make each file unique
    timestamp = int(time.time())
    
    # Show warning for XML with SPDX
    if args.output == 'xml' and args.format == 'spdx':
        print("Warning: XML output is only available for CycloneDX format. Using JSON instead.")
        output_format = 'json'
    else:
        output_format = args.output
    
    try:
        if args.format == 'spdx':
            sbom = generate_spdx_sbom(args.count, args.complexity)
            filename = f'synthetic_spdx_{args.count}_c{args.complexity}.{output_format}'
            filepath = save_sbom(sbom, filename, output_format)
            print(f"Generated SPDX SBOM with {args.count} components (complexity level {args.complexity}): {filepath}")
        else:
            sbom = generate_cyclonedx_sbom(args.count, args.complexity)
            filename = f'synthetic_cyclonedx_{args.count}_c{args.complexity}.{output_format}'
            filepath = save_sbom(sbom, filename, output_format)
            print(f"Generated CycloneDX SBOM with {args.count} components (complexity level {args.complexity}): {filepath}")
    except Exception as e:
        print(f"Error generating SBOM: {e}")


# python3 sbom_generator.py --format cyclonedx --count 5000
# python3 sbom_generator.py --format spdx --count 5000 
