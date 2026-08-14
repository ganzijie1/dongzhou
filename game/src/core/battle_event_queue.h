#ifndef MENGDE_CORE_BATTLE_EVENT_QUEUE_H_
#define MENGDE_CORE_BATTLE_EVENT_QUEUE_H_

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <string>

namespace mengde {
namespace core {

enum class BattleEventType {
  kMoveCompleted,
  kAttackStarted,
  kHit,
  kCounterattackStarted,
  kDeath,
  kScriptTriggered,
};

inline const char* BattleEventTypeName(BattleEventType type) {
  switch (type) {
    case BattleEventType::kMoveCompleted: return "move_completed";
    case BattleEventType::kAttackStarted: return "attack_started";
    case BattleEventType::kHit: return "hit";
    case BattleEventType::kCounterattackStarted: return "counterattack_started";
    case BattleEventType::kDeath: return "death";
    case BattleEventType::kScriptTriggered: return "script_triggered";
  }
  return "unknown";
}

struct BattleEvent {
  BattleEventType type = BattleEventType::kScriptTriggered;
  uint64_t sequence = 0;
  uint16_t turn = 0;
  std::string actor;
  std::string target;
  std::string detail;
  int from_x = -1;
  int from_y = -1;
  int to_x = -1;
  int to_y = -1;
  int value = 0;
};

class BattleEventQueue {
 public:
  BattleEventQueue() noexcept : enabled_(true), next_sequence_(1) {
    try {
      const char* enabled = std::getenv("MENGDE_BATTLE_EVENTS");
      if (enabled != nullptr) {
        const std::string value(enabled);
        if (value == "0" || value == "false" || value == "FALSE") enabled_ = false;
      }
      const char* replay_path = std::getenv("MENGDE_BATTLE_REPLAY_LOG");
      if (enabled_ && replay_path != nullptr && replay_path[0] != '\0') {
        replay_.open(replay_path, std::ios::out | std::ios::app);
      }
    } catch (...) {
      Disable();
    }
  }

  void Emit(BattleEvent event) noexcept {
    if (!enabled_) return;
    try {
      event.sequence = next_sequence_++;
      pending_.push_back(event);
      history_.push_back(event);
      if (pending_.size() > kPendingLimit) pending_.pop_front();
      if (history_.size() > kHistoryLimit) history_.pop_front();
      WriteReplay(event);
    } catch (...) {
      Disable();
    }
  }

  bool enabled() const noexcept { return enabled_; }
  const std::deque<BattleEvent>& pending() const noexcept { return pending_; }
  const std::deque<BattleEvent>& history() const noexcept { return history_; }
  void ClearPending() noexcept { pending_.clear(); }

 private:
  static std::string EscapeJson(const std::string& value) {
    std::string escaped;
    escaped.reserve(value.size());
    for (char ch : value) {
      switch (ch) {
        case '\\': escaped += "\\\\"; break;
        case '"': escaped += "\\\""; break;
        case '\n': escaped += "\\n"; break;
        case '\r': escaped += "\\r"; break;
        case '\t': escaped += "\\t"; break;
        default: escaped += ch; break;
      }
    }
    return escaped;
  }

  void WriteReplay(const BattleEvent& event) noexcept {
    if (!replay_.is_open()) return;
    replay_ << "{\"sequence\":" << event.sequence
            << ",\"turn\":" << event.turn
            << ",\"type\":\"" << BattleEventTypeName(event.type) << '"'
            << ",\"actor\":\"" << EscapeJson(event.actor) << '"'
            << ",\"target\":\"" << EscapeJson(event.target) << '"'
            << ",\"detail\":\"" << EscapeJson(event.detail) << '"'
            << ",\"from\":[" << event.from_x << ',' << event.from_y << ']'
            << ",\"to\":[" << event.to_x << ',' << event.to_y << ']'
            << ",\"value\":" << event.value << "}\n";
    replay_.flush();
    if (!replay_) replay_.close();
  }

  void Disable() noexcept {
    enabled_ = false;
    pending_.clear();
    history_.clear();
    if (replay_.is_open()) replay_.close();
  }

  static const size_t kPendingLimit = 4096;
  static const size_t kHistoryLimit = 65536;
  bool enabled_;
  uint64_t next_sequence_;
  std::deque<BattleEvent> pending_;
  std::deque<BattleEvent> history_;
  std::ofstream replay_;
};

}  // namespace core
}  // namespace mengde

#endif  // MENGDE_CORE_BATTLE_EVENT_QUEUE_H_