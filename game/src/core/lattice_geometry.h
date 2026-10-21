#ifndef MENGDE_CORE_LATTICE_GEOMETRY_H_
#define MENGDE_CORE_LATTICE_GEOMETRY_H_

#include <algorithm>
#include <array>
#include <cmath>
#include <stdexcept>
#include <utility>

#include "util/vec2d.h"

namespace mengde {
namespace core {

// Coordinate conventions shared by native movement, range, and grid queries.
class LatticeCoordinate final {
 public:
  static std::array<Vec2D, 4> Neighbors4(Vec2D cell) {
    return {{Vec2D(cell.x, cell.y - 1), Vec2D(cell.x, cell.y + 1),
             Vec2D(cell.x - 1, cell.y), Vec2D(cell.x + 1, cell.y)}};
  }

  static int Manhattan(Vec2D left, Vec2D right) {
    return std::abs(left.x - right.x) + std::abs(left.y - right.y);
  }

  static int Chebyshev(Vec2D left, Vec2D right) {
    return std::max(std::abs(left.x - right.x), std::abs(left.y - right.y));
  }

  static double Euclidean(Vec2D left, Vec2D right) {
    const double dx = static_cast<double>(left.x - right.x);
    const double dy = static_cast<double>(left.y - right.y);
    return std::sqrt(dx * dx + dy * dy);
  }

  static Vec2D WorldToCell(double x, double y, double cell_width = 1.0,
                           double cell_height = 1.0, double origin_x = 0.0,
                           double origin_y = 0.0) {
    if (cell_width <= 0.0 || cell_height <= 0.0) {
      throw std::invalid_argument("cell size must be positive");
    }
    return Vec2D(static_cast<int>(std::floor((x - origin_x) / cell_width)),
                 static_cast<int>(std::floor((y - origin_y) / cell_height)));
  }

  static std::pair<double, double> CellCenter(
      Vec2D cell, double cell_width = 1.0, double cell_height = 1.0,
      double origin_x = 0.0, double origin_y = 0.0) {
    if (cell_width <= 0.0 || cell_height <= 0.0) {
      throw std::invalid_argument("cell size must be positive");
    }
    return std::make_pair(origin_x + (cell.x + 0.5) * cell_width,
                          origin_y + (cell.y + 0.5) * cell_height);
  }
};

}  // namespace core
}  // namespace mengde

#endif  // MENGDE_CORE_LATTICE_GEOMETRY_H_
