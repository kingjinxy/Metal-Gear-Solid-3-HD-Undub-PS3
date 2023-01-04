import os
import sys
import struct

def get_u32_le(buf, offset):
    return struct.unpack("<I", buf[offset:offset+4])[0]

def put_u32_le(buf, offset, n):
    buf[offset:offset+4] = struct.pack("<I", n)

extmap = {
    0x00000001: ".genh",   # ADPCM -> GENH / ".sdx_0"
    0x00000002: ".dmx",    # this container was found on Zone of the Enders HD Remaster
	0x00000003: ".nrm",
    0x00000004: ".pacb",   # has "PACB" magic not seen in any of the original versions the HD remaster was based on
    0x00000005: ".dmx",    # ditto
    0x00000006: ".bpx",    
    0x0000000c: ".pac",    # XBOX version of MGS2 - MPEG2 video format
    0x0000000d: ".pac",    # XBOX version of MGS2 - MPEG2 video format
	0x0000000e: ".pss",    # PS2 version of MGS2 - MPEG2 video format
	0x0000000f: ".ipu",    # PS2 version of MGS2 - MPEG2 video format
    0x00000020: ".m2v",    # this container is present even on all versions of the HD remaster(PS3, XBOX360, PSVITA), regardless of format
    0x00010001: ".sdx_1",
	0x00010004: ".sub_en", # it's a made-up container, becuase in the executable of those Metal Gear Solid PS2 games there's no indication of a container used for these formats
    0x00020001: ".sdx_2",
	0x00020004: ".sub_fr", # ditto
    0x00030001: ".msf",    # PS3 HD remaster audio format
	0x00030004: ".sub_de", # ditto
	0x00040001: ".xwma",   # XBOX360 HD remaster audio format
	0x00040004: ".sub_it", # ditto
	0x00050001: ".9tav",   # PSVITA HD remaster audio format
	0x00050004: ".sub_es", # ditto
	0x00060004: ".sub_jp", # ditto
	0x00070004: ".sub_jp", # ditto
    0x00100001: ".vag",    # VAG1/VAG2 format
    0x00110001: ".mtaf",   # MTAF format

    #0x00000002: ".xxxx",
    #0x00000005: ".xxxx",
    #0x00010006: ".xxxx",
    #0x00020006: ".xxxx",
    #0x00030006: ".xxxx",
    #0x00040006: ".xxxx",
    #0x00050006: ".xxxx",
    #0x00070006: ".xxxx",
}

"""
Header (16 Bytes):
ID SIZE X STREAM_ID

"""





def read_stream_sections(sdt_path):
    streams = {}
    stream_extensions = {}

    if not os.path.isfile(sdt_path):
        print("Invalid path for the SDT file")
        exit()
    
    if not os.path.splitext(sdt_path)[-1] == ".sdt":
        print("Not an SDT file!")
        exit()
    
    # open the sdt
    with open(sdt_path, "rb") as sdt:
        # get the file size
        sdt_size = os.path.getsize(sdt_path)

        last_stream_id = None
        last_stream_section_bytes = 0
        subsections = 0

        # iterate over all bytes in the file
        while (sdt.tell() < sdt_size):
            # read the header for the subsection
            header = sdt.read(16)
            header_id = get_u32_le(header, 0x00) # what type of header we have

            if header_id == 0xF0:
                print(f"End of File")
                # end of file header found
                break
            elif header_id == 0x10:
                # register a new stream
                stream_id = get_u32_le(header, 0x0C)

                # failure state,
                if stream_id in streams:
                    print("0x%08X: stream already registered once: %08X" % (sdt.tell() - 16, stream_id))
                    return 1
                
                # assign the extension to the stream_id
                if stream_id in extmap:
                    stream_extensions[stream_id] = extmap[stream_id]
                else:
                    stream_extensions[stream_id] = ".bin"
                
                # setup an empty list for all of the byte data for the individual stream
                streams[stream_id] = []

                print(f"Register Stream: {stream_id:x} ({stream_extensions[stream_id]})")

            elif header_id in streams:
                if not header_id == last_stream_id and last_stream_id:
                    # print(f"\tRead {last_stream_id:x} ({stream_extensions[last_stream_id]}): {last_stream_section_bytes} bytes in {subsections} subsections")
                    last_stream_section_bytes = 0
                    subsections = 0
                
                if len(streams[header_id]) == 0:
                    print(f"\t{stream_extensions[header_id]} first encountered at {sdt.tell()}")

                # read data into the stream lists
                size = get_u32_le(header, 0x04) - 16
                data = sdt.read(size)

                

                streams[header_id].append(data)

                last_stream_id = header_id

                last_stream_section_bytes += size
                subsections += 1

            else:
                print("0x%08X: unregistered stream / unknown header ID: %08X" % (sdt.tell() - 16, header_id))
                return 1
    
    """
    Summary
    """
    for key in streams.keys():
        n_bytes = 0
        for section in streams[key]:
            n_bytes += len(section)
        
        print(f"\t{stream_extensions[key]} with {len(streams[key])} sections with {n_bytes} bytes")
    
                



            


if __name__ == "__main__":
    for i in range(len(sys.argv) - 1):
        file = sys.argv[i + 1]
        read_stream_sections(file)
