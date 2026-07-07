// Niskala - Signal Generator Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <vector>
#include <string>
#include <memory>

namespace niskala {

class SignalGenerator {
public:
    SignalGenerator();
    ~SignalGenerator();

    // Generate trading signal for a symbol
    AISignal generate(const std::string& symbol);

    // Generate signals for watchlist
    std::vector<AISignal> generate_batch(const std::vector<std::string>& symbols);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace niskala
