#include "font_manager.h"
#include "util/common.h"
#include "util/game_env.h"

namespace mengde {
namespace gui {
namespace foundation {

FontManager::FontManager(const string& base_path) : base_path_(base_path) {
  TTF_Init();

  default_font_name_ = "Literation Mono Powerline";
  //  default_font_name_ = "NanumGothicCodingBold"; // Default Font for Hangul
}

FontManager::~FontManager() {
  for (const auto& u : container_) {
    TTF_Font* font = u.second;
    TTF_CloseFont(font);
  }

  TTF_Quit();
}

TTF_Font* FontManager::FetchFont(const string& name, int size) {
  string full_path = base_path_ + "/" + name + ".ttf";
  string key       = name + ":" + std::to_string(size);

  auto iter = container_.find(key);
  if (iter == container_.end()) {
    TTF_Font* font = TTF_OpenFont(full_path.c_str(), size);
    if (font == nullptr) {
      const char* fallback_fonts[] = {
          "C:/Windows/Fonts/consola.ttf",
          "C:/Windows/Fonts/segoeui.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
          "/System/Library/Fonts/Menlo.ttc",
      };
      for (const char* fallback : fallback_fonts) {
        font = TTF_OpenFont(fallback, size);
        if (font != nullptr) break;
      }
    }
    if (font == nullptr) {
      LOG_FATAL("Unable to load a UI font: %s", TTF_GetError());
    }
    container_[key] = font;
    return font;
  } else {
    return iter->second;
  }
}

TTF_Font* FontManager::FetchDefaultFont(int size) { return FetchFont(default_font_name_, size); }

}  // namespace foundation
}  // namespace gui
}  // namespace mengde
