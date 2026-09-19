#include "rl_environment.h"

#include <algorithm>
#include <limits>
#include <stdexcept>

#include "attack_range.h"
#include "cmd.h"
#include "game.h"
#include "magic.h"
#include "map.h"
#include "stat.h"
#include "unit.h"

namespace mengde {
namespace core {

namespace {

float Clamp01(float value) { return std::max(0.0f, std::min(1.0f, value)); }

float Ratio(int value, int maximum) {
  if (maximum <= 0) return 0.0f;
  return Clamp01(static_cast<float>(value) / static_cast<float>(maximum));
}

}  // namespace

RLEnvironment::RLEnvironment(Game* game, uint32_t max_units, uint32_t max_agent_actions, bool auto_opponents)
    : game_(game),
      max_units_(max_units),
      max_agent_actions_(max_agent_actions),
      agent_actions_(0),
      truncated_(false),
      auto_opponents_(auto_opponents),
      legal_actions_() {
  if (game_ == nullptr) throw std::invalid_argument("RLEnvironment requires a Game");
  LoadSupplies();
  DrainCommands();
  AdvanceFinishedForces();
  if (auto_opponents_) PlayOpponentTurns();
  RebuildLegalActions();
}

std::vector<float> RLEnvironment::Observe() const {
  std::vector<float> result;
  result.reserve(GetObservationSize());

  const Vec2D map_size = game_->GetMapSize();
  result.push_back(Ratio(game_->GetTurnCurrent(), std::max<uint16_t>(1, game_->GetTurnLimit())));
  result.push_back(Ratio(static_cast<int>(game_->GetCurrentForce()), static_cast<int>(Force::kEnemy)));
  result.push_back(Ratio(map_size.x, 64));
  result.push_back(Ratio(map_size.y, 64));

  uint32_t count = 0;
  game_->ForEachUnitIdxConst([&](uint32_t, const Unit* unit) {
    if (count >= max_units_) return;
    const Force force = unit->GetForce();
    const Vec2D pos   = unit->GetPosition();
    const HpMp& hpmp  = unit->GetCurrentHpMp();
    const HpMp& max   = unit->GetOriginalHpMp();
    const Attribute& attr = unit->GetCurrentAttr();

    result.push_back(1.0f);
    result.push_back(force == Force::kOwn ? 1.0f : 0.0f);
    result.push_back(force == Force::kAlly ? 1.0f : 0.0f);
    result.push_back(force == Force::kEnemy ? 1.0f : 0.0f);
    result.push_back(unit->IsDead() ? 0.0f : 1.0f);
    result.push_back(unit->IsDoneAction() ? 1.0f : 0.0f);
    result.push_back(Ratio(pos.x, std::max(1, map_size.x - 1)));
    result.push_back(Ratio(pos.y, std::max(1, map_size.y - 1)));
    result.push_back(Ratio(hpmp.hp, max.hp));
    result.push_back(Ratio(hpmp.mp, max.mp));
    result.push_back(Ratio(attr.atk, 500));
    result.push_back(Ratio(attr.def, 500));
    result.push_back(Ratio(attr.dex, 500));
    result.push_back(Ratio(attr.itl, 500));
    result.push_back(Ratio(attr.mor, 500));
    result.push_back(Ratio(unit->GetMove(), 20));
    ++count;
  });

  result.resize(GetObservationSize(), 0.0f);
  return result;
}

const std::vector<RLEnvironment::Action>& RLEnvironment::GetLegalActions() {
  RebuildLegalActions();
  return legal_actions_;
}

void RLEnvironment::RebuildLegalActions() {
  legal_actions_.clear();
  if (IsDone()) return;
  const Force active_force = game_->GetCurrentForce();
  const bool hold_position = active_force == Force::kAlly &&
                             game_->GetLuaScript()->GetOpt<bool>("gally_hold_position");
  const uint16_t own_hold_until =
      game_->GetLuaScript()->GetOpt<uint16_t>("gown_hold_until_turn");
  const bool forced_wait = active_force == Force::kOwn && own_hold_until > 0 &&
                           game_->GetTurnCurrent() < own_hold_until;

  game_->ForEachUnitIdxConst([&](uint32_t unit_id, const Unit* const_unit) {
    Unit* unit = game_->GetUnit(unit_id);
    if (const_unit->IsDead() || const_unit->IsDoneAction() || const_unit->GetForce() != active_force) return;

    const Vec2D original = unit->GetPosition();
    legal_actions_.push_back({unit_id, ActionType::kWait, original, kNoTarget, ""});
    if (forced_wait) return;

    const std::vector<Vec2D> moves = hold_position ? std::vector<Vec2D>{original}
                                                   : game_->FindMovablePos(unit);
    for (const Vec2D& destination : moves) {
      if (destination != original && game_->UnitInCell(destination)) continue;
      if (destination != original) {
        legal_actions_.push_back({unit_id, ActionType::kMove, destination, kNoTarget, ""});
      }

      unit->GetAttackRange().ForEach(
          [&](Vec2D target_pos) {
            if (!game_->IsValidCoords(target_pos)) return;
            Unit* target = game_->GetUnitInCell(target_pos);
            if (target == nullptr || target->IsDead() || !unit->IsHostile(target)) return;

            game_->ForEachUnitIdxConst([&](uint32_t target_id, const Unit* candidate) {
              if (candidate == target) {
                legal_actions_.push_back({unit_id, ActionType::kBasicAttack, destination, target_id, ""});
              }
            });
          },
          destination);

      game_->GetMagicManager()->ForEach([&](Magic* magic) {
        if (!magic->IsAvailible(unit) || unit->GetCurrentHpMp().mp < magic->GetMpCost()) return;
        magic->GetRange().ForEach(
            [&](Vec2D target_pos) {
              if (!game_->IsValidCoords(target_pos)) return;
              Unit* target = game_->GetUnitInCell(target_pos);
              if (target == nullptr || target->IsDead()) return;
              const bool valid_target = magic->GetIsTargetEnemy() ? unit->IsHostile(target) : !unit->IsHostile(target);
              if (!valid_target) return;
              game_->ForEachUnitIdxConst([&](uint32_t target_id, const Unit* candidate) {
                if (candidate == target) {
                  legal_actions_.push_back({unit_id, ActionType::kMagic, destination, target_id, magic->GetId()});
                }
              });
            }, destination);
      });
    }
  });
}

RLEnvironment::StepResult RLEnvironment::Step(uint32_t action_index) {
  RebuildLegalActions();
  if (IsDone()) throw std::logic_error("step called after episode end");
  if (action_index >= legal_actions_.size()) throw std::out_of_range("illegal RL action index");

  const uint32_t own_before    = game_->GetNumOwnsAlive();
  const uint32_t enemy_before  = game_->GetNumEnemiesAlive();
  const float own_hp_before    = UnitHealthTotal(Force::kOwn);
  const float enemy_hp_before  = UnitHealthTotal(Force::kEnemy);
  const Action action          = legal_actions_[action_index];
  Unit* unit                  = game_->GetUnit(action.unit_id);

  CmdAction* command = new CmdAction();
  command->SetCmdMove(unique_ptr<CmdMove>(new CmdMove(unit, action.destination)));
  if (action.type == ActionType::kBasicAttack) {
    Unit* target = game_->GetUnit(action.target_id);
    command->SetCmdAct(unique_ptr<CmdBasicAttack>(
        new CmdBasicAttack(unit, target, CmdBasicAttack::Type::kActive)));
  } else if (action.type == ActionType::kMagic) {
    Unit* target = game_->GetUnit(action.target_id);
    command->SetCmdAct(unique_ptr<CmdMagic>(new CmdMagic(unit, target, game_->GetMagic(action.skill_id))));
  } else {
    command->SetCmdAct(unique_ptr<CmdStay>(new CmdStay(unit)));
  }
  game_->Push(unique_ptr<CmdAction>(command));
  DrainCommands();
  CheckSiteEntry(unit);
  game_->RunScriptUpdate();
  DrainCommands();
  ++agent_actions_;

  AdvanceFinishedForces();
  if (auto_opponents_) PlayOpponentTurns();
  game_->RunScriptUpdate();
  DrainCommands();

  const uint32_t own_after   = game_->GetNumOwnsAlive();
  const uint32_t enemy_after = game_->GetNumEnemiesAlive();
  float reward = -0.01f;
  reward += 2.0f * static_cast<float>(enemy_before - enemy_after);
  reward -= 2.0f * static_cast<float>(own_before - own_after);

  // Small dense feedback keeps long Cao Cao maps trainable without changing
  // the paper's dominant kill/death and terminal rewards.
  reward += 0.5f * ((enemy_hp_before - UnitHealthTotal(Force::kEnemy)) -
                    (own_hp_before - UnitHealthTotal(Force::kOwn)));

  if (game_->GetStatus() == Game::Status::kVictory) reward += 10.0f;
  if (game_->GetStatus() == Game::Status::kDefeat) reward -= 10.0f;
  if (!IsDone() && agent_actions_ >= max_agent_actions_) {
    truncated_ = true;
    reward -= 1.0f;
  }

  RebuildLegalActions();
  return {Observe(), reward, game_->GetStatus() == Game::Status::kVictory ||
                                game_->GetStatus() == Game::Status::kDefeat,
          truncated_};
}

bool RLEnvironment::IsDone() const {
  return truncated_ || game_->GetStatus() == Game::Status::kVictory || game_->GetStatus() == Game::Status::kDefeat;
}

void RLEnvironment::DrainCommands() {
  while (game_->HasNext()) game_->DoNext();
}

void RLEnvironment::AdvanceFinishedForces() {
  for (int skipped = 0; skipped < 3 && !IsDone(); ++skipped) {
    const Force active_force = game_->GetCurrentForce();
    bool has_ready_unit = false;
    game_->ForEachUnit([&](Unit* unit) {
      if (!unit->IsDead() && !unit->IsDoneAction() && unit->GetForce() == active_force) has_ready_unit = true;
    });
    if (has_ready_unit) return;
    const Force previous_force = game_->GetCurrentForce();
    game_->Push(unique_ptr<CmdEndTurn>(new CmdEndTurn()));
    DrainCommands();
    if (game_->GetCurrentForce() != previous_force) ApplySiteRecovery(game_->GetCurrentForce());
  }
}

void RLEnvironment::PlayOpponentTurns() {
  while (!IsDone() && game_->GetCurrentForce() != Force::kOwn) {
    const Force previous_force = game_->GetCurrentForce();
    game_->Push(unique_ptr<CmdPlayAI>(new CmdPlayAI()));
    DrainCommands();
    if (game_->GetCurrentForce() != previous_force) ApplySiteRecovery(game_->GetCurrentForce());
  }
}

Force RLEnvironment::GetCurrentForce() const { return game_->GetCurrentForce(); }

int RLEnvironment::GetGameStatus() const { return static_cast<int>(game_->GetStatus()); }

Vec2D RLEnvironment::GetMapSize() const { return game_->GetMapSize(); }

std::string RLEnvironment::GetTerrainName(Vec2D position) const {
  return game_->GetMap()->GetTerrain(position)->GetName();
}

std::vector<Vec2D> RLEnvironment::GetMovementPath(uint32_t unit_id, Vec2D destination) const {
  Unit* unit = game_->GetUnit(unit_id);
  std::vector<Vec2D> path = game_->GetMap()->FindPathTo(unit, destination);
  std::reverse(path.begin(), path.end());
  return path;
}

std::vector<Vec2D> RLEnvironment::GetMovementRange(uint32_t unit_id) const {
  return game_->FindMovablePos(game_->GetUnit(unit_id));
}

void RLEnvironment::LoadSupplies() {
  lua::Lua* script = game_->GetLuaScript();
  if (!script->GetOpt<bool>("gsupply_enabled")) return;

  script->ForEachTableEntry("gitems", [&](lua::Lua* entry, const std::string&) {
    ItemInfo item;
    item.id = entry->Get<std::string>("id");
    item.name = entry->Get<std::string>("name");
    item.hp = entry->GetOpt<int>("hp");
    item.mp = entry->GetOpt<int>("mp");
    item.price = entry->GetOpt<uint32_t>("price");
    item.count = entry->GetOpt<uint32_t>("initial");
    items_[item.id] = item;
  });

  script->ForEachTableEntry("gsites", [&](lua::Lua* entry, const std::string&) {
    SiteInfo site;
    site.id = entry->Get<std::string>("id");
    site.name = entry->Get<std::string>("name");
    const std::vector<int> position = entry->Get<std::vector<int>>("position");
    site.position = {position[0], position[1]};
    site.restore_hp = entry->GetOpt<int>("restore_hp");
    site.restore_mp = entry->GetOpt<int>("restore_mp");
    entry->ForEachTableEntry("rewards", [&](lua::Lua* reward, const std::string&) {
      site.rewards.push_back({reward->Get<std::string>("item"), reward->Get<uint32_t>("amount")});
    });
    sites_.push_back(site);
  });
}

std::vector<RLEnvironment::ItemInfo> RLEnvironment::GetItems() const {
  std::vector<ItemInfo> result;
  for (const auto& item : items_) result.push_back(item.second);
  return result;
}

std::map<std::string, uint32_t> RLEnvironment::GetInventoryCounts() const {
  std::map<std::string, uint32_t> result;
  for (const auto& item : items_) result[item.first] = item.second.count;
  return result;
}

void RLEnvironment::SetInventoryCounts(const std::map<std::string, uint32_t>& counts) {
  for (const auto& count : counts) {
    auto item = items_.find(count.first);
    if (item != items_.end()) item->second.count = count.second;
  }
}
void RLEnvironment::PurchaseItem(const std::string& item_id, uint32_t* money) {
  if (money == nullptr) throw std::invalid_argument("money balance is missing");
  auto item = items_.find(item_id);
  if (item == items_.end() || item->second.price == 0) {
    throw std::out_of_range("item is not sold here");
  }
  if (*money < item->second.price) throw std::logic_error("not enough money");
  *money -= item->second.price;
  ++item->second.count;
}


std::vector<std::string> RLEnvironment::TakeNotices() {
  std::vector<std::string> result;
  result.swap(notices_);
  return result;
}

void RLEnvironment::CheckSiteEntry(Unit* unit) {
  if (unit == nullptr || unit->IsDead() || unit->GetForce() != Force::kOwn) return;
  for (const SiteInfo& site : sites_) {
    if (unit->GetPosition() != site.position || visited_sites_.count(site.id) != 0) continue;
    visited_sites_.insert(site.id);
    std::string reward_text;
    for (const auto& reward : site.rewards) {
      auto item = items_.find(reward.first);
      if (item == items_.end()) continue;
      item->second.count += reward.second;
      if (!reward_text.empty()) reward_text += u8"\u3001";
      reward_text += item->second.name + u8"\u00d7" + std::to_string(reward.second);
    }
    notices_.push_back(unit->GetId() + u8"\u8fdb\u5165" + site.name +
                       (reward_text.empty() ? "" : u8"\uff0c\u83b7\u5f97" + reward_text));
  }
}

void RLEnvironment::ApplySiteRecovery(Force force) {
  game_->ForEachUnit([&](Unit* unit) {
    if (unit->IsDead() || unit->GetForce() != force) return;
    for (const SiteInfo& site : sites_) {
      if (unit->GetPosition() != site.position) continue;
      const HpMp before = unit->GetCurrentHpMp();
      unit->RestoreHP(unit->GetOriginalHpMp().hp * site.restore_hp / 100);
      unit->RestoreMP(unit->GetOriginalHpMp().mp * site.restore_mp / 100);
      const HpMp after = unit->GetCurrentHpMp();
      if (after.hp != before.hp || after.mp != before.mp) {
        notices_.push_back(unit->GetId() + u8"\u5728" + site.name + u8"\u6062\u590d HP " +
                           std::to_string(after.hp - before.hp) + " / MP " +
                           std::to_string(after.mp - before.mp));
      }
    }
  });
}

RLEnvironment::StepResult RLEnvironment::UseItem(uint32_t unit_id, const std::string& item_id) {
  RebuildLegalActions();
  if (IsDone()) throw std::logic_error("item used after episode end");
  auto item = items_.find(item_id);
  if (item == items_.end() || item->second.count == 0) throw std::out_of_range("item is unavailable");
  Unit* unit = game_->GetUnit(unit_id);
  if (unit == nullptr || unit->IsDead() || unit->GetForce() != Force::kOwn || unit->IsDoneAction() ||
      game_->GetCurrentForce() != Force::kOwn) {
    throw std::logic_error("unit cannot use an item now");
  }
  const HpMp before = unit->GetCurrentHpMp();
  unit->RestoreHP(item->second.hp);
  unit->RestoreMP(item->second.mp);
  const HpMp after = unit->GetCurrentHpMp();
  if (after.hp == before.hp && after.mp == before.mp) throw std::logic_error("item would have no effect");
  --item->second.count;
  unit->EndAction();
  game_->RunScriptUpdate();
  DrainCommands();
  ++agent_actions_;
  notices_.push_back(unit->GetId() + u8"\u4f7f\u7528" + item->second.name);
  AdvanceFinishedForces();
  if (auto_opponents_) PlayOpponentTurns();
  game_->RunScriptUpdate();
  DrainCommands();
  RebuildLegalActions();
  return {Observe(), 0.0f, game_->GetStatus() == Game::Status::kVictory ||
                                    game_->GetStatus() == Game::Status::kDefeat,
          truncated_};
}

void RLEnvironment::BeginRestore(uint16_t turn, Force force, uint32_t agent_actions, bool truncated) {
  game_->ForEachUnit([&](Unit* unit) {
    if (game_->GetMap()->UnitInCell(unit->GetPosition()) &&
        game_->GetMap()->GetUnit(unit->GetPosition()) == unit) {
      game_->GetMap()->EmptyCell(unit->GetPosition());
    }
  });
  game_->RestoreTurn(turn, force);
  // In-process search may restore after a speculative branch reached victory
  // or defeat. Match a clean process restore by reopening the battle before
  // legal actions are rebuilt.
  game_->RestoreStatus(Game::Status::kUndecided);
  agent_actions_ = agent_actions;
  truncated_     = truncated;
  visited_sites_.clear();
  notices_.clear();
  for (auto& item : items_) item.second.count = 0;
  legal_actions_.clear();
}

void RLEnvironment::RestoreUnit(uint32_t unit_id, uint16_t level, uint16_t exp, int hp, int mp,
                                Vec2D position, int direction, bool done_action) {
  if (!game_->IsValidCoords(position)) throw std::out_of_range("saved unit position is invalid");
  if (direction < static_cast<int>(kDirNone) || direction > static_cast<int>(kDirDown)) {
    throw std::out_of_range("saved unit direction is invalid");
  }
  Unit* unit = game_->GetUnit(unit_id);
  if (unit == nullptr) throw std::out_of_range("saved unit id is invalid");
  unit->SetPosition(position);
  unit->RestoreState(level, exp, HpMp(hp, mp), static_cast<Direction>(direction), done_action);
  if (!unit->IsDead()) {
    if (game_->GetMap()->UnitInCell(position)) throw std::logic_error("saved units overlap");
    game_->GetMap()->PlaceUnit(unit, position);
  }
}

uint32_t RLEnvironment::RestoreSpawnUnit(
    const std::string& hero_id, uint16_t level, uint16_t exp, int hp, int mp,
    Vec2D position, int direction, bool done_action, Force force) {
  if (!game_->IsValidCoords(position)) throw std::out_of_range("saved unit position is invalid");
  if (game_->UnitInCell(position)) throw std::logic_error("saved units overlap");
  if (direction < static_cast<int>(kDirNone) || direction > static_cast<int>(kDirDown)) {
    throw std::out_of_range("saved unit direction is invalid");
  }
  const uint32_t unit_id = game_->GenerateUnit(hero_id, level, force, position);
  Unit* unit = game_->GetUnit(unit_id);
  unit->RestoreState(level, exp, HpMp(hp, mp), static_cast<Direction>(direction), done_action);
  return unit_id;
}

void RLEnvironment::RestoreItem(const std::string& item_id, uint32_t count) {
  auto item = items_.find(item_id);
  if (item == items_.end()) throw std::out_of_range("saved item is unknown");
  item->second.count = count;
}

void RLEnvironment::RestoreVisitedSite(const std::string& site_id) {
  auto site = std::find_if(sites_.begin(), sites_.end(), [&](const SiteInfo& candidate) {
    return candidate.id == site_id;
  });
  if (site == sites_.end()) throw std::out_of_range("saved supply site is unknown");
  visited_sites_.insert(site_id);
}

void RLEnvironment::FinishRestore() { RebuildLegalActions(); }

float RLEnvironment::UnitHealthTotal(Force force) const {
  float total = 0.0f;
  game_->ForEachUnitIdxConst([&](uint32_t, const Unit* unit) {
    if (!unit->IsDead() && unit->GetForce() == force) {
      total += Ratio(unit->GetCurrentHpMp().hp, unit->GetOriginalHpMp().hp);
    }
  });
  return total;
}

}  // namespace core
}  // namespace mengde
