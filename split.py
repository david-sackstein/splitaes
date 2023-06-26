import struct


# Define the data for each block
blocks = [
    (1, 10),  # Block 1: All 1's of size 100
    (2, 11),  # Block 2: All 2's of size 200
    (3, 45)  # Block 3: All 3's of size 300
]


def create_file(file_name):
    with open(file_name, "wb") as file:
        for value, size in blocks:
            # Write the size in network byte order (!H) as a 2-byte integer
            file.write(struct.pack('!H', size))

            # Write the block data by repeating the value 'size' times
            file.write(struct.pack('B', value) * size)


def split_file(file_name, max_size):

    acc_data = []
    index = 0
    with open(file_name, "rb") as file:
        while True:
            data = file.read(2)

            if not data:  # Reached EOF
                break

            # Unpack the 2-byte integer using network byte order (big-endian)
            size = struct.unpack('!H', data)[0]

            acc_data += file.read(size)

            if len(acc_data) > max_size:
                # Write acc_data to file with index
                partial_name = file_name + f'index'
                # Write the data to the file named partial_name

                # Increment the index and zero acc_data
                index += 1
                acc_data = []
                pass

            # Advance the position by the value of the 2 bytes read
            file.seek(size, 1)


filename = "binary_file"

create_file(filename)

split_file(filename, 12)