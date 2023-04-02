import hashlib
import randomfiletree

def random_file_tree(output_path) -> None:
    randomfiletree.iterative_gaussian_tree(
        output_path, nfiles=4.0, nfolders=2.0, maxdepth=3, repeat=2,
    )

def md5(file: str) -> str:
    hash_md5 = hashlib.md5()
    with open(file, 'rb') as _file:
        for chunk in iter(lambda: _file.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
