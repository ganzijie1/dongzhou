#ifndef MENGDE_CORE_RL_ENVIRONMENT_H_
#define MENGDE_CORE_RL_ENVIRONMENT_H_

#include <stdint.h>

#include <map>
#include <set>
#include <string>
#include <vector>

#include "force.h"
#include "util/vec2d.h"

namespace mengde {
namespace core {

class Game;
class Unit;

// A headless reinforcement-learning facade over the real game rules.
class RLEnvironment {
 public:
  enum class ActionType { kWait = 0, kMove = 1, kBasicAttack = 2, kMagic = 3 };

  struct Action {
    uint32_t   unit_id;
    ActionType type;
    Vec2D      destination;
    uint32_t   target_id;
    std::string skill_id;
  };

  struct StepResult {
    std::vector<float> observation;
    float              reward;
    bool               terminated;
    bool               truncated;
  };

  struct ItemInfo {
    std::string id;
    std::string name;
    int hp;
    int mp;
    uint32_t price;
    uint32_t count;
  };

  struct SiteInfo {
    std::string id;
    std::string name;
    Vec2D position;
    int restore_hp;
    int restore_mp;
    std::vector<std::pair<std::string, uint32_t>> rewards;
  };

  static const uint32_t kNoTarget = UINT32_MAX;

  RLEnvironment(Game* game, uint32_t max_units = 32, uint32_t max_agent_actions = 20,
                bool auto_opponents = true);

  std::vector<float> Observe() const;
  const std::vector<Action>& GetLegalActions();
  StepResult Step(uint32_t action_index);
  bool       IsDone() const;

  uint32_t GetMaxUnits() const { return max_units_; }
  uint32_t GetObservationSize() const { return 4 + max_units_ * 16; }
  Force    GetCurrentForce() const;
  int      GetGameStatus() const;
  Vec2D    GetMapSize() const;
  std::string GetTerrainName(Vec2D position) const;
  std::vector<Vec2D> GetMovementPath(uint32_t unit_id, Vec2D destination) const;
  std::vector<Vec2D> GetMovementRange(uint32_t unit_id) const;
  std::vector<ItemInfo> GetItems() const;
  std::map<std::string, uint32_t> GetInventoryCounts() const;
  void SetInventoryCounts(const std::map<std::string, uint32_t>& counts);
  void PurchaseItem(const std::string& item_id, uint32_t* money);
  const std::vector<SiteInfo>& GetSites() const { return sites_; }
  std::vector<std::string> TakeNotices();
  StepResult UseItem(uint32_t unit_id, const std::string& item_id);
  void BeginRestore(uint16_t turn, Force force, uint32_t agent_actions, bool truncated);
  void RestoreUnit(uint32_t unit_id, uint16_t level, uint16_t exp, int hp, int mp,
                   Vec2D position, int direction, bool done_action);
  uint32_t RestoreSpawnUnit(const std::string& hero_id, uint16_t level, uint16_t exp,
                            int hp, int mp, Vec2D position, int direction,
                            bool done_action, Force force);
  void RestoreItem(const std::string& item_id, uint32_t count);
  void RestoreVisitedSite(const std::string& site_id);
  void FinishRestore();
  uint32_t GetAgentActions() const { return agent_actions_; }
  bool GetTruncated() const { return truncated_; }
  const std::set<std::string>& GetVisitedSites() const { return visited_sites_; }
  Game*       GetGame() const { return game_; }

 private:
  void  RebuildLegalActions();
  void  DrainCommands();
  void  AdvanceFinishedForces();
  void  PlayOpponentTurns();
  void  LoadSupplies();
  void  CheckSiteEntry(Unit* unit);
  void  ApplySiteRecovery(Force force);
  float UnitHealthTotal(Force force) const;

  Game*               game_;
  uint32_t            max_units_;
  uint32_t            max_agent_actions_;
  uint32_t            agent_actions_;
  bool                truncated_;
  bool                auto_opponents_;
  std::vector<Action> legal_actions_;
  std::map<std::string, ItemInfo> items_;
  std::vector<SiteInfo> sites_;
  std::set<std::string> visited_sites_;
  std::vector<std::string> notices_;
};

}  // namespace core
}  // namespace mengde

#endif  // MENGDE_CORE_RL_ENVIRONMENT_H_
