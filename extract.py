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
        png_file.read(8)  # skip the PNG signature

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

def extract_message_pixels(raw_pixels, message_length):
    random.seed(100)
    total_pixels = len(raw_pixels)
    indices = random.sample(range(total_pixels), message_length * 8)
    message_bits = ''

    for idx in indices:
        message_bits += str(raw_pixels[idx] & 1)

    message = ''
    for i in range(0, len(message_bits), 8):
        byte = message_bits[i:i+8]
        if len(byte) < 8:
            break
        char = chr(int(byte, 2))
        if char == '\0':
            break
        message += char

    return message

def main():
    input_filename = 'modified_image.png'
    estimated_message_length = 1500  # Adjust if needed

    try:
        read_png_signature(input_filename)
        width, height, idat_chunks = extract_png_info(input_filename)
        decompressed_data = decompress_idat_data(idat_chunks)
        raw_pixels = unfilter_scanlines(decompressed_data, width, height, 3)
        extracted_message = extract_message_pixels(raw_pixels, estimated_message_length)
        print(f"Extracted message: {extracted_message}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
