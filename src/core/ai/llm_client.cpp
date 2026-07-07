// Niskala - LLM Client Implementation
// Version: 1.0.0

#include "core/ai/llm_client.h"
#include <string>

namespace niskala {

struct LLMClient::Impl {
    // TODO: API endpoint, API key, model name
};

LLMClient::LLMClient()
    : impl_(std::make_unique<Impl>()) {
}

LLMClient::~LLMClient() = default;

std::string LLMClient::interpret(const std::string& /*text*/) {
    // TODO: Call LLM API (OpenAI/Local)
    return "";
}

} // namespace niskala
