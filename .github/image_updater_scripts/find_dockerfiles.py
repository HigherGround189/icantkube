import os
import json
import yaml #type:ignore
from pathlib import Path

# Read imageConfig.yaml
with open("../../imageConfig.yaml", "r") as file:
    imageConfig = yaml.safe_load(file)

# Get list of changed directories
dirs = os.environ.get("DIRS")
print(f"Dirs: {dirs}")

# Turn into list
cleaned_dirs = dirs[1:-1].split(",")

# Remove root directory if exists
if "." in cleaned_dirs:
    cleaned_dirs.remove(".")

def trim_to_src_child(path):
    p = Path(path)
    parts = p.parts

    # Only return paths that contain "src"
    if "src" in p.parts:
        src_index = parts.index("src")
        return Path(*parts[:src_index + 2])
    
    else:
        return

# Turn directories into Path objects
cleaned_paths = {trim_to_src_child(dirs) for dirs in cleaned_dirs}
print(f"Cleaned Paths: {cleaned_paths}")

# Loop through Paths to calculate matrix
matrix = {"include": []}
for path in cleaned_paths:
    try:
        # Remove every directory that is not a direct child of src/
        print(f"\nPath: {path}")

        # Get all dockerfiles in a directory
        dockerfiles = list(path.rglob("*.Dockerfile"))
        print(f"Dockerfiles in directory: {dockerfiles}")

        # Loop through dockerfiles to get dockerfile info
        for dockerfile_path in dockerfiles:
            dockerfile_name = dockerfile_path.name.removesuffix(".Dockerfile")
            dockerfile_autobuild = imageConfig[dockerfile_name]["autoBuild"]
            dockerfile_current_tag = imageConfig[dockerfile_name]["currentTag"]
            temp_tag = dockerfile_current_tag.lstrip("v").split(".")
            temp_tag[-1] = str(int(temp_tag[-1]) + 1)
            dockerfile_updated_tag = "v" + ".".join(temp_tag)

            print(f"Dockerfile Path: {dockerfile_path}")
            print(f"Dockerfile Name: {dockerfile_name}")
            print(f"Dockerfile Autobuild: {dockerfile_autobuild}")
            print(f"Dockerfile Tag: {dockerfile_updated_tag}")

            # If Image is has autobuild enabled, add them to matrix
            if dockerfile_autobuild:
                matrix["include"].append({
                    "buildContext": str(path),
                    "dockerfile": str(dockerfile_path),
                    "tag": f"icantkube/{dockerfile_name}:{str(dockerfile_updated_tag)}"
                })
            else:
                print(f"Skipping {dockerfile_name}")

    except StopIteration:
        continue

# Convert to JSON
print(f"\nMatrix: {json.dumps(matrix)}", flush=True)
with open(os.environ["GITHUB_OUTPUT"], "a") as f:
    f.write(f"matrix={json.dumps(matrix)}\n")