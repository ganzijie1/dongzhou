#include "game_env.h"
#include <cstdlib>
#include "SDL.h"

GameEnv::GameEnv() {
  const char* configured_path = std::getenv("MENGDE_GAME_PATH");
  if (configured_path != nullptr && configured_path[0] != '\0') {
    game_path_ = Path(string(configured_path));
  } else {
    char* basepath = SDL_GetBasePath();
    game_path_     = Path(string(basepath));
    SDL_free(basepath);
  }

  resource_path_ = game_path_ / "res";
  scenario_path_ = game_path_ / "sce";
}

const GameEnv* GameEnv::GetInstance() {
  static GameEnv instance;
  return &instance;
}
