// Niskala - Screen Interface
// Version: 1.0.0

#pragma once

#include <ftxui/ftxui.hpp>

namespace niskala {

using namespace ftxui;

class ScreenBase {
public:
    virtual ~ScreenBase() = default;
    
    // Render the screen
    virtual Element render() = 0;
    
    // Handle events
    virtual bool on_event(Event event) = 0;
    
    // Refresh data
    virtual void refresh() = 0;
    
    // Get screen name
    virtual std::string name() const = 0;
};

} // namespace niskala
