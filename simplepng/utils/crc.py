# Cyclic Redundancy Checksum
import zlib


def calc_crc32(origin_data: bytes) -> bytes:
    crc_int = zlib.crc32(origin_data)  # 计算crc32
    crc_bytes = crc_int.to_bytes(4, byteorder='big', signed=False)
    return crc_bytes



