import zlib
import random

# Function to read the PNG signature
def read_png_signature(filename):
    with open(filename, 'rb') as png_file:
        signature = png_file.read(8)
        
        if signature != b'\x89PNG\r\n\x1A\n':
            raise ValueError("Not a valid PNG file")
        
        print("Valid PNG signature found.")

# Function to extract PNG width, height, and IDAT data
def extract_png_info(filename):
    width, height = None, None
    idat_data = b''

    with open(filename, 'rb') as png_file:
        png_file.read(8)  # skip the PNG signature
        
        while True:
            length_bytes = png_file.read(4)  # read the next 4 bytes to get the length of the chunk
            if not length_bytes:
                break
            
            length = int.from_bytes(length_bytes, 'big')
            chunk_type = png_file.read(4).decode('ascii')
            chunk_data = png_file.read(length)
            png_file.read(4)  # CRC
            
            if chunk_type == 'IHDR':
                width = int.from_bytes(chunk_data[0:4], 'big')
                height = int.from_bytes(chunk_data[4:8], 'big')
                print(f"Image dimensions: {width}x{height}") 
            elif chunk_type == 'IDAT':
                idat_data += chunk_data  # Append IDAT data
                print(f'Found IDAT chunk of length {length}')
    
    if width is None or height is None:
        raise ValueError("IHDR chunk not found or dimensions not available.")

    return width, height, idat_data


def decompress_idat_data(idat_data):
    return zlib.decompress(idat_data)

def embed_message(pixels, message):
    random.seed(100)
    message += '\0'  # null terminator
    message_bits = ''.join(format(ord(c), '08b') for c in message)  # Converts each character to binary
    
    pixel_array = bytearray(pixels)

    total_pixels = len(pixel_array)
    indices = random.sample(range(total_pixels), len(message_bits))  # Randomly select pixel indices to modify

    for i, bit in enumerate(message_bits):
        pixel_index = indices[i]
        pixel_array[pixel_index] = (pixel_array[pixel_index] & ~1) | int(bit)  # Modify LSB of chosen pixels
    
    return bytes(pixel_array)

# Calculate embedding capacity
def calculate_embedding_capacity(width, height):
    max_chars = (width * height * 3) // 8
    print(f"The maximum number of characters you can embed is {max_chars} characters.")
    return max_chars

# Function to save modified pixel data back to a new PNG
def save_png(filename, pixel_data, width, height):
    compressed_data = zlib.compress(pixel_data)
    new_idat_chunk = (
        len(compressed_data).to_bytes(4, 'big') +
        b'IDAT' +
        compressed_data +
        (zlib.crc32(b'IDAT' + compressed_data) & 0xffffffff).to_bytes(4, 'big')
    )
    
    with open(filename, 'wb') as png_file:
        png_file.write(b'\x89PNG\r\n\x1A\n')  # Write PNG signature
        
        # Write IHDR chunk
        ihdr_data = (
            width.to_bytes(4, 'big') +
            height.to_bytes(4, 'big') +
            b'\x08' +  # Bit depth
            b'\x02' +  # Color type (RGB)
            b'\x00' +  # Compression method
            b'\x00' +  # Filter method
            b'\x00'    # Interlace method
        )
        ihdr_length = len(ihdr_data).to_bytes(4, 'big')
        ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
        
        # Write IHDR chunk
        png_file.write(ihdr_length)
        png_file.write(b'IHDR')
        png_file.write(ihdr_data)
        png_file.write(ihdr_crc.to_bytes(4, 'big'))

        # Write IDAT chunk
        png_file.write(new_idat_chunk)
        
        # Write IEND chunk
        png_file.write(b'\x00\x00\x00\x00IEND' + b'\xaeB\x82')

# Main function to embed a message into a PNG image
def main():
    input_filename = 'image.png'
    output_filename = 'modified_image.png' 
    secret_message = " "

    try:
        read_png_signature(input_filename)

        width, height, idat_chunks = extract_png_info(input_filename)

        decompressed_pixels = decompress_idat_data(idat_chunks)

        embedded_pixels = embed_message(decompressed_pixels, secret_message)

        save_png(output_filename, embedded_pixels, width, height)

        calculate_embedding_capacity(width, height)

        print(f"Message embedded successfully into {output_filename}.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
