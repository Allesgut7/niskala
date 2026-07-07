// Niskala - LLM Client Header
// Version: 1.0.0

#pragma once

#include <string>
#include <memory>

namespace niskala {

class LLMClient {
public:
    LLMClient();
    ~LLMClient();

    // Interpret a text prompt and return a response
    std::string interpret(const std::string& text);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace niskala
