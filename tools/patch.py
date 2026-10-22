import pefile,sys,shutil
BAD={'GetOverlappedResultEx','PathCchStripPrefix','RoOriginateErrorW','CoTaskMemFree','CoCreateFreeThreadedMarshaler'}
NEW=b'w7shim.dll'
needed={}
for f in sys.argv[1:]:
    pe=pefile.PE(f,fast_load=True); pe.parse_data_directories(directories=[1])
    rvas=set()
    for d in pe.DIRECTORY_ENTRY_IMPORT:
        if any(x.name and x.name.decode() in BAD for x in d.imports): rvas.add(d.struct.Name)
    for d in pe.DIRECTORY_ENTRY_IMPORT:
        if d.struct.Name in rvas:
            for x in d.imports: needed[x.name.decode()]=d.dll.decode()
    data=bytearray(open(f,'rb').read())
    for r in rvas:
        off=pe.get_offset_from_rva(r); old=bytes(data[off:off+64]).split(b'\0')[0]
        assert len(NEW)<=len(old)
        data[off:off+len(old)]=NEW+b'\0'*(len(old)-len(NEW))
        print(f,old.decode(),'->',NEW.decode())
    for d in pe.DIRECTORY_ENTRY_IMPORT:
        if d.dll.decode().lower()=='opengl32.dll':
            off=pe.get_offset_from_rva(d.struct.Name); old=bytes(data[off:off+64]).split(b'\0')[0]
            data[off:off+len(old)]=b'w7gl.dll'+b'\0'*(len(old)-8); print(f,'opengl32.dll -> w7gl.dll')
    pe.close(); open(f,'wb').write(data)
import json; json.dump(needed,open('needed.json','w'),indent=0); print(needed)
