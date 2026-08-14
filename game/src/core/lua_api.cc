#include "lua_api.h"

#include "cmd.h"
#include "game.h"
#include "lua/lua.h"

using namespace mengde::core;

static Vec2D GetVec2DFromLua(lua::Lua* lua) {
  vector<int> vec = lua->Pop<vector<int>>();
  return {vec[0], vec[1]};
}

#define LUA_IMPL(cname) int Game_##cname(lua_State* L)

LUA_IMPL(AppointHero) {
  lua::Lua lua(L);
  uint16_t level = lua.Pop<uint16_t>();
  string   id    = lua.Pop<string>();
  Game*    game  = lua.Pop<Game*>();

  game->AppointHero(id, level);

  return 0;
}

LUA_IMPL(GenerateOwnUnit) {
  lua::Lua lua(L);
  Vec2D    pos  = GetVec2DFromLua(&lua);
  string   id   = lua.Pop<string>();
  Game*    game = lua.Pop<Game*>();

  int unit_no = game->GenerateOwnUnit(id, pos);

  lua.PushToStack(unit_no);
  return 1;
}

LUA_IMPL(GenerateUnit) {
  lua::Lua lua(L);
  Vec2D    pos   = GetVec2DFromLua(&lua);
  Force    force = (Force)lua.Pop<int>();
  uint16_t level = lua.Pop<uint16_t>();
  string   id    = lua.Pop<string>();
  Game*    game  = lua.Pop<Game*>();

  int unit_no = game->GenerateUnit(id, level, force, pos);

  lua.PushToStack(unit_no);
  return 1;
}

LUA_IMPL(SetUnitInvulnerable) {
  lua::Lua lua(L);
  bool     enabled = lua.Pop<bool>();
  string   id      = lua.Pop<string>();
  Game*    game    = lua.Pop<Game*>();

  game->ForEachUnit([&](Unit* unit) {
    if (!unit->IsDead() && unit->GetId() == id) unit->SetInvulnerable(enabled);
  });
  return 0;
}
LUA_IMPL(SetForceDirection) {
  lua::Lua lua(L);
  Direction direction = static_cast<Direction>(lua.Pop<int>());
  Force     force     = static_cast<Force>(lua.Pop<int>());
  Game*     game      = lua.Pop<Game*>();

  game->ForEachUnit([&](Unit* unit) {
    if (!unit->IsDead() && unit->GetForce() == force) unit->SetDirection(direction);
  });
  return 0;
}
LUA_IMPL(SetUnitDirection) {
  lua::Lua lua(L);
  Direction direction = static_cast<Direction>(lua.Pop<int>());
  int       unit_id   = lua.Pop<int>();
  Game*     game      = lua.Pop<Game*>();

  game->GetUnit(unit_id)->SetDirection(direction);
  return 0;
}
LUA_IMPL(ObtainEquipment) {
  lua::Lua lua(L);
  uint16_t amount = lua.Pop<uint16_t>();
  string   id     = lua.Pop<string>();
  Game*    game   = lua.Pop<Game*>();

  game->ObtainEquipment(id, amount);

  return 0;
}

LUA_IMPL(GetNumEnemiesAlive) {
  lua::Lua lua(L);
  Game*    game = lua.Pop<Game*>();

  uint32_t ret = game->GetNumEnemiesAlive();

  lua_pushnumber(L, ret);
  return 1;
}

LUA_IMPL(GetNumOwnsAlive) {
  lua::Lua lua(L);
  Game*    game = lua.Pop<Game*>();

  uint32_t ret = game->GetNumOwnsAlive();

  lua_pushnumber(L, ret);
  return 1;
}

LUA_IMPL(GetNumCommandersAlive) {
  lua::Lua lua(L);
  Game*    game = lua.Pop<Game*>();

  uint32_t ret = game->GetNumCommandersAlive();

  lua_pushnumber(L, ret);
  return 1;
}

LUA_IMPL(GetTurnCurrent) {
  lua::Lua lua(L);
  Game* game = lua.Pop<Game*>();
  lua_pushnumber(L, game->GetTurnCurrent());
  return 1;
}

LUA_IMPL(HasUnit) {
  lua::Lua lua(L);
  string id = lua.Pop<string>();
  Game* game = lua.Pop<Game*>();
  lua_pushboolean(L, game->HasUnit(id));
  return 1;
}

LUA_IMPL(GetNumUnitsAlive) {
  lua::Lua lua(L);
  string id = lua.Pop<string>();
  Game* game = lua.Pop<Game*>();
  lua_pushnumber(L, game->GetNumUnitsAlive(id));
  return 1;
}

LUA_IMPL(AreUnitsWithin) {
  lua::Lua lua(L);
  uint16_t radius = lua.Pop<uint16_t>();
  string second_id = lua.Pop<string>();
  string first_id = lua.Pop<string>();
  Game* game = lua.Pop<Game*>();
  lua_pushboolean(L, game->AreUnitsWithin(first_id, second_id, radius));
  return 1;
}

LUA_IMPL(IsCellVacant) {
  lua::Lua lua(L);
  Vec2D position = GetVec2DFromLua(&lua);
  Game* game = lua.Pop<Game*>();
  lua_pushboolean(L, game->IsCellVacant(position));
  return 1;
}

LUA_IMPL(IsForceWithin) {
  lua::Lua lua(L);
  uint16_t radius = lua.Pop<uint16_t>();
  Vec2D center = GetVec2DFromLua(&lua);
  Force force = (Force)lua.Pop<int>();
  Game* game = lua.Pop<Game*>();
  lua_pushboolean(L, game->IsForceWithin(force, center, radius));
  return 1;
}

LUA_IMPL(IsUnitWithin) {
  lua::Lua lua(L);
  uint16_t radius = lua.Pop<uint16_t>();
  Vec2D center = GetVec2DFromLua(&lua);
  string id = lua.Pop<string>();
  Game* game = lua.Pop<Game*>();
  lua_pushboolean(L, game->IsUnitWithin(id, center, radius));
  return 1;
}

LUA_IMPL(PushCmdMove) {
  lua::Lua lua(L);
  Vec2D    pos     = GetVec2DFromLua(&lua);
  int      unit_id = lua.Pop<int>();
  Game*    game    = lua.Pop<Game*>();

  Unit* unit = game->GetUnit(unit_id);
  game->Push(unique_ptr<CmdMove>(new CmdMove(unit, pos)));

  return 0;
}

LUA_IMPL(PushCmdSpeak) {
  lua::Lua lua(L);
  string   words   = lua.Pop<string>();
  int      unit_id = lua.Pop<int>();
  Game*    game    = lua.Pop<Game*>();

  Unit* unit = game->GetUnit(unit_id);
  game->Push(unique_ptr<CmdSpeak>(new CmdSpeak(unit, words)));

  return 0;
}

#undef LUA_IMPL
