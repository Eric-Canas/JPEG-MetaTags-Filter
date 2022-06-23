import os
import re

OPENING_META_TAG = b"<x:xmpmeta xmlns:x=\"adobe:ns:meta/\">"
CLOSE_META_TAG = b"</x:xmpmeta>"
FIRST_LI_OPEN = b"<rdf:li>"
FIRST_LI_CLOSE = b"</rdf:li>"

METADATA_TAG_RE = OPENING_META_TAG + b"[\s\S]*" + CLOSE_META_TAG
TAG_LIST_RE = FIRST_LI_OPEN + b"(.*?)" + FIRST_LI_CLOSE


def read_all_jpegs_in_dir(dir_path:str, recursive:bool=False) -> tuple:
    """
    Reads all jpegs in a directory and returns a list of their paths.
    """
    jpegs = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if os.path.isfile(os.path.join(root, file)):
                if file.lower().endswith(".jpg") or file.lower().endswith(".jpeg"):
                    jpegs.append(os.path.join(root, file))
            elif recursive and os.path.isdir(os.path.join(root, file)):
                jpegs.extend(read_all_jpegs_in_dir(dir_path=os.path.join(root, file), recursive=recursive))

    return tuple(jpegs)

def read_all_metadata_tags_in_files(img_paths: list | tuple) -> tuple:
    """
    Reads all tags in the metadata of all jpegs in a directory and returns a list of their paths.
    """
    tags = tuple((img_path, read_tags_in_metadata_for_img(img_path=img_path)) for img_path in img_paths)

    return tags

def read_tags_in_metadata_for_img(img_path:str) -> tuple:
    """
    Reads all tags in the metadata of a jpeg and returns a list of their paths.
    """
    with open(img_path, "rb") as f:
        # Read all the lines as bytes
        lines = b"".join(f.readlines())
        # Retrieve the metadata part of the file
        metadata = re.findall(METADATA_TAG_RE, lines)
        if len(metadata) == 0: return None
        elif len(metadata) == 1: metadata = metadata[0]
        else: raise ValueError("Multiple metadata tags found in the file.")
        # Get a list with every tag.
        tags = re.findall(TAG_LIST_RE, metadata)
        # Transform all the tags to strings
        tags = tuple(tag.decode("utf-8") for tag in tags)
    return tags

def files_containing_tags(paths_and_tags: tuple[tuple[str, tuple[str, ...]]], tags: tuple[str] | list[str],
                          mode:str="any") -> tuple[str]:
    """
    Returns a list of paths of files containing all the tags in the given list.
    """
    if mode.lower() == "all":
        return tuple(path for path, tags_in_path in paths_and_tags if all(tag is not None and tag in tags_in_path for tag in tags))
    elif mode.lower() == "any":
        return tuple(path for path, tags_in_path in paths_and_tags if any(tag is not None and tag in tags_in_path for tag in tags))
    else:
        raise ValueError("Invalid mode: {}".format(mode))