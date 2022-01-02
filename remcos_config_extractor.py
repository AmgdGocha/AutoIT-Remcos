import sys
import pefile
from arc4 import ARC4

def rc4_decrypt(key, data):
    cipher = ARC4(key)
    return cipher.decrypt(data).decode('latin1')

def extract_the_config(remcos_agent):
    offset = 0x0
    size = 0x0
    for rsrc in remcos_agent.DIRECTORY_ENTRY_RESOURCE.entries:
        for entry in rsrc.directory.entries:
            if str(entry.name) == 'SETTINGS':
                offset = entry.directory.entries[0].data.struct.OffsetToData
                size = entry.directory.entries[0].data.struct.Size
                break
        if offset or size:
            break
    return remcos_agent.get_memory_mapped_image()[offset: offset+size]

if __name__ == '__main__':
    remcos_agent = pefile.PE(sys.argv[1])
    config = extract_the_config(remcos_agent)
    key_len = config[0]
    key = config[1: key_len + 1]
    encrpted_config = config[key_len + 1:]
    print(rc4_decrypt(key, encrpted_config))
