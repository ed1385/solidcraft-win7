import pefile,sys,json
BAD={'GetOverlappedResultEx','PathCchStripPrefix','RoOriginateErrorW','CoTaskMemFree','CoCreateFreeThreadedMarshaler'}
BADDLL={'combase.dll','api-ms-win-core-path-l1-1-0.dll','api-ms-win-core-winrt-error-l1-1-0.dll'}
for f in sys.argv[1:]:
    pe=pefile.PE(f,fast_load=True); pe.parse_data_directories(directories=[1])
    for i,d in enumerate(pe.DIRECTORY_ENTRY_IMPORT):
        names=[x.name.decode() if x.name else f'#{x.ordinal}' for x in d.imports]
        hit=[n for n in names if n in BAD]
        if hit or d.dll.decode().lower() in BADDLL:
            print(f,i,d.dll.decode(),len(names),hit)
