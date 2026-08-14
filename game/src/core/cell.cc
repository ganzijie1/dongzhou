#include "cell.h"

namespace mengde {
namespace core {

Cell::Cell(Terrain* terrain)
    : terrain_(terrain), secondary_terrain_(nullptr), secondary_coverage_(0), unit_(nullptr) {}

Terrain* Cell::GetTerrain() { return terrain_; }

Terrain* Cell::GetSecondaryTerrain() { return secondary_terrain_; }

uint8_t Cell::GetSecondaryCoverage() const { return secondary_coverage_; }

bool Cell::HasSecondaryTerrain() const {
  return secondary_terrain_ != nullptr && secondary_coverage_ != 0;
}

int Cell::GetMoveCost(int class_idx) {
  const int primary = terrain_->GetMoveCost(class_idx);
  if (!HasSecondaryTerrain() || primary >= 255) return primary;
  const int secondary = secondary_terrain_->GetMoveCost(class_idx);
  // Structure collisions are primary-owned and never softened by a visual blend.
  if (secondary >= 255) return primary;
  return (primary * (255 - secondary_coverage_) + secondary * secondary_coverage_ + 127) / 255;
}

int Cell::GetTerrainEffect(int class_idx) {
  const int primary = terrain_->GetEffect(class_idx);
  if (!HasSecondaryTerrain()) return primary;
  const int secondary = secondary_terrain_->GetEffect(class_idx);
  return (primary * (255 - secondary_coverage_) + secondary * secondary_coverage_ + 127) / 255;
}

int Cell::GetTerrainEffectThisCell() {
  ASSERT(IsUnitPlaced());
  return GetTerrainEffect(unit_->GetClassIndex());
}

int Cell::ApplyTerrainEffect(int class_idx, int value) {
  return value * GetTerrainEffect(class_idx) / 100;
}

std::string Cell::GetTerrainName() const { return terrain_->GetName(); }

std::string Cell::GetTerrainDisplayName() const {
  if (!HasSecondaryTerrain()) return terrain_->GetName();
  const int percent = (secondary_coverage_ * 100 + 127) / 255;
  return terrain_->GetName() + " / " + secondary_terrain_->GetName() + " " +
         std::to_string(percent) + "%";
}

void Cell::SetTerrainBlend(Terrain* primary, Terrain* secondary, uint8_t coverage) {
  ASSERT(primary != nullptr);
  ASSERT(primary == terrain_);
  ASSERT((secondary == nullptr) == (coverage == 0));
  secondary_terrain_ = secondary;
  secondary_coverage_ = coverage;
}

bool Cell::IsUnitPlaced() const { return unit_ != nullptr; }

Unit* Cell::GetUnit() { return unit_; }

void Cell::SetUnit(Unit* unit) { unit_ = unit; }

}  // namespace core
}  // namespace mengde