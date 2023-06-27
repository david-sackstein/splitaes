import struct


# Define the data for each block as (value, size)
blocks = [
    (1, 10),
    (2, 10),
    (3, 10),
    (4, 10)
]


def create_file(file_name):
    with open(file_name, "wb") as file:
        for value, size in blocks:
            # Write the size in network byte order (!H) as a 2-byte integer
            file.write(struct.pack('!H', size))

            # Write the block data by repeating the value 'size' times
            file.write(struct.pack('B', value) * size)


# A chunk is a piece of the original file that
# - contains whole lines (a line is 2 bytes of size followed by size bytes of encrypted data).
# - is not larger than the max_chunk_size
# ChunkWriter writes chunks, switching to a new chunk whenever appending a new line would exceed the max_chunk_size.
class ChunkWriter:
    def __init__(self, base_name, max_chunk_size):
        self.index = 0
        self.base_name = base_name
        self.max_chunk_size = max_chunk_size
        self.chunk_file = None
        self.acc_chunk_size = 0
        self.new_chunk()

    def new_chunk(self):
        # close the chunk file, (if not None), before creating a new one
        self.close()

        # increase the index and reset the accumulated size to 0
        self.index = self.index + 1
        self.acc_chunk_size = 0

        # open a new chunk file
        chunk_file_name = f"{self.base_name}.{self.index:02d}.bin"
        self.chunk_file = open(chunk_file_name, "wb")

    def write_line(self, line_bytes, line_size):
        # If it is too large for the current chunk, tell the writer to close
        # the current chunk and open a new one.
        if self.acc_chunk_size + line_size > self.max_chunk_size:
            self.new_chunk()

        # Write the line as the two bytes line_size followed by the line bytes.
        self.chunk_file.write(struct.pack('!H', line_size))
        self.chunk_file.write(line_bytes)

        # Accumulate the size
        self.acc_chunk_size += line_size

    def close(self):
        if self.chunk_file:
            self.chunk_file.close()


def split_file(file_name, max_chunk_size):

    # Open the original_file
    with open(file_name, "rb") as original_file:

        writer = ChunkWriter(file_name, max_chunk_size)

        write_chunks(original_file, writer)

        writer.close()


def write_chunks(original_file, writer):

    while True:

        # Read the size of the next line
        size_bytes = original_file.read(2)
        if not size_bytes:
            break

        line_size = struct.unpack('!H', size_bytes)[0]

        # Now read the line
        line_bytes = original_file.read(line_size)
        if not line_bytes:
            # This is actually an error because line_size is expected to be greater than zero
            break

        # Write it to the chunk
        writer.write_line(line_bytes, line_size)


filename = "binary_file"

create_file(filename)

split_file(filename, 20)
