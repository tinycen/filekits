from PIL import Image
from imagehash import phash, dhash, whash
from ..base_io import download_file, clear_folder, StrPath


def dedup_images( image_urls: list,  download_dir: StrPath ):
    clear_folder(download_dir)

    # 感知哈希阈值：两张图对应哈希的汉明距离 ≤ 阈值即判为重复。
    # 值越大容忍的差异越多（默认 5）
    phash_threshold = dhash_threshold = whash_threshold = 5

    image_hashes = []
    unique_images = []
    downloaded = set()
    for url in image_urls:
        if url in downloaded:
            continue
        image_path = download_file(url, download_dir, return_type="path")
        assert isinstance(image_path, str)
        downloaded.add(url)
        with Image.open(image_path) as img:
            hash_p = phash(img)
            hash_d = dhash(img)
            hash_w = whash(img)
            is_duplicate = False
            for exist_hash in image_hashes:
                # 三个哈希均满足"汉明距离 ≤ 阈值"才判定为重复
                if (
                    (hash_p - exist_hash['phash'] <= phash_threshold) and
                    (hash_d - exist_hash['dhash'] <= dhash_threshold) and
                    (hash_w - exist_hash['whash'] <= whash_threshold)
                ):
                    is_duplicate = True
                    break
            if not is_duplicate:
                image_hashes.append({'phash': hash_p, 'dhash': hash_d, 'whash': hash_w})
                unique_images.append(url)
    clear_folder(download_dir)

    return unique_images
