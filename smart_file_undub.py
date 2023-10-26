"""
Smart Undubbing

Copies .vag and .msf sections from one .sdt to another for MGS3.
The files must corrsepond across dubs and have the same number of audio sections.

Written by Matthew Tran (giantlightbulb@gmail.com) with substantial reference to AnonRunzes's
sdt_demux.py
"""
import struct
import os

def get_u32_le(buf, offset):
    return struct.unpack("<I", buf[offset:offset+4])[0]

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

class Section:
    """
    Section of a .sdt file
    """
    def __init__(self, header, data):
        self.header = header
        self.data = data
    
    def get_header_id(self):
        return get_u32_le(self.header, 0x00)
    
    def get_stream_id(self):
        return get_u32_le(self.header, 0x0C)
    
    def get_size(self):
        return get_u32_le(self.header, 0x04) - 16
    
    def get_extension(self):
        if self.get_header_id() == 0x10:
            stream_id = self.get_stream_id()
        else:
            stream_id = self.get_header_id()
        
        if stream_id in extmap.keys():
            return extmap[stream_id]
        else:
            return ".bin"
        

        
        
    
    def to_bytes(self):
        if self.data:
            return self.header + self.data
        else:
            return self.header

def read_in_sections(sdt_path):
    """
    Read in all of the sections for a .sdt file at some path
    """
    sections = []

    streams = [] # list of all registered streams

    if not os.path.isfile(sdt_path):
        raise Exception(f"{sdt_path} Invalid path for the SDT file")
    
    if not os.path.splitext(sdt_path)[-1] == ".sdt":
        raise Exception(f"{sdt_path} is not an SDT file!")

    sdt_size = os.path.getsize(sdt_path)

    # open the sdt
    with open(sdt_path, "rb") as sdt:
        # iterate over all bytes in the file
        while (sdt.tell() < sdt_size):
            header = sdt.read(16)
            header_id = get_u32_le(header, 0x00) # what type of header we have

            if header_id == 0xF0:
                # end of file header
                end_section = Section(header, None)
                sections.append(end_section)
                break
            elif header_id == 0x10:
                # register a new stream
                stream_id = get_u32_le(header, 0x0C)

                # failure state,
                if stream_id in streams:
                    print("0x%08X: stream already registered once: %08X" % (sdt.tell() - 16, stream_id))
                    exit()
                
                streams.append(stream_id)

                register_section = Section(header, None)
                sections.append(register_section)
            elif header_id in streams:
                # read in header data section
                size = get_u32_le(header, 0x04) - 16
                data = sdt.read(size)

                # add the stream data section to the list of sections
                data_section = Section(header, data)
                sections.append(data_section)
            else:
                print("0x%08X: unregistered stream / unknown header ID: %08X" % (sdt.tell() - 16, header_id))
                exit()
    
    return sections, streams

def chunk_sections(sections):
    last_header_id = None
    
    chunks = []
    chunk_data = []
    
    for section in sections:
        header_id = section.get_header_id()
        
        if not header_id == last_header_id and last_header_id:
            chunks.append(chunk_data)
            chunk_data = []
		
        chunk_data.append(section)
        
        last_header_id = header_id
    
    chunks.append(chunk_data)
    
    return chunks

def smart_stitch(source_sdt_path, target_sdt_path):
    """
    Intelligently stiches two .sdt files based on file sections.
    Currently manages .msf and .vag formatted sections
    """
    supported_formats = [".vag", ".xwma"]

    # read in all of the file sections
    source_sections, source_streams = read_in_sections(source_sdt_path)
    target_sections, target_streams = read_in_sections(target_sdt_path)
    
    # chunk the sections by header_id 
    source_chunks = chunk_sections(source_sections)
    target_chunks = chunk_sections(target_sections)
    
    source_audio_chunks = [chunk for chunk in source_chunks if (chunk[0].get_extension() in supported_formats and (not chunk[0].get_header_id() == 0x10))]
    
    if len(source_streams) == 1 and extmap[source_streams[0]] in supported_formats:
        # audio only file, just copy the source data over the target
        output_sections = source_sections
    else:
        output_sections = []
        audio_chunk_index = 0
        
        # stitch the files together
        for i in range(len(target_chunks)):
            target_chunk = target_chunks[i]
            # make sure we're not working with a header
            if (target_chunk[0].get_extension() in supported_formats) and (not target_chunk[0].get_header_id() == 0x10):
                # working with an audio chunk
                if audio_chunk_index >= len(source_audio_chunks):
                    continue
                
                # verify that the extensions are the same
                if not target_chunk[0].get_extension() == source_audio_chunks[audio_chunk_index][0].get_extension():
                    raise Exception("Mismatch audio formats")

                # add the Japanese audio chunk to the end
                output_sections += source_audio_chunks[audio_chunk_index]
                audio_chunk_index += 1
                
            else:
                output_sections += target_chunk
        
        # catch extra japanese audio chunks at the end
        while audio_chunk_index < len(source_audio_chunks):
            output_sections += source_audio_chunks[audio_chunk_index]
            audio_chunk_index += 1
    

    # convert the sections back into bytes
    output_byte_sections = [section.to_bytes() for section in output_sections]

    # join and return them as a total data stream
    return b"".join(output_byte_sections)

def dumb_stitch(source_sdt_path, target_sdt_path):
    """
    Stupidly stiches two .sdt files based on file sections. Alternates between dubs. Don't use this.
    Currently manages .msf and .vag formatted sections
    """
    supported_formats = [".vag", ".msf"]

    source_sections = read_in_sections(source_sdt_path)
    target_sections = read_in_sections(target_sdt_path)

    source_audio_sections = [section for section in source_sections if section.get_extension() in supported_formats]

    audio_index = 0

    output_sections = []
    for i in range(len(target_sections)):
        section = target_sections[i]
        if section.get_extension() in supported_formats:
            if audio_index % 2 == 0:
                output_sections.append(source_audio_sections[audio_index])
            else:
                output_sections.append(target_sections[i])

            audio_index += 1
        else:
            output_sections.append(target_sections[i])

    output_byte_sections = [section.to_bytes() for section in output_sections]

    return b"".join(output_byte_sections)

if __name__ == "__main__":
    japanese_file = "[Input 1 - JPN audio] m010_010_p010.sdt"
    english_file = "]Input 2 - US subitles] m010_010_p010.sdt"

    # correctly copies Japanese audio into the US caption stream
    stitched_data = smart_stitch(japanese_file, english_file)
    with open("smart_output.sdt", "wb") as output_file:
        output_file.write(stitched_data)

    # alternates audio streams
    stitched_data = dumb_stitch(japanese_file, english_file)
    with open("dumb_output.sdt", "wb") as output_file:
        output_file.write(stitched_data)