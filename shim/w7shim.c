/* w7shim.dll: Windows 8+ functions SolidCraft imports, implemented for Windows 7 SP1. */
#include <windows.h>
BOOL WINAPI w7_GetOverlappedResultEx(HANDLE h, LPOVERLAPPED ov, LPDWORD n, DWORD ms, BOOL alertable) {
    if (ms == 0) return GetOverlappedResult(h, ov, n, FALSE);
    if (ms == INFINITE && !alertable) return GetOverlappedResult(h, ov, n, TRUE);
    HANDLE ev = ov->hEvent ? ov->hEvent : h;
    DWORD r = WaitForSingleObjectEx(ev, ms, alertable);
    if (r == WAIT_TIMEOUT) { SetLastError(WAIT_TIMEOUT); return FALSE; }
    if (r == WAIT_IO_COMPLETION) { SetLastError(WAIT_IO_COMPLETION); return FALSE; }
    if (r != WAIT_OBJECT_0) return FALSE;
    return GetOverlappedResult(h, ov, n, FALSE);
}
HRESULT WINAPI w7_PathCchStripPrefix(PWSTR p, SIZE_T cch) {
    if (!p) return E_INVALIDARG;
    if (cch >= 8 && wcsncmp(p, L"\\\\?\\UNC\\", 8) == 0) {
        size_t len = wcslen(p + 8);
        p[0] = L'\\'; p[1] = L'\\';
        memmove(p + 2, p + 8, (len + 1) * sizeof(WCHAR));
        return S_OK;
    }
    if (cch >= 4 && wcsncmp(p, L"\\\\?\\", 4) == 0 && p[4] && p[5] == L':') {
        size_t len = wcslen(p + 4);
        memmove(p, p + 4, (len + 1) * sizeof(WCHAR));
        return S_OK;
    }
    return S_FALSE;
}
BOOL WINAPI w7_RoOriginateErrorW(HRESULT e, UINT len, PCWSTR msg) { (void)e; (void)len; (void)msg; return FALSE; }
BOOL WINAPI DllMain(HINSTANCE h, DWORD r, LPVOID p) { (void)h; (void)r; (void)p; return TRUE; }
