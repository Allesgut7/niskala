// Niskala - Impact Mapper Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <vector>
#include <string>
#include <memory>

namespace niskala {

struct ImpactResult {
    std::vector<std::string> sectors;
    std::vector<std::string> tickers;
    std::string summary;
};

class ImpactMapper {
public:
    ImpactMapper();
    ~ImpactMapper();

    // Map a news article to impacted sectors/tickers
    ImpactResult map_impact(const NewsArticle& article);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace niskala
