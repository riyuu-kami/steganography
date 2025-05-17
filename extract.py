import random
import zlib
from embed import unfilter_scanlines

def read_png_signature(filename):
    with open(filename, 'rb') as png_file:
        signature = png_file.read(8)
        if signature != b'\x89PNG\r\n\x1A\n':
            raise ValueError("Not a valid PNG file")

def extract_png_info(filename):
    width, height = None, None
    idat_data = b''

    with open(filename, 'rb') as png_file:
        png_file.read(8)  # skip PNG signature

        while True:
            length_bytes = png_file.read(4)
            if not length_bytes:
                break
            length = int.from_bytes(length_bytes, 'big')
            chunk_type = png_file.read(4)
            chunk_data = png_file.read(length)
            png_file.read(4)  # CRC
            if chunk_type == b'IHDR':
                width = int.from_bytes(chunk_data[0:4], 'big')
                height = int.from_bytes(chunk_data[4:8], 'big')
            elif chunk_type == b'IDAT':
                idat_data += chunk_data

    if width is None or height is None:
        raise ValueError("IHDR chunk not found or dimensions not available.")

    return width, height, idat_data

def decompress_idat_data(idat_data):
    return zlib.decompress(idat_data)

def extract_embedded_file(raw_pixels):
    random.seed(100)
    total_pixels = len(raw_pixels)

    # extract length bits indices:
    length_indices = random.sample(range(total_pixels), 32)
    length_bits = [str(raw_pixels[idx] & 1) for idx in length_indices]
    file_length = int(''.join(length_bits), 2)
    
    random.seed(100) # resetting seed
    all_indices = random.sample(range(total_pixels), 32 + file_length * 8)

    # extract bits for file bytes (skip first 32 used for length)
    data_bits = []
    for idx in all_indices[32:]:
        data_bits.append(str(raw_pixels[idx] & 1))

    # convert bits to bytes
    file_bytes = bytearray()
    for i in range(0, len(data_bits), 8):
        byte_bits = data_bits[i:i+8]
        if len(byte_bits) < 8:
            break
        file_bytes.append(int(''.join(byte_bits), 2))

    return bytes(file_bytes)


def main():
    input_filename = 'modified_image.png'
    output_file = ''

    try:
        read_png_signature(input_filename)
        width, height, idat_chunks = extract_png_info(input_filename)
        decompressed_data = decompress_idat_data(idat_chunks)
        raw_pixels = unfilter_scanlines(decompressed_data, width, height, 3)

        extracted_file_bytes = extract_embedded_file(raw_pixels)

        with open(output_file, 'wb') as f:
            f.write(extracted_file_bytes)

        print(f"Extracted file saved as: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
