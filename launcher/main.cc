#include <windows.h>

#include <string>
#include <vector>

namespace {

std::wstring GetLauncherDirectory() {
  wchar_t path[MAX_PATH] = {};
  const DWORD length = GetModuleFileNameW(nullptr, path, MAX_PATH);
  if (length == 0 || length >= MAX_PATH) return L"";
  std::wstring result(path, length);
  const size_t separator = result.find_last_of(L"\\/");
  return separator == std::wstring::npos ? L"" : result.substr(0, separator);
}

bool IsFile(const std::wstring& path) {
  const DWORD attributes = GetFileAttributesW(path.c_str());
  return attributes != INVALID_FILE_ATTRIBUTES && (attributes & FILE_ATTRIBUTE_DIRECTORY) == 0;
}

bool IsDirectory(const std::wstring& path) {
  const DWORD attributes = GetFileAttributesW(path.c_str());
  return attributes != INVALID_FILE_ATTRIBUTES && (attributes & FILE_ATTRIBUTE_DIRECTORY) != 0;
}

std::wstring ReadSetting(const std::wstring& ini, const wchar_t* key, const wchar_t* fallback) {
  wchar_t value[2048] = {};
  GetPrivateProfileStringW(L"launcher", key, fallback, value, 2048, ini.c_str());
  return value;
}

void ShowError(const wchar_t* message) {
  MessageBoxW(nullptr, message, L"Ekgd - Dong Zhou Lie Guo Zhi", MB_OK | MB_ICONERROR);
}

}  // namespace

int WINAPI wWinMain(HINSTANCE, HINSTANCE, PWSTR, int) {
  const std::wstring root = GetLauncherDirectory();
  if (root.empty()) {
    ShowError(L"Unable to locate the game directory.");
    return 1;
  }

  const std::wstring ini = root + L"\\launcher.ini";
  std::wstring python = ReadSetting(ini, L"python", L".venv-rl\\Scripts\\python.exe");
  if (python.find(L':') == std::wstring::npos && python.rfind(L"\\\\", 0) != 0) {
    python = root + L"\\" + python;
  }
  std::wstring assets = ReadSetting(ini, L"assets_root", L"assets\\lzc");
  if (assets.find(L':') == std::wstring::npos && assets.rfind(L"\\\\", 0) != 0) {
    assets = root + L"\\" + assets;
  }
  const std::wstring scenario = ReadSetting(ini, L"scenario", L"dongzhou");

  if (!IsFile(python)) {
    ShowError(L"Python runtime is missing. Expected .venv-rl\\Scripts\\python.exe beside Ekgd.exe.");
    return 2;
  }
  if (!IsDirectory(assets)) {
    ShowError(L"Asset directory is missing. Update assets_root in launcher.ini.");
    return 3;
  }

  const std::wstring parameters = L"-m rl.play_gui --scenario \"" + scenario +
                                  L"\" --assets-root \"" + assets + L"\"";
  const std::wstring command_line = L"\"" + python + L"\" " + parameters;
  std::vector<wchar_t> command_buffer(command_line.begin(), command_line.end());
  command_buffer.push_back(L'\0');

  SECURITY_ATTRIBUTES security = {};
  security.nLength = sizeof(security);
  security.bInheritHandle = TRUE;
  HANDLE null_handle = CreateFileW(L"NUL", GENERIC_READ | GENERIC_WRITE,
                                   FILE_SHARE_READ | FILE_SHARE_WRITE, &security,
                                   OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
  if (null_handle == INVALID_HANDLE_VALUE) {
    ShowError(L"The game could not initialize its background process.");
    return 4;
  }

  STARTUPINFOW startup = {};
  startup.cb = sizeof(startup);
  startup.dwFlags = STARTF_USESTDHANDLES;
  startup.hStdInput = null_handle;
  startup.hStdOutput = null_handle;
  startup.hStdError = null_handle;
  PROCESS_INFORMATION process = {};
  const BOOL started = CreateProcessW(
      python.c_str(), command_buffer.data(), nullptr, nullptr, TRUE,
      CREATE_NO_WINDOW | CREATE_UNICODE_ENVIRONMENT, nullptr, root.c_str(),
      &startup, &process);
  CloseHandle(null_handle);
  if (!started) {
    ShowError(L"The game could not be started. Check launcher.ini and the Python environment.");
    return 4;
  }
  CloseHandle(process.hThread);
  CloseHandle(process.hProcess);
  return 0;
}
