from pathlib import Path
import requests # type:ignore
from ruamel.yaml import YAML # type:ignore

# Create yaml object
yaml = YAML()
yaml.preserve_quotes = True

# Read imageConfig file
with open("../../imageConfig.yaml", "r") as f:
    imageConfig = yaml.load(f)
print(f"ImageConfig: {imageConfig}")

# Create list of images to update
update_list = []
for image in imageConfig:
    if imageConfig[image]["autoUpdate"]:
        update_list.append(image)
print(f"Update List: {update_list}")

# Get all "kustomization.yaml" files
kustomizations = [str(files) for files in Path(".").rglob("kustomization.yaml")]

# Loop through each kustomization.yaml files
image_list = {}
for kustomize in kustomizations:

    # Read kustomization.yaml
    with open(kustomize, "r") as f:
        kustomize_yaml = yaml.load(f)
    print(f"\nKustomization.yaml: {kustomize_yaml}")
    
    # Get all images from kustomization.yaml`s images field
    kustomize_images = kustomize_yaml["images"]
    print(f"Kustomize Images: {kustomize_images}") 

    # Loop through all images for image_list
    for image in kustomize_images:
        # Get name of image    
        image_name = image["name"].removeprefix(r"icantkube/")
        print(f"Image Name: {image_name}")
    
        # If image is in update_list, get latest tag from dockerhub
        if image_name in update_list:
            url = f"https://hub.docker.com/v2/repositories/icantkube/{image_name}/tags/"
            params = {
                "page_size": 1,
                "ordering": "last_updated",
            }
            response = requests.get(url, params=params)
            data = response.json()
            print(f"Dockerhub Response: {data}")
            tag = data["results"][0]["name"]
            print(f"Tag: {tag}")

            image_list[image_name] = {
                "kustomizeFile": kustomize,
                "tag": tag
            }
            
print(f"\nImage List: {image_list}")

# Update each image`s kustomization.yaml with the new tag
for image_name, image_data in image_list.items():
    kustomize_file_location = image_data["kustomizeFile"]
    new_tag = image_data["tag"]
    print(f"\nImage Name: {image_name}")
    print(f"Kustomization.yaml Location: {kustomize_file_location}")
    print(f"New Tag: {new_tag}")

    # Load kustomization.yaml
    with open(kustomize_file_location, "r") as f:
        kustomize_yaml = yaml.load(f)
    print(f"Kustomization.yaml: {kustomize_yaml}")

    # Loop through all images in the image field to match the current one
    for kustomize_image in kustomize_yaml["images"]:
        if image_name == kustomize_image["name"].removeprefix(r"icantkube/"):

            # Update image tag
            kustomize_image["newTag"] = new_tag
            print(f"Updated Kustomization.yaml: {kustomize_yaml}")

            # Write changes back to kustomization.yaml
            with open(kustomize_file_location, "w") as f:
                yaml.dump(kustomize_yaml, f)

    # Load imageConfig.yaml
    with open("imageConfig.yaml", "r") as f:
        imageConfig = yaml.load(f)

    # Update imageConfig.yaml with new tag
    imageConfig[image_name]["currentTag"] = new_tag
    print(f"Updated ImageConfig: {imageConfig}")

    # Write changes back to imageConfig.yaml
    with open("imageConfig.yaml", "w") as file:
        yaml.dump(imageConfig, file)