from simplepng.utils.crc import *
from simplepng.utils.const import *


class Chunks(object):
    def __init__(self, length: int, chunktype: str):
        self.length = length  # 数据长度
        self.chunktype = chunktype  # 类型码


class IHDR(Chunks):
    def __init__(self, length, chunktype, width, height, bit_depth, colortype, compression_method=0x00,
                 filter_method=0x00, interlace_method=0x00):
        super(IHDR, self).__init__(length, chunktype)
        self.width = width  # 图片宽度
        self.height = height  # 图片高度
        self.bit_depth = bit_depth  # 图片深度
        self.colortype = colortype  # 颜色类型
        self.compression_method = compression_method  # 压缩方法,默认0x00(LZ77派生算法)
        self.filter_method = filter_method  # 滤波器方法,默认0x00
        self.interlace_method = interlace_method  # 隔行扫描方法,默认0x00

    def ihdr_data(self) -> bytes:
        chunktp = bytes(self.chunktype.encode('utf8'))  # 数据块类型
        lth = self.length.to_bytes(4, 'big', signed=False)  # 数据块长度
        wth = self.width.to_bytes(4, 'big', signed=False)  # 图片宽度
        hth = self.height.to_bytes(4, 'big', signed=False)  # 图片高度
        dth, colortp = bytes([self.bit_depth]), bytes([self.colortype])  # 色深，颜色类型
        cm, fm, im = bytes([self.compression_method]), bytes([self.filter_method]), bytes([self.interlace_method])
        chunkdata = chunktp + wth + hth + dth + colortp + cm + fm + im
        crc = calc_crc32(chunkdata)
        return lth + chunkdata + crc


def idat_data(png) -> bytes:
    sources = []
    bytesdata = bytes()
    for x in range(len(png)):
        sources.append([0x00])  # 每行开头添加滤波器方法0x00
        for y in range(len(png[x])):
            sources.append(COLOR[png[x][y]])
    for i in sources:
        bytesdata += bytes(i)
    compressdata = zlib.compress(bytesdata)  # 压缩后数据
    crc = calc_crc32(compressdata)  # 计算compressdata的crc
    compressdatalen = len(compressdata).to_bytes(4, 'big', signed=False)  # 数据块长度
    return compressdatalen + b'IDAT' + compressdata + crc


class IEND(Chunks):
    def __init__(self, length=0, chunktype=PNG_IEND):
        super(IEND, self).__init__(length, chunktype)

    def iend_data(self):
        lth = self.length.to_bytes(4, 'big', signed=False)
        data = bytes(self.chunktype)
        crc = bytes(PNG_IEND_CRC)
        return lth + data + crc


def write_memory(filename: str, crc_bytes: bytes):
    with open(filename, "wb") as f:
        f.write(crc_bytes)


class Simplepng(object):
    def __init__(self, image_sources: list[list[int]], width: int, height: int, target_filename: str):
        self.image = image_sources
        self.width = width
        self.height = height
        self.target_filename = target_filename

    def run(self):
        ihdr = IHDR(PNG_IHDR_LEN, 'IHDR', self.width, self.height, 8, 2)
        iend = IEND()
        header = bytes(PNG_SIGNATURE_HEADER)  # PNG签名
        ihdr_dt = ihdr.ihdr_data()
        idat_dt = idat_data(self.image)
        iend_dt = iend.iend_data()
        final_data = header + ihdr_dt + idat_dt + iend_dt
        write_memory('{}.png'.format(self.target_filename), final_data)
        print("Completed!")
