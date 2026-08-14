#include "game.h"

#include <cstdlib>

#include "assets.h"
#include "cmd.h"
#include "commander.h"
#include "core/path_tree.h"
#include "deployer.h"
#include "event_effect.h"
#include "formulae.h"
#include "magic.h"
#include "stage_unit_manager.h"
#include "user_interface.h"
#include "util/game_env.h"
#include "util/path.h"

// XXX temporary include
#include "lua_api.h"

namespace mengde {
namespace core {

Game::Game(const ResourceManagers& rc, Assets* assets, const Path& stage_script_path)
    : rc_(rc),
      assets_(assets),  // FIXME Change this to clone the object as we need to rollback assets for some cases
      lua_(nullptr),
      lua_this_(this, "Game"),
      user_interface_(new UserInterface(this)),
      commander_(nullptr),
      deployer_(nullptr),
      map_(nullptr),
      stage_unit_manager_(nullptr),
      turn_(),
      status_(Status::kDeploying) {
  lua_ = CreateLua(stage_script_path);
  turn_.SetLimit(lua_->Get<uint16_t>("gstage.turn_limit"));
  map_ = CreateMap();
  lua_->Call<void>(string("on_deploy"), lua_this_);
  deployer_ = CreateDeployer();

  commander_          = new Commander();
  stage_unit_manager_ = new StageUnitManager();
}

Game::~Game() {
  // NOTE rc_ and assets_ are not deleted here
  delete lua_;
  delete commander_;
  delete deployer_;
  delete map_;
  delete stage_unit_manager_;
}

lua::Lua* Game::CreateLua(const Path& stage_script_path) {
  lua::Lua* lua = new lua::Lua();

#define GAME_PREFIX "Game_"

  // Register API functions
  {
#define MACRO_LUA_GAME(cname, luaname) lua->Register(GAME_PREFIX #luaname, Game_##cname);
#include "lua_api_game.h.inc"
#undef MACRO_LUA_GAME
  }

  // Register OO-style pseudo class for Lua
  {
    lua->RegisterClass(lua_this_.name());

#define MACRO_LUA_GAME(cname, luaname) lua->RegisterMethod(lua_this_.name(), string(#luaname));
#include "lua_api_game.h.inc"
#undef MACRO_LUA_GAME
  }

#undef GAME_PREFIX

  // Register enum values
  {
#define ENUM_PREFIX "Enum."
    lua->Set(ENUM_PREFIX "force.own", (int)Force::kOwn);
    lua->Set(ENUM_PREFIX "force.ally", (int)Force::kAlly);
    lua->Set(ENUM_PREFIX "force.enemy", (int)Force::kEnemy);
    lua->Set(ENUM_PREFIX "status.undecided", (int)Status::kUndecided);
    lua->Set(ENUM_PREFIX "status.defeat", (int)Status::kDefeat);
    lua->Set(ENUM_PREFIX "status.victory", (int)Status::kVictory);
#undef GAME_PREFIX
  }

  // Run the main script
  lua->RunFile(stage_script_path.ToString());
  return lua;
}

Map* Game::CreateMap() {
  ASSERT(lua_ != nullptr);

  vector<uint32_t> size    = lua_->GetVector<uint32_t>("gstage.map.size");
  uint32_t         cols    = size[0];
  uint32_t         rows    = size[1];
  vector<string>   terrain = lua_->GetVector<string>("gstage.map.terrain");
  string           file    = lua_->Get<string>("gstage.map.file");  // FIXME filename should be same as stage id + .bmp
  ASSERT(rows == terrain.size());
  for (auto e : terrain) {
    ASSERT(cols == e.size());
  }
  Map* map = new Map(terrain, file, rc_.terrain_manager);
  const string blendable = "fgFwm";
  if (lua_->GetOpt<bool>("gstage.map.has_terrain_layers")) {
  lua_->ForEachTableEntry("gstage.map.terrain_layers", [map, this, blendable](lua::Lua* l, const string&) {
    const vector<int> position = l->Get<vector<int>>("position");
    const string primary_id = l->Get<string>("primary_terrain");
    const string secondary_id = l->GetOpt<string>("secondary_terrain");
    const int coverage = l->GetOpt<int>("coverage");
    ASSERT(position.size() == 2);
    ASSERT(primary_id.size() == 1);
    ASSERT(blendable.find(primary_id[0]) != string::npos);
    ASSERT(coverage >= 0 && coverage <= 255);
    Terrain* primary = rc_.terrain_manager->Get(primary_id);
    Terrain* secondary = nullptr;
    if (!secondary_id.empty() && secondary_id != "nil") {
      ASSERT(secondary_id.size() == 1);
      ASSERT(blendable.find(secondary_id[0]) != string::npos);
      ASSERT(secondary_id != primary_id);
      ASSERT(coverage > 0);
      secondary = rc_.terrain_manager->Get(secondary_id);
    } else {
      ASSERT(coverage == 0);
    }
    ASSERT(primary != nullptr);
    ASSERT(map->GetTerrain({position[0], position[1]}) == primary);
    map->SetTerrainBlend({position[0], position[1]}, primary, secondary,
                         static_cast<uint8_t>(coverage));
  });
  }
  lua_->ForEachTableEntry("gstage.map.blocked_edges", [map](lua::Lua* l, const string&) {
    vector<int> from = l->Get<vector<int>>("from");
    vector<int> to   = l->Get<vector<int>>("to");
    ASSERT(from.size() == 2 && to.size() == 2);
    map->BlockEdge({from[0], from[1]}, {to[0], to[1]});
  });
  return map;
}

Deployer* Game::CreateDeployer() {
  ASSERT(lua_ != nullptr);

  vector<DeployInfoUnselectable> unselectable_info_list;
  lua_->ForEachTableEntry("gstage.deploy.unselectables", [=, &unselectable_info_list](lua::Lua* l, const string&) {
    vector<int> pos_vec = l->Get<vector<int>>("position");
    string      hero_id = l->Get<string>("hero");
    Vec2D       position(pos_vec[0], pos_vec[1]);
    Hero*       hero = assets_->GetHero(hero_id);  // TODO Check if Hero exists in our assets
    unselectable_info_list.push_back({position, hero});
  });
  uint32_t                     num_required = lua_->Get<uint32_t>("gstage.deploy.num_required_selectables");
  vector<DeployInfoSelectable> selectable_info_list;
  lua_->ForEachTableEntry("gstage.deploy.selectables", [=, &selectable_info_list](lua::Lua* l, const string&) mutable {
    vector<int> pos_vec = l->Get<vector<int>>("position");
    Vec2D       position(pos_vec[0], pos_vec[1]);
    selectable_info_list.push_back({position});
  });
  return new Deployer(unselectable_info_list, selectable_info_list, num_required);
}

void Game::ForEachUnit(std::function<void(Unit*)> fn) { stage_unit_manager_->ForEach(fn); }

void Game::ForEachUnitIdxConst(std::function<void(uint32_t idx, const Unit*)> fn) const {
  stage_unit_manager_->ForEachIdxConst(fn);
}

void Game::MoveUnit(Unit* unit, Vec2D dst) {
  Vec2D src = unit->GetPosition();
  if (src == dst) return;
  map_->MoveUnit(src, dst);
  unit->SetPosition(dst);
}

void Game::KillUnit(Unit* unit) {
  const Vec2D position = unit->GetPosition();
  map_->RemoveUnit(position);
  stage_unit_manager_->Kill(unit);
  BattleEvent event;
  event.type = BattleEventType::kDeath;
  event.target = unit->GetId();
  event.from_x = position.x;
  event.from_y = position.y;
  EmitBattleEvent(std::move(event));
}

bool Game::TryBasicAttack(Unit* unit_atk, Unit* unit_def) {
  return GenRandom(100) < Formulae::ComputeBasicAttackAccuracy(unit_atk, unit_def);
}

bool Game::TryMagic(Unit* unit_atk, Unit* unit_def) {
  return GenRandom(100) < Formulae::ComputeMagicAccuracy(unit_atk, unit_def);
}

bool Game::IsValidCoords(Vec2D c) { return map_->IsValidCoords(c); }

Magic* Game::GetMagic(const std::string& id) { return rc_.magic_manager->Get(id); }

Unit* Game::GetUnit(uint32_t id) { return stage_unit_manager_->Get(id); }

Equipment* Game::GetEquipment(const std::string& id) { return rc_.equipment_manager->Get(id); }

Force Game::GetCurrentForce() const { return turn_.GetForce(); }

bool Game::EndForceTurn() {
  ForEachUnit([this](Unit* u) {
    if (this->IsCurrentTurn(u)) {
      u->ResetAction();
    }
  });

  bool next_turn = turn_.Next();

  ForEachUnit([this](Unit* u) {
    if (this->IsCurrentTurn(u)) {
      commander_->Push(u->RaiseEvent(event::GeneralEvent::kTurnBegin));
    }
  });

  if (next_turn) {
    // TODO do stuff when next turn begins (when actually the turn number increased)
  }

  return IsUserTurn();
}

bool Game::IsUserTurn() const { return turn_.GetForce() == Force::kOwn; }

bool Game::IsAITurn() const { return !IsUserTurn(); }

bool Game::IsCurrentTurn(Unit* unit) const { return unit->GetForce() == turn_.GetForce(); }

uint16_t Game::GetTurnCurrent() const { return turn_.GetCurrent(); }

bool Game::HasUnit(const std::string& id) const {
  bool found = false;
  ForEachUnitIdxConst([&](uint32_t, const Unit* unit) {
    if (!unit->IsDead() && unit->GetId() == id) found = true;
  });
  return found;
}

uint32_t Game::GetNumUnitsAlive(const std::string& id) const {
  uint32_t count = 0;
  ForEachUnitIdxConst([&](uint32_t, const Unit* unit) {
    if (!unit->IsDead() && unit->GetId() == id) ++count;
  });
  return count;
}

bool Game::AreUnitsWithin(const std::string& first_id, const std::string& second_id,
                          uint16_t radius) const {
  vector<Vec2D> first_positions;
  vector<Vec2D> second_positions;
  ForEachUnitIdxConst([&](uint32_t, const Unit* unit) {
    if (unit->IsDead()) return;
    if (unit->GetId() == first_id) first_positions.push_back(unit->GetPosition());
    if (unit->GetId() == second_id) second_positions.push_back(unit->GetPosition());
  });
  for (const Vec2D& first : first_positions) {
    for (const Vec2D& second : second_positions) {
      const int distance = std::abs(first.x - second.x) + std::abs(first.y - second.y);
      if (distance <= radius) return true;
    }
  }
  return false;
}

bool Game::IsCellVacant(Vec2D position) const { return !UnitInCell(position); }

bool Game::IsForceWithin(Force force, Vec2D center, uint16_t radius) const {
  bool found = false;
  ForEachUnitIdxConst([&](uint32_t, const Unit* unit) {
    if (found || unit->IsDead() || unit->GetForce() != force) return;
    const Vec2D pos = unit->GetPosition();
    const int distance = std::abs(pos.x - center.x) + std::abs(pos.y - center.y);
    if (distance <= radius) found = true;
  });
  return found;
}

bool Game::IsUnitWithin(const std::string& id, Vec2D center, uint16_t radius) const {
  bool found = false;
  ForEachUnitIdxConst([&](uint32_t, const Unit* unit) {
    if (found || unit->IsDead() || unit->GetId() != id) return;
    const Vec2D pos = unit->GetPosition();
    const int distance = std::abs(pos.x - center.x) + std::abs(pos.y - center.y);
    if (distance <= radius) found = true;
  });
  return found;
}

void Game::RunScriptUpdate() {
  lua_->Call<void>(string("on_update"), lua_this_);
  BattleEvent event;
  event.type = BattleEventType::kScriptTriggered;
  event.detail = "on_update";
  EmitBattleEvent(std::move(event));
}

uint16_t Game::GetTurnLimit() const { return turn_.GetLimit(); }

vector<Unit*> Game::GetCurrentTurnUnits() {
  vector<Unit*> units;
  ForEachUnit([this, &units](Unit* u) {
    if (this->IsCurrentTurn(u)) {
      units.push_back(u);
    }
  });
  return units;
}

vector<Vec2D> Game::FindMovablePos(Unit* unit) {
  unique_ptr<PathTree> path_tree(FindMovablePath(unit));
  return path_tree->GetNodeList();
}

PathTree* Game::FindMovablePath(Unit* unit) { return map_->FindMovablePath(unit); }

Unit* Game::GetOneHostileInRange(Unit* unit, Vec2D virtual_pos) {
  Vec2D original_pos = unit->GetPosition();
  MoveUnit(unit, virtual_pos);
  Unit* target = nullptr;
  stage_unit_manager_->ForEach([unit, &target](Unit* candidate) {
    if (unit->IsHostile(candidate)) {
      if (unit->IsInRange(candidate->GetPosition())) {
        target = candidate;
      }
    }
  });
  MoveUnit(unit, original_pos);
  return target;
}

bool Game::HasNext() const { return commander_->HasNext(); }

const Cmd* Game::GetNextCmdConst() const {
  ASSERT(HasNext());
  return commander_->GetNextCmdConst();
}

bool Game::UnitInCell(Vec2D c) const { return map_->UnitInCell(c); }

Unit* Game::GetUnitInCell(Vec2D c) const {
  if (!map_->UnitInCell(c)) return nullptr;
  return map_->GetUnit(c);
}

void Game::DoNext() {
  ASSERT(HasNext());
#ifdef DEBUG
  commander_->DebugPrint();
#endif
  commander_->DoNext(this);
}

void Game::Push(unique_ptr<Cmd> cmd) {
  ///  if (cmd == nullptr) return;
  commander_->Push(std::move(cmd));
}

void Game::EmitBattleEvent(BattleEvent event) noexcept {
  event.turn = GetTurnCurrent();
  battle_event_queue_.Emit(std::move(event));
}

bool Game::CheckStatus() {
  if (status_ != Status::kUndecided) return false;
  uint32_t res = lua_->Call<uint32_t>("end_condition", lua_this_);
  status_      = static_cast<Status>(res);
  return (status_ != Status::kUndecided);
}

uint32_t Game::GetNumEnemiesAlive() {
  uint32_t count = 0;
  ForEachUnit([=, &count](Unit* u) {
    if (!u->IsDead() && u->GetForce() == Force::kEnemy) {
      count++;
    }
  });
  return count;
}

uint32_t Game::GetNumOwnsAlive() {
  uint32_t count = 0;
  ForEachUnit([=, &count](Unit* u) {
    if (!u->IsDead() && u->GetForce() == Force::kOwn) {
      count++;
    }
  });
  return count;
}

uint32_t Game::GetNumCommandersAlive() {
  const vector<string> commander_ids = lua_->GetVector<string>("gcommanders");
  uint32_t count = 0;
  ForEachUnit([&](Unit* unit) {
    if (unit->IsDead() || unit->GetForce() != Force::kOwn) return;
    for (const string& id : commander_ids) {
      if (unit->GetId() == id) {
        ++count;
        break;
      }
    }
  });
  return count;
}

void Game::AppointHero(const string& id, uint16_t level) {
  LOG_INFO("Hero added to asset '%s' with Lv %d", id.c_str(), level);
  Hero* hero = new Hero(rc_.hero_tpl_manager->Get(id), level);
  assets_->AddHero(hero);
}

uint32_t Game::GenerateOwnUnit(const string& id, Vec2D pos) {
  const Hero* hero = assets_->GetHero(id);
  return GenerateOwnUnit(hero, pos);
}

uint32_t Game::GenerateOwnUnit(const Hero* hero, Vec2D pos) {
  Unit* unit = new Unit(hero, Force::kOwn);
  map_->PlaceUnit(unit, pos);
  return stage_unit_manager_->Deploy(unit);
}

uint32_t Game::GenerateUnit(const string& id, uint16_t level, Force force, Vec2D pos) {
  HeroTemplate* hero_tpl = rc_.hero_tpl_manager->Get(id);
  Hero*         hero     = new Hero(hero_tpl, level);
  Unit*         unit     = new Unit(hero, force);
  map_->PlaceUnit(unit, pos);
  return stage_unit_manager_->Deploy(unit);
}

void Game::ObtainEquipment(const string& id, uint32_t amount) {
  Equipment* eq = rc_.equipment_manager->Get(id);
  assets_->AddEquipment(eq, amount);
}

bool Game::SubmitDeploy() {
  ASSERT(status_ == Status::kDeploying);
  if (status_ != Status::kDeploying) return true;

  if (!deployer_->IsReady()) return false;

  deployer_->ForEach([=](const DeployElement& e) { this->GenerateOwnUnit(e.hero, deployer_->GetPosition(e.hero)); });

  status_ = Status::kUndecided;
  lua_->Call<void>(string("on_begin"), lua_this_);
  return true;
}

uint32_t Game::AssignDeploy(const Hero* hero) { return deployer_->Assign(hero); }

uint32_t Game::UnassignDeploy(const Hero* hero) { return deployer_->Unassign(hero); }

uint32_t Game::FindDeploy(const Hero* hero) { return deployer_->Find(hero); }

}  // namespace core
}  // namespace mengde
