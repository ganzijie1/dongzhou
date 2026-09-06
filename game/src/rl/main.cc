#include <algorithm>
#include <cctype>
#include <cstdlib>
#include <exception>
#include <iomanip>
#include <iostream>
#include <memory>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "core/attack_range.h"
#include "core/cell.h"
#include "core/game.h"
#include "core/formulae.h"
#include "core/magic.h"
#include "core/rl_environment.h"
#include "core/scenario.h"
#include "core/terrain.h"
#include "core/unit_class.h"

using mengde::core::Game;
using mengde::core::Magic;
using mengde::core::RLEnvironment;
using mengde::core::Scenario;
using mengde::core::Terrain;
using mengde::core::Unit;
using mengde::core::HpMp;
using mengde::core::Attribute;

namespace {

std::string JsonString(const std::string& value) {
  std::ostringstream out;
  out << '"';
  for (char c : value) {
    switch (c) {
      case '"': out << "\\\""; break;
      case '\\': out << "\\\\"; break;
      case '\n': out << "\\n"; break;
      case '\r': out << "\\r"; break;
      case '\t': out << "\\t"; break;
      default: out << c; break;
    }
  }
  out << '"';
  return out.str();
}

class Session {
 public:
  Session(const std::string& scenario_id, uint32_t max_units, uint32_t max_actions, bool interactive,
          uint32_t initial_stage = 0)
      : scenario_id_(scenario_id), max_units_(max_units), max_actions_(max_actions), interactive_(interactive) {
    Reset(initial_stage);
  }

  void Reset(uint32_t stage_index = 0) {
    environment_.reset();
    commander_progress_.clear();
    training_candidates_.clear();
    money_ = scenario_id_ == "dongzhou" ? 500 : 0;
    scenario_.reset(new Scenario(scenario_id_, stage_index));
    Game* game = scenario_->GetGame();
    if (!game->SubmitDeploy()) {
      throw std::runtime_error("headless RL requires a stage with automatic deployment");
    }
    if (scenario_id_ == "dongzhou") SetStageLevel(game, 1);
    environment_.reset(new RLEnvironment(game, max_units_, max_actions_, !interactive_));
    if (scenario_id_ == "dongzhou") RecordCurrentCommanderProgress();
  }

  bool NextStage() {
    if (!scenario_->HasNextStage()) return false;
    const uint16_t next_level = scenario_id_ == "dongzhou" ? RoundedOwnLevel() : 1;
    if (scenario_id_ == "dongzhou") RecordCurrentCommanderProgress();
    std::map<std::string, uint32_t> inventory = environment_->GetInventoryCounts();
    money_ += environment_->GetGame()->GetLuaScript()->GetOpt<uint32_t>(
        "gstage.rewards.money");
    lua::Lua* stage_lua = environment_->GetGame()->GetLuaScript();
    std::vector<std::string> reward_ids;
    std::vector<std::string> reward_conditions;
    std::vector<uint32_t> reward_amounts;
    if (stage_lua->GetOpt<bool>("gstage.rewards.has_conditional_items")) {
      stage_lua->ForEachTableEntry("gstage.rewards.conditional_items", [&](lua::Lua* entry, const std::string&) {
        reward_ids.push_back(entry->Get<std::string>("id"));
        reward_conditions.push_back(entry->Get<std::string>("condition"));
        reward_amounts.push_back(entry->Get<uint32_t>("amount"));
      });
    }
    for (size_t i = 0; i < reward_ids.size(); ++i) {
      if (stage_lua->GetOpt<bool>(reward_conditions[i])) inventory[reward_ids[i]] += reward_amounts[i];
    }
    environment_.reset();
    scenario_->NextStage();
    Game* game = scenario_->GetGame();
    if (!game->SubmitDeploy()) {
      throw std::runtime_error("headless RL requires a stage with automatic deployment");
    }
    if (scenario_id_ == "dongzhou") {
      PrepareTrainingCandidates(game, next_level);
      SetStageProgress(game, next_level, commander_progress_);
    }
    environment_.reset(new RLEnvironment(game, max_units_, max_actions_, !interactive_));
    environment_->SetInventoryCounts(inventory);
    if (scenario_id_ == "dongzhou") RecordCurrentCommanderProgress();
    return true;
  }

  void LoadStage(uint32_t stage_index) { Reset(stage_index); }

  RLEnvironment* environment() { return environment_.get(); }
  uint32_t stage_index() const { return scenario_->GetStageNo(); }

  uint32_t money() const { return money_; }
  void RestoreMoney(uint32_t money) { money_ = money; }
  void PurchaseItem(const std::string& item_id) { environment_->PurchaseItem(item_id, &money_); }

  uint16_t ResolveDuel(uint32_t attacker_id, uint32_t defender_id) {
    Game* game = environment_->GetGame();
    Unit* attacker = game->GetUnit(attacker_id);
    Unit* defender = game->GetUnit(defender_id);
    if (attacker == nullptr || defender == nullptr || attacker->IsDead() || defender->IsDead()) {
      throw std::logic_error("duel participants must be alive");
    }
    uint16_t duel_exp = 0;
    lua::Lua* script = game->GetLuaScript();
    if (script->GetOpt<bool>("gduel_enabled")) {
      script->ForEachTableEntry("gduels", [&](lua::Lua* entry, const std::string&) {
        if (entry->Get<std::string>("attacker") == attacker->GetId() &&
            entry->Get<std::string>("defender") == defender->GetId()) {
          duel_exp = entry->GetOpt<uint16_t>("exp");
        }
      });
    }
    if (duel_exp == 0 || attacker->GetForce() != mengde::core::Force::kOwn ||
        defender->GetForce() != mengde::core::Force::kEnemy) {
      throw std::logic_error("duel is not configured for these units");
    }
    const Vec2D delta = attacker->GetPosition() - defender->GetPosition();
    if (std::abs(delta.x) + std::abs(delta.y) != 1) {
      throw std::logic_error("duel participants are not adjacent");
    }
    attacker->GainExp(duel_exp);
    game->KillUnit(defender);
    game->CheckStatus();
    return duel_exp;
  }

  struct UnitProgress {
    uint16_t level;
    uint16_t exp;
    uint16_t training_penalty;
    uint16_t last_stage;
  };

  struct TrainingCandidate {
    std::string hero_id;
    uint16_t current_level;
    uint16_t target_level;
    uint16_t penalty;
  };

  uint16_t CurrentStageNo() const {
    return static_cast<uint16_t>(scenario_->GetStageNo());
  }

  static std::string ProgressionKey(std::string id) {
    while (!id.empty() && std::isdigit(static_cast<unsigned char>(id.back()))) {
      id.pop_back();
    }
    return id;
  }

  std::map<std::string, UnitProgress> CaptureOwnCommanderProgress() const {
    Game* game = environment_->GetGame();
    const std::vector<std::string> commander_ids =
        game->GetLuaScript()->GetVector<std::string>("gcommanders");
    std::map<std::string, UnitProgress> progress;
    game->ForEachUnitIdxConst([&](uint32_t, const Unit* unit) {
      if (unit->GetForce() != mengde::core::Force::kOwn) return;
      bool named_commander = false;
      for (const std::string& id : commander_ids) {
        if (unit->GetId() == id) {
          named_commander = true;
          break;
        }
      }
      if (!named_commander) return;
      progress[ProgressionKey(unit->GetId())] = {
          unit->GetLevel(), unit->GetExp(), unit->GetTrainingPenalty(), CurrentStageNo()};
    });
    return progress;
  }

  void RecordCurrentCommanderProgress() {
    if (!environment_) return;
    for (const auto& entry : CaptureOwnCommanderProgress()) {
      commander_progress_[entry.first] = entry.second;
    }
  }

  void RestoreCommanderProgress(
      const std::string& id, uint16_t level, uint16_t exp,
      uint16_t training_penalty, uint16_t last_stage) {
    commander_progress_[ProgressionKey(id)] = {
        level, exp, training_penalty, last_stage};
  }

  void ApplyRestoredCommanderPenalties() {
    Game* game = environment_->GetGame();
    const std::vector<std::string> commander_ids =
        game->GetLuaScript()->GetVector<std::string>("gcommanders");
    game->ForEachUnit([&](Unit* unit) {
      if (unit->GetForce() != mengde::core::Force::kOwn) return;
      bool named_commander = false;
      for (const std::string& id : commander_ids) {
        if (unit->GetId() == id) named_commander = true;
      }
      if (!named_commander) return;
      const auto progress = commander_progress_.find(ProgressionKey(unit->GetId()));
      if (progress != commander_progress_.end()) {
        unit->SetTrainingPenalty(progress->second.training_penalty);
      }
    });
  }

  void PrepareTrainingCandidates(Game* game, uint16_t average_level) {
    training_candidates_.clear();
    const uint16_t stage = CurrentStageNo();
    const std::vector<std::string> commander_ids =
        game->GetLuaScript()->GetVector<std::string>("gcommanders");
    game->ForEachUnit([&](Unit* unit) {
      if (unit->GetForce() != mengde::core::Force::kOwn) return;
      bool named_commander = false;
      for (const std::string& id : commander_ids) {
        if (unit->GetId() == id) named_commander = true;
      }
      if (!named_commander) return;
      const auto progress = commander_progress_.find(ProgressionKey(unit->GetId()));
      if (progress == commander_progress_.end()) return;
      const UnitProgress& old = progress->second;
      if (stage <= old.last_stage + 2 || old.level >= average_level) return;
      const uint16_t gained_levels = average_level - old.level;
      training_candidates_.push_back({
          unit->GetId(), old.level, average_level,
          static_cast<uint16_t>((gained_levels + 1) / 2)});
    });
  }

  UnitProgress ApplyTraining(const std::string& hero_id) {
    for (auto candidate = training_candidates_.begin();
         candidate != training_candidates_.end(); ++candidate) {
      if (candidate->hero_id != hero_id) continue;
      Unit* matched = nullptr;
      environment_->GetGame()->ForEachUnit([&](Unit* unit) {
        if (unit->GetId() == hero_id &&
            unit->GetForce() == mengde::core::Force::kOwn) matched = unit;
      });
      if (matched == nullptr) throw std::logic_error("training candidate is not deployed");
      matched->SetTrainingPenalty(
          static_cast<uint16_t>(matched->GetTrainingPenalty() + candidate->penalty));
      RestoreFullProgress(matched, candidate->target_level, matched->GetExp());
      const UnitProgress result = {
          matched->GetLevel(), matched->GetExp(), matched->GetTrainingPenalty(),
          CurrentStageNo()};
      commander_progress_[ProgressionKey(hero_id)] = result;
      training_candidates_.erase(candidate);
      return result;
    }
    throw std::logic_error("commander is not eligible for training");
  }

  const std::map<std::string, UnitProgress>& commander_progress() const {
    return commander_progress_;
  }

  const std::vector<TrainingCandidate>& training_candidates() const {
    return training_candidates_;
  }

  static void RestoreFullProgress(Unit* unit, uint16_t level, uint16_t exp) {
    const HpMp current = unit->GetCurrentHpMp();
    const auto direction = unit->GetDirection();
    const bool done = unit->IsDoneAction();
    unit->RestoreState(level, exp, current, direction, done);
    unit->RestoreState(level, exp, unit->GetOriginalHpMp(), direction, done);
  }

  static void SetStageProgress(
      Game* game, uint16_t average_level,
      const std::map<std::string, UnitProgress>& carried_progress) {
    const std::vector<std::string> commander_ids =
        game->GetLuaScript()->GetVector<std::string>("gcommanders");
    game->ForEachUnit([&](Unit* unit) {
      uint16_t level = average_level;
      uint16_t exp = 0;
      uint16_t training_penalty = 0;
      if (unit->GetForce() == mengde::core::Force::kOwn) {
        bool named_commander = false;
        for (const std::string& id : commander_ids) {
          if (unit->GetId() == id) {
            named_commander = true;
            break;
          }
        }
        if (named_commander) {
          const auto carried = carried_progress.find(ProgressionKey(unit->GetId()));
          if (carried != carried_progress.end()) {
            level = carried->second.level;
            exp = carried->second.exp;
            training_penalty = carried->second.training_penalty;
          }
        }
      }
      unit->SetTrainingPenalty(training_penalty);
      RestoreFullProgress(unit, level, exp);
    });
  }
  uint16_t RoundedOwnLevel() const {
    Game* game = environment_->GetGame();
    const std::vector<std::string> commander_ids =
        game->GetLuaScript()->GetVector<std::string>("gcommanders");
    uint32_t sum = 0;
    uint32_t count = 0;
    game->ForEachUnitIdxConst([&](uint32_t, const Unit* unit) {
      if (unit->GetForce() != mengde::core::Force::kOwn) return;
      bool named_commander = false;
      for (const std::string& id : commander_ids) {
        if (unit->GetId() == id) named_commander = true;
      }
      if (!named_commander) return;
      sum += unit->GetLevel();
      ++count;
    });
    return count == 0 ? 1 : static_cast<uint16_t>((sum + count / 2) / count);
  }

  static void SetStageLevel(Game* game, uint16_t level) {
    game->ForEachUnit([&](Unit* unit) {
      RestoreFullProgress(unit, level, 0);
    });
  }

 private:
  std::string                    scenario_id_;
  uint32_t                       max_units_;
  uint32_t                       max_actions_;
  bool                           interactive_;
  std::unique_ptr<Scenario>      scenario_;
  std::unique_ptr<RLEnvironment> environment_;
  uint32_t                       money_;
  std::map<std::string, UnitProgress> commander_progress_;
  std::vector<TrainingCandidate> training_candidates_;
};

void PrintState(RLEnvironment* env, float reward, bool terminated, bool truncated) {
  const std::vector<float> observation = env->Observe();
  const size_t action_count = env->GetLegalActions().size();
  std::cout << "RL\t{\"observation\":[";
  for (size_t i = 0; i < observation.size(); ++i) {
    if (i != 0) std::cout << ',';
    std::cout << std::setprecision(7) << observation[i];
  }
  std::cout << "],\"reward\":" << reward << ",\"terminated\":" << (terminated ? "true" : "false")
            << ",\"truncated\":" << (truncated ? "true" : "false") << ",\"action_count\":" << action_count
            << ",\"current_force\":" << static_cast<int>(env->GetCurrentForce())
            << ",\"turn_current\":" << env->GetGame()->GetTurnCurrent()
            << ",\"turn_limit\":" << env->GetGame()->GetTurnLimit()
            << ",\"status\":" << env->GetGameStatus()
            << "}" << std::endl;
}

void PrintActions(RLEnvironment* env) {
  const std::vector<RLEnvironment::Action>& actions = env->GetLegalActions();
  std::cout << "RL\t{\"actions\":[";
  for (size_t i = 0; i < actions.size(); ++i) {
    if (i != 0) std::cout << ',';
    const RLEnvironment::Action& action = actions[i];
    std::cout << "{\"index\":" << i << ",\"unit\":" << action.unit_id << ",\"type\":"
              << static_cast<int>(action.type) << ",\"x\":" << action.destination.x << ",\"y\":"
              << action.destination.y << ",\"target\":";
    if (action.target_id == RLEnvironment::kNoTarget)
      std::cout << "null";
    else
      std::cout << action.target_id;
    std::cout << ",\"skill\":" << JsonString(action.skill_id);
    if (action.target_id != RLEnvironment::kNoTarget) {
      Unit* attacker = env->GetGame()->GetUnit(action.unit_id);
      Unit* defender = env->GetGame()->GetUnit(action.target_id);
      int damage = 0;
      int heal = 0;
      int accuracy = 100;
      int critical = 0;
      int double_attack = 0;
      int mp_cost = 0;
      int counter_damage = 0;
      int counter_accuracy = 0;
      bool target_enemy = attacker->IsHostile(defender);
      bool stat_modifier = false;
      if (action.type == RLEnvironment::ActionType::kBasicAttack) {
        damage = mengde::core::Formulae::ComputeBasicAttackDamageAt(
            env->GetGame()->GetMap(), attacker, action.destination, defender,
            defender->GetPosition());
        accuracy = mengde::core::Formulae::ComputeBasicAttackAccuracy(attacker, defender);
        critical = mengde::core::Formulae::ComputeBasicAttackCritical(attacker, defender);
        double_attack = mengde::core::Formulae::ComputeBasicAttackDouble(attacker, defender);
        if (defender->IsInRange(action.destination)) {
          counter_damage = mengde::core::Formulae::ComputeBasicAttackDamageAt(
              env->GetGame()->GetMap(), defender, defender->GetPosition(), attacker,
              action.destination);
          counter_accuracy = mengde::core::Formulae::ComputeBasicAttackAccuracy(defender, attacker);
        }
      } else if (action.type == RLEnvironment::ActionType::kMagic) {
        Magic* magic = env->GetGame()->GetMagic(action.skill_id);
        mp_cost = magic->GetMpCost();
        accuracy = magic->CalcAccuracy(attacker, defender);
        if (magic->IsTypeDeal()) damage = magic->CalcDamage(attacker, defender);
        if (magic->IsTypeHeal()) heal = magic->CalcDamage(attacker, defender);
        stat_modifier = !magic->IsTypeDeal() && !magic->IsTypeHeal();
      }
      const double hit_probability = static_cast<double>(accuracy) / 100.0;
      double expected_damage = hit_probability * static_cast<double>(damage);
      if (action.type == RLEnvironment::ActionType::kBasicAttack) {
        expected_damage *= 1.0 + static_cast<double>(critical) / 200.0;
        expected_damage *= 1.0 + 0.75 * static_cast<double>(double_attack) / 100.0;
      }
      const double expected_heal = hit_probability * static_cast<double>(heal);
      std::cout << ",\"damage\":" << damage << ",\"heal\":" << heal
                << ",\"accuracy\":" << accuracy << ",\"critical\":" << critical
                << ",\"double\":" << double_attack << ",\"mp_cost\":" << mp_cost
                << ",\"counter_damage\":" << counter_damage
                << ",\"counter_accuracy\":" << counter_accuracy
                << ",\"expected_damage\":" << expected_damage
                << ",\"expected_heal\":" << expected_heal
                << ",\"target_enemy\":" << (target_enemy ? "true" : "false")
                << ",\"stat_modifier\":" << (stat_modifier ? "true" : "false")
                << ",\"advantage\":"
                << mengde::core::Formulae::ComputeClassAdvantage(attacker, defender);
    }
    std::cout << '}';
  }
  std::cout << "]}" << std::endl;
}

void PrintUnits(RLEnvironment* env) {
  Game* game = env->GetGame();
  std::cout << "RL\t{\"units\":[";
  bool first = true;
  game->ForEachUnitIdxConst([&](uint32_t id, const Unit* const_unit) {
    Unit* unit = game->GetUnit(id);
    if (!first) std::cout << ',';
    first = false;
    const HpMp& current = unit->GetCurrentHpMp();
    const HpMp& maximum = unit->GetOriginalHpMp();
    const Attribute& attr = unit->GetCurrentAttr();
    mengde::core::Cell* cell = game->GetMap()->GetCell(unit->GetPosition());
    Terrain* terrain = cell->GetTerrain();
    int attack_min = 999;
    int attack_max = 0;
    unit->GetAttackRange().ForEach([&](Vec2D offset) {
      const int distance = std::abs(offset.x) + std::abs(offset.y);
      attack_min = std::min(attack_min, distance);
      attack_max = std::max(attack_max, distance);
    });
    if (attack_min == 999) attack_min = 0;
    std::cout << "{\"id\":" << id << ",\"name\":" << JsonString(unit->GetId())
              << ",\"force\":" << static_cast<int>(unit->GetForce()) << ",\"name\":" << JsonString(unit->GetId())
              << ",\"class\":" << JsonString(unit->GetClass()->GetId())
              << ",\"force\":" << static_cast<int>(unit->GetForce())
              << ",\"level\":" << unit->GetLevel() << ",\"exp\":" << unit->GetExp()
              << ",\"x\":" << unit->GetPosition().x
              << ",\"y\":" << unit->GetPosition().y
              << ",\"direction\":" << static_cast<int>(unit->GetDirection()) << ",\"hp\":" << current.hp
              << ",\"max_hp\":" << maximum.hp << ",\"mp\":" << current.mp
              << ",\"max_mp\":" << maximum.mp << ",\"atk\":" << attr.atk
              << ",\"def\":" << attr.def << ",\"dex\":" << attr.dex
              << ",\"int\":" << attr.itl << ",\"mor\":" << attr.mor
              << ",\"move\":" << unit->GetMove() << ",\"attack_min\":" << attack_min
              << ",\"attack_max\":" << attack_max << ",\"attack_offsets\":[";
    bool first_offset = true;
    unit->GetAttackRange().ForEach([&](Vec2D offset) {
      if (!first_offset) std::cout << ',';
      first_offset = false;
      std::cout << '[' << offset.x << ',' << offset.y << ']';
    });
    std::cout << "],\"done\":"
              << (unit->IsDoneAction() ? "true" : "false") << ",\"dead\":"
              << (unit->IsDead() ? "true" : "false") << ",\"invulnerable\":"
              << (unit->IsInvulnerable() ? "true" : "false") << ",\"terrain\":"
              << JsonString(terrain->GetName()) << ",\"primary_terrain\":"
              << JsonString(terrain->GetName()) << ",\"secondary_terrain\":";
    if (cell->HasSecondaryTerrain())
      std::cout << JsonString(cell->GetSecondaryTerrain()->GetName());
    else
      std::cout << "null";
    std::cout << ",\"coverage\":" << static_cast<int>(cell->GetSecondaryCoverage())
              << ",\"terrain_effect\":" << cell->GetTerrainEffect(unit->GetClassIndex())
              << ",\"move_cost\":" << cell->GetMoveCost(unit->GetClassIndex())
              << ",\"skills\":[";
    bool first_skill = true;
    game->GetMagicManager()->ForEach([&](Magic* magic) {
      if (!magic->IsAvailible(unit)) return;
      if (!first_skill) std::cout << ',';
      first_skill = false;
      std::cout << "{\"id\":" << JsonString(magic->GetId()) << ",\"mp\":" << magic->GetMpCost()
                << ",\"power\":" << magic->GetPower() << ",\"target_enemy\":"
                << (magic->GetIsTargetEnemy() ? "true" : "false") << '}';
    });
    std::cout << "]}";
    (void)const_unit;
  });
  std::cout << "]}" << std::endl;
}

void PrintMap(RLEnvironment* env) {
  const Vec2D size = env->GetMapSize();
  Game* game = env->GetGame();
  std::cout << "RL\t{\"width\":" << size.x << ",\"height\":" << size.y << ",\"terrain\":[";
  bool first = true;
  for (int y = 0; y < size.y; ++y) {
    for (int x = 0; x < size.x; ++x) {
      if (!first) std::cout << ',';
      first = false;
      std::cout << JsonString(game->GetMap()->GetCell({x, y})->GetTerrainName());
    }
  }
  std::cout << "],\"terrain_layers\":[";
  first = true;
  for (int y = 0; y < size.y; ++y) {
    for (int x = 0; x < size.x; ++x) {
      if (!first) std::cout << ',';
      first = false;
      mengde::core::Cell* cell = game->GetMap()->GetCell({x, y});
      std::cout << "{\"primary_terrain\":" << JsonString(cell->GetTerrainName())
                << ",\"secondary_terrain\":";
      if (cell->HasSecondaryTerrain())
        std::cout << JsonString(cell->GetSecondaryTerrain()->GetName());
      else
        std::cout << "null";
      std::cout << ",\"coverage\":" << static_cast<int>(cell->GetSecondaryCoverage()) << '}';
    }
  }
  std::cout << "]}" << std::endl;
}
void PrintPath(RLEnvironment* env, uint32_t unit_id, int x, int y) {
  const std::vector<Vec2D> path = env->GetMovementPath(unit_id, {x, y});
  std::cout << "RL\t{\"path\":[";
  for (size_t i = 0; i < path.size(); ++i) {
    if (i != 0) std::cout << ',';
    std::cout << '[' << path[i].x << ',' << path[i].y << ']';
  }
  std::cout << "]}" << std::endl;
}

void PrintMoves(RLEnvironment* env, uint32_t unit_id) {
  const std::vector<Vec2D> moves = env->GetMovementRange(unit_id);
  std::cout << "RL\t{\"moves\":[";
  for (size_t i = 0; i < moves.size(); ++i) {
    if (i != 0) std::cout << ',';
    std::cout << '[' << moves[i].x << ',' << moves[i].y << ']';
  }
  std::cout << "]}" << std::endl;
}

void PrintMoveCosts(RLEnvironment* env, uint32_t unit_id) {
  Game* game = env->GetGame();
  Unit* unit = game->GetUnit(unit_id);
  const Vec2D size = env->GetMapSize();
  std::cout << "RL\t{\"costs\":[";
  bool first = true;
  for (int y = 0; y < size.y; ++y) {
    for (int x = 0; x < size.x; ++x) {
      if (!first) std::cout << ',';
      first = false;
      std::cout << game->GetMap()->GetCell({x, y})->GetMoveCost(unit->GetClassIndex());
    }
  }
  std::cout << "]}" << std::endl;
}

void PrintSupplies(Session* session) {
  RLEnvironment* env = session->environment();
  const std::vector<RLEnvironment::ItemInfo> items = env->GetItems();
  std::cout << "RL\t{\"money\":" << session->money() << ",\"items\":[";
  for (size_t i = 0; i < items.size(); ++i) {
    if (i != 0) std::cout << ',';
    const auto& item = items[i];
    std::cout << "{\"id\":" << JsonString(item.id) << ",\"name\":" << JsonString(item.name)
              << ",\"hp\":" << item.hp << ",\"mp\":" << item.mp << ",\"price\":" << item.price
              << ",\"count\":" << item.count << '}';
  }
  std::cout << "],\"sites\":[";
  const std::vector<RLEnvironment::SiteInfo>& sites = env->GetSites();
  for (size_t i = 0; i < sites.size(); ++i) {
    if (i != 0) std::cout << ',';
    const auto& site = sites[i];
    std::cout << "{\"id\":" << JsonString(site.id) << ",\"name\":" << JsonString(site.name)
              << ",\"x\":" << site.position.x << ",\"y\":" << site.position.y
              << ",\"restore_hp\":" << site.restore_hp << ",\"restore_mp\":" << site.restore_mp << '}';
  }
  std::cout << "]}" << std::endl;
}

void PrintNotices(RLEnvironment* env) {
  const std::vector<std::string> notices = env->TakeNotices();
  std::cout << "RL\t{\"notices\":[";
  for (size_t i = 0; i < notices.size(); ++i) {
    if (i != 0) std::cout << ',';
    std::cout << JsonString(notices[i]);
  }
  std::cout << "]}" << std::endl;
}

void PrintBattleEvents(RLEnvironment* env, bool drain) {
  auto& queue = env->GetGame()->GetBattleEventQueue();
  std::cout << "RL\t{\"enabled\":" << (queue.enabled() ? "true" : "false") << ",\"events\":[";
  bool first = true;
  for (const auto& event : queue.pending()) {
    if (!first) std::cout << ',';
    first = false;
    std::cout << "{\"sequence\":" << event.sequence
              << ",\"turn\":" << event.turn
              << ",\"type\":" << JsonString(mengde::core::BattleEventTypeName(event.type))
              << ",\"actor\":" << JsonString(event.actor)
              << ",\"target\":" << JsonString(event.target)
              << ",\"detail\":" << JsonString(event.detail)
              << ",\"from\":[" << event.from_x << ',' << event.from_y << ']'
              << ",\"to\":[" << event.to_x << ',' << event.to_y << ']'
              << ",\"value\":" << event.value << '}';
  }
  std::cout << "]}" << std::endl;
  if (drain) queue.ClearPending();
}
void PrintOk() { std::cout << "RL\t{\"ok\":true}" << std::endl; }

void PrintSnapshot(Session* session) {
  RLEnvironment* env = session->environment();
  Game* game = env->GetGame();
  std::cout << "RL\t{\"stage_index\":" << session->stage_index()
            << ",\"money\":" << session->money()
            << ",\"turn_current\":" << game->GetTurnCurrent()
            << ",\"current_force\":" << static_cast<int>(game->GetCurrentForce())
            << ",\"agent_actions\":" << env->GetAgentActions()
            << ",\"truncated\":" << (env->GetTruncated() ? "true" : "false")
            << ",\"units\":[";
  bool first = true;
  game->ForEachUnitIdxConst([&](uint32_t id, const Unit* unit) {
    if (!first) std::cout << ',';
    first = false;
    const HpMp& hpmp = unit->GetCurrentHpMp();
    std::cout << "{\"id\":" << id << ",\"level\":" << unit->GetLevel()
              << ",\"exp\":" << unit->GetExp() << ",\"hp\":" << hpmp.hp
              << ",\"mp\":" << hpmp.mp << ",\"x\":" << unit->GetPosition().x
              << ",\"y\":" << unit->GetPosition().y
              << ",\"direction\":" << static_cast<int>(unit->GetDirection())
              << ",\"done\":" << (unit->IsDoneAction() ? "true" : "false")
              << ",\"invulnerable\":" << (unit->IsInvulnerable() ? "true" : "false") << '}';
  });
  std::cout << "],\"inventory\":{";
  first = true;
  for (const auto& item : env->GetInventoryCounts()) {
    if (!first) std::cout << ',';
    first = false;
    std::cout << JsonString(item.first) << ':' << item.second;
  }
  std::cout << "},\"visited_sites\":[";
  first = true;
  for (const std::string& site_id : env->GetVisitedSites()) {
    if (!first) std::cout << ',';
    first = false;
    std::cout << JsonString(site_id);
  }
  std::cout << "],\"commander_progress\":{";
  first = true;
  for (const auto& entry : session->commander_progress()) {
    if (!first) std::cout << ',';
    first = false;
    std::cout << JsonString(entry.first) << ":{\"level\":" << entry.second.level
              << ",\"exp\":" << entry.second.exp
              << ",\"training_penalty\":" << entry.second.training_penalty
              << ",\"last_stage\":" << entry.second.last_stage << '}';
  }
  std::cout << "}}" << std::endl;
}

void PrintTraining(Session* session) {
  std::cout << "RL\t{\"candidates\":[";
  bool first = true;
  for (const auto& candidate : session->training_candidates()) {
    if (!first) std::cout << ',';
    first = false;
    std::cout << "{\"hero_id\":" << JsonString(candidate.hero_id)
              << ",\"current_level\":" << candidate.current_level
              << ",\"target_level\":" << candidate.target_level
              << ",\"penalty\":" << candidate.penalty << '}';
  }
  std::cout << "]}" << std::endl;
}

void PrintStoryEntries(lua::Lua* script, const std::string& name) {
  std::cout << '[';
  bool first = true;
  script->ForEachTableEntry(name, [&](lua::Lua* entry, const std::string&) {
    if (!first) std::cout << ',';
    first = false;
    std::cout << "{\"speaker\":" << JsonString(entry->Get<std::string>("speaker"))
              << ",\"text\":" << JsonString(entry->Get<std::string>("text")) << '}';
  });
  std::cout << ']';
}

void PrintStoryDuels(lua::Lua* script) {
  std::cout << '[';
  bool first = true;
  if (script->GetOpt<bool>("gduel_enabled")) {
    script->ForEachTableEntry("gduels", [&](lua::Lua* entry, const std::string&) {
      if (!first) std::cout << ',';
      first = false;
      std::cout << "{\"attacker\":" << JsonString(entry->Get<std::string>("attacker"))
                << ",\"defender\":" << JsonString(entry->Get<std::string>("defender"))
                << ",\"exp\":" << entry->GetOpt<uint16_t>("exp")
                << ",\"outcome\":" << JsonString(entry->GetOpt<std::string>("outcome"))
                << ",\"text\":" << JsonString(entry->GetOpt<std::string>("text"))
                << ",\"attacker_speech\":" << JsonString(entry->GetOpt<std::string>("attacker_speech"))
                << ",\"defender_speech\":" << JsonString(entry->GetOpt<std::string>("defender_speech"))
                << ",\"result_speech\":" << JsonString(entry->GetOpt<std::string>("result_speech"))
                << '}';
    });
  }
  std::cout << ']';
}

void PrintStoryEvents(lua::Lua* script) {
  std::cout << '[';
  bool first = true;
  if (script->GetOpt<bool>("gevents_enabled")) {
    script->ForEachTableEntry("gstory.events", [&](lua::Lua* entry, const std::string&) {
      if (!first) std::cout << ',';
      first = false;
      std::cout << "{\"id\":" << JsonString(entry->Get<std::string>("id"))
                << ",\"trigger\":" << JsonString(entry->Get<std::string>("trigger"))
                << ",\"turn\":" << entry->GetOpt<uint16_t>("turn")
                << ",\"unit\":" << JsonString(entry->GetOpt<std::string>("unit"))
                << ",\"target\":" << JsonString(entry->GetOpt<std::string>("target"))
                << ",\"hp_percent\":" << entry->GetOpt<uint16_t>("hp_percent")
                << ",\"speaker\":" << JsonString(entry->Get<std::string>("speaker"))
                << ",\"text\":" << JsonString(entry->Get<std::string>("text"))
                << '}';
    });
  }
  std::cout << ']';
}
void PrintStory(RLEnvironment* env) {
  lua::Lua* script = env->GetGame()->GetLuaScript();
  const std::string title = script->GetOpt<std::string>("gstory.title");
  if (title == "nil") {
    std::cout << "RL\t{}" << std::endl;
    return;
  }
  std::cout << "RL\t{\"chapter\":" << JsonString(script->GetOpt<std::string>("gstory.chapter"))
            << ",\"title\":" << JsonString(title)
            << ",\"battle_title\":" << JsonString(script->GetOpt<std::string>("gstory.battle_title"))
            << ",\"objective\":" << JsonString(script->GetOpt<std::string>("gstory.objective"))
            << ",\"map_asset\":" << JsonString(script->GetOpt<std::string>("gstory.map_asset"))
            << ",\"story_only\":" << (script->GetOpt<bool>("gstory.story_only") ? "true" : "false")
            << ",\"intro\":";
  PrintStoryEntries(script, "gstory.intro");
  std::cout << ",\"victory\":";
  PrintStoryEntries(script, "gstory.victory");
  std::cout << ",\"defeat\":";
  PrintStoryEntries(script, "gstory.defeat");
  std::cout << ",\"duels\":";
  PrintStoryDuels(script);
  std::cout << ",\"events\":";
  PrintStoryEvents(script);
  std::cout << '}' << std::endl;
}

}  // namespace

int main(int argc, char** argv) {
  const std::string scenario_id = argc > 1 ? argv[1] : "example";
  const uint32_t max_units      = argc > 2 ? static_cast<uint32_t>(std::atoi(argv[2])) : 32;
  const uint32_t max_actions    = argc > 3 ? static_cast<uint32_t>(std::atoi(argv[3])) : 20;
  const bool interactive       = argc > 4 && std::string(argv[4]) == "interactive";
  const uint32_t initial_stage  = argc > 5 ? static_cast<uint32_t>(std::atoi(argv[5])) : 0;

  try {
    Session session(scenario_id, max_units, max_actions, interactive, initial_stage);
    PrintState(session.environment(), 0.0f, false, false);

    std::string line;
    while (std::getline(std::cin, line)) {
      std::istringstream command(line);
      std::string op;
      command >> op;
      if (op == "RESET") {
        session.Reset();
        PrintState(session.environment(), 0.0f, false, false);
      } else if (op == "NEXT") {
        if (session.NextStage())
          PrintState(session.environment(), 0.0f, false, false);
        else
          std::cout << "RL\t{\"complete\":true}" << std::endl;
      } else if (op == "STEP") {
        uint32_t action = 0;
        command >> action;
        const RLEnvironment::StepResult result = session.environment()->Step(action);
        PrintState(session.environment(), result.reward, result.terminated, result.truncated);
      } else if (op == "ACTIONS") {
        PrintActions(session.environment());
      } else if (op == "MAP") {
        PrintMap(session.environment());
      } else if (op == "PATH") {
        uint32_t unit_id = 0;
        int x = 0;
        int y = 0;
        command >> unit_id >> x >> y;
        PrintPath(session.environment(), unit_id, x, y);
      } else if (op == "MOVES") {
        uint32_t unit_id = 0;
        command >> unit_id;
        PrintMoves(session.environment(), unit_id);
      } else if (op == "COSTS") {
        uint32_t unit_id = 0;
        command >> unit_id;
        PrintMoveCosts(session.environment(), unit_id);
      } else if (op == "SUPPLIES") {
        PrintSupplies(&session);
      } else if (op == "BUY") {
        std::string item_id;
        command >> item_id;
        session.PurchaseItem(item_id);
        PrintSupplies(&session);
} else if (op == "DUEL") {
        uint32_t attacker_id = 0;
        uint32_t defender_id = 0;
        command >> attacker_id >> defender_id;
        session.ResolveDuel(attacker_id, defender_id);
        PrintState(session.environment(), 2.0f, session.environment()->IsDone(), false);
      } else if (op == "NOTICES") {
        PrintNotices(session.environment());
      } else if (op == "EVENTS") {
        PrintBattleEvents(session.environment(), false);
      } else if (op == "DRAIN_EVENTS") {
        PrintBattleEvents(session.environment(), true);
      } else if (op == "SEED") {
        uint32_t seed = 0;
        command >> seed;
        std::srand(seed);
        PrintOk();
      } else if (op == "USE_ITEM") {
        uint32_t unit_id = 0;
        std::string item_id;
        command >> unit_id >> item_id;
        const RLEnvironment::StepResult result = session.environment()->UseItem(unit_id, item_id);
        PrintState(session.environment(), result.reward, result.terminated, result.truncated);
      } else if (op == "SNAPSHOT") {
        PrintSnapshot(&session);
      } else if (op == "LOAD_STAGE") {
        uint32_t stage_index = 0;
        command >> stage_index;
        session.LoadStage(stage_index);
        PrintState(session.environment(), 0.0f, false, false);
      } else if (op == "RESTORE_BEGIN") {
        uint16_t turn = 1;
        uint32_t force = 1;
        uint32_t agent_actions = 0;
        int truncated = 0;
        command >> turn >> force >> agent_actions >> truncated;
        session.environment()->BeginRestore(turn, static_cast<mengde::core::Force>(force), agent_actions,
                                            truncated != 0);
        PrintOk();
      } else if (op == "RESTORE_UNIT") {
        uint32_t unit_id = 0;
        uint16_t level = 1;
        uint16_t exp = 0;
        int hp = 0, mp = 0, x = 0, y = 0, direction = 0, done = 0, invulnerable = 0;
        command >> unit_id >> level >> exp >> hp >> mp >> x >> y >> direction >> done >> invulnerable;
        session.environment()->RestoreUnit(unit_id, level, exp, hp, mp, {x, y}, direction, done != 0);
        session.environment()->GetGame()->GetUnit(unit_id)->SetInvulnerable(invulnerable != 0);
        PrintOk();
      } else if (op == "RESTORE_SPAWN") {
        std::string hero_id;
        uint16_t level = 1;
        uint16_t exp = 0;
        uint32_t force = 1;
        int hp = 0, mp = 0, x = 0, y = 0, direction = 0, done = 0, invulnerable = 0;
        command >> hero_id >> level >> exp >> hp >> mp >> x >> y >> direction >> done >> force >> invulnerable;
        uint32_t restored_id = session.environment()->RestoreSpawnUnit(
            hero_id, level, exp, hp, mp, {x, y}, direction, done != 0,
            static_cast<mengde::core::Force>(force));
        session.environment()->GetGame()->GetUnit(restored_id)->SetInvulnerable(invulnerable != 0);
        PrintOk();
      } else if (op == "RESTORE_ITEM") {
        std::string item_id;
        uint32_t count = 0;
        command >> item_id >> count;
        session.environment()->RestoreItem(item_id, count);
        PrintOk();
      } else if (op == "RESTORE_MONEY") {
        uint32_t money = 0;
        command >> money;
        session.RestoreMoney(money);
        PrintOk();
      } else if (op == "RESTORE_PROGRESS") {
        std::string hero_id;
        uint16_t level = 1;
        uint16_t exp = 0;
        uint16_t training_penalty = 0;
        uint16_t last_stage = 0;
        command >> hero_id >> level >> exp >> training_penalty >> last_stage;
        session.RestoreCommanderProgress(
            hero_id, level, exp, training_penalty, last_stage);
        PrintOk();
      } else if (op == "TRAINING") {
        PrintTraining(&session);
      } else if (op == "TRAIN") {
        std::string hero_id;
        command >> hero_id;
        const Session::UnitProgress progress = session.ApplyTraining(hero_id);
        std::cout << "RL\t{\"hero_id\":" << JsonString(hero_id)
                  << ",\"level\":" << progress.level
                  << ",\"exp\":" << progress.exp
                  << ",\"training_penalty\":" << progress.training_penalty
                  << "}" << std::endl;
      } else if (op == "RESTORE_VISITED") {
        std::string site_id;
        command >> site_id;
        session.environment()->RestoreVisitedSite(site_id);
        PrintOk();
      } else if (op == "RESTORE_DONE") {
        session.environment()->FinishRestore();
        session.ApplyRestoredCommanderPenalties();
        session.RecordCurrentCommanderProgress();
        PrintState(session.environment(), 0.0f, false, session.environment()->GetTruncated());
      } else if (op == "UNITS") {
        PrintUnits(session.environment());
      } else if (op == "STORY") {
        PrintStory(session.environment());
      } else if (op == "QUIT") {
        break;
      } else {
        std::cout << "RL\t{\"error\":\"unknown command\"}" << std::endl;
      }
    }
  } catch (const std::exception& error) {
    std::cout << "RL\t{\"error\":" << JsonString(error.what()) << "}" << std::endl;
    return 1;
  }
  return 0;
}
