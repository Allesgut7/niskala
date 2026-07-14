# Niskala - Financial Market Impact Model
# Multi-task IndoBERT for Indonesian financial news analysis

import json
import logging
import torch
import torch.nn as nn
from transformers import AutoConfig, AutoModel, AutoTokenizer
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

FINANCIAL_BACKBONE = "intanm/mlm-20230503-indobert-base-p1-combined-001"

NER_TAGS = [
    "O", "B-COMPANY", "I-COMPANY", "B-ORGANIZATION", "I-ORGANIZATION",
    "B-INDEX", "I-INDEX", "B-CURRENCY", "I-CURRENCY",
    "B-COMMODITY", "I-COMMODITY", "B-PERSON", "I-PERSON",
]

EVENT_TYPES = [
    "Dividen", "Buyback", "Merger", "Rights Issue", "IPO",
    "Tender Offer", "Akuisisi", "Laba Naik", "Laba Turun",
    "Default", "Restrukturisasi", "Stock Split",
]

RELATION_TYPES = [
    "akuisisi", "merger", "investasi", "ekspor_ke", "menjual",
    "membeli", "kerjasama_dengan", "diatur_oleh", "dimiliki_oleh", "mempengaruhi",
]

SENTIMENT_MAP = {0: "Bearish", 1: "Neutral", 2: "Bullish"}
IMPACT_MAP = {0: "Very Negative", 1: "Negative", 2: "Neutral", 3: "Positive", 4: "Very Positive"}
TIME_MAP = {0: "Intraday", 1: "Swing", 2: "Long-term"}


class MultiTaskIndoBERT(nn.Module):
    def __init__(
        self,
        model_name: str = FINANCIAL_BACKBONE,
        num_sentiment: int = 3,
        num_events: int = len(EVENT_TYPES),
        num_impact: int = 5,
        num_time: int = 3,
        num_ner_tags: int = len(NER_TAGS),
        num_relations: int = len(RELATION_TYPES),
    ):
        super().__init__()
        config = AutoConfig.from_pretrained(model_name)
        config.output_hidden_states = True
        self.bert = AutoModel.from_pretrained(model_name, config=config)
        hidden_size = config.hidden_size

        self.dropout = nn.Dropout(0.2)

        self.sentiment_head = nn.Linear(hidden_size, num_sentiment)
        self.event_head = nn.Linear(hidden_size, num_events)
        self.impact_head = nn.Linear(hidden_size, num_impact)
        self.time_head = nn.Linear(hidden_size, num_time)
        self.confidence_head = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )
        self.ner_head = nn.Linear(hidden_size, num_ner_tags)
        self.relation_head = nn.Linear(hidden_size, num_relations)

    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled = outputs.pooler_output
        sequence_output = outputs.last_hidden_state

        pooled = self.dropout(pooled)
        seq_output = self.dropout(sequence_output)

        sentiment_logits = self.sentiment_head(pooled)
        event_logits = self.event_head(pooled)
        impact_logits = self.impact_head(pooled)
        time_logits = self.time_head(pooled)
        confidence_out = self.confidence_head(pooled).squeeze(-1)
        ner_logits = self.ner_head(seq_output)
        relation_logits = self.relation_head(pooled)

        result = {
            "sentiment": sentiment_logits,
            "event": event_logits,
            "impact": impact_logits,
            "time_horizon": time_logits,
            "confidence": confidence_out,
            "ner": ner_logits,
            "relation": relation_logits,
        }

        if labels is not None:
            loss_fct_ce = nn.CrossEntropyLoss(reduction="none")
            loss_fct_bce = nn.BCEWithLogitsLoss(reduction="none")

            weight = labels.get("confidence_weight", None)
            if weight is None:
                weight = torch.ones_like(labels["sentiment"], dtype=torch.float)

            L_sent = (loss_fct_ce(sentiment_logits, labels["sentiment"]) * weight).mean()
            L_event = (loss_fct_bce(event_logits, labels["event"]).mean(dim=-1) * weight).mean()
            L_impact = (loss_fct_ce(impact_logits, labels["impact"]) * weight).mean()
            L_time = (loss_fct_ce(time_logits, labels["time_horizon"]) * weight).mean()
            L_conf = (nn.functional.binary_cross_entropy(confidence_out, labels["confidence"], reduction="none") * weight).mean()

            active = attention_mask.unsqueeze(-1).expand_as(ner_logits).bool()
            ner_logits_flat = ner_logits[active].view(-1, ner_logits.size(-1))
            ner_tags_flat = labels["ner_tags"][attention_mask.bool()]
            L_ner = loss_fct_ce(ner_logits_flat, ner_tags_flat).mean()

            L_rel = (loss_fct_bce(relation_logits, labels["relation"]).mean(dim=-1) * weight).mean()

            loss = (
                1.0 * L_sent
                + 0.5 * L_event
                + 0.7 * L_impact
                + 0.3 * L_time
                + 0.2 * L_conf
                + 0.8 * L_ner
                + 0.4 * L_rel
            )
            result["loss"] = loss

        return result


class FinancialMarketImpactModel:
    def __init__(self, model_dir: str, device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = MultiTaskIndoBERT(FINANCIAL_BACKBONE)
        state = torch.load(f"{model_dir}/pytorch_model.bin", map_location=self.device)
        self.model.load_state_dict(state)
        self.model.to(self.device)
        self.model.eval()
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)

        with open(f"{model_dir}/label_mappings.json") as f:
            self.mappings = json.load(f)

        logger.info(f"FinancialMarketImpactModel loaded from {model_dir} on {self.device}")

    def analyze(self, text: str) -> Dict:
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=384,
            return_tensors="pt",
        )
        input_ids = encoding["input_ids"].to(self.device)
        attn_mask = encoding["attention_mask"].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids, attn_mask)

        sent_id = torch.argmax(outputs["sentiment"], dim=-1).item()
        impact_id = torch.argmax(outputs["impact"], dim=-1).item()
        time_id = torch.argmax(outputs["time_horizon"], dim=-1).item()
        confidence = outputs["confidence"].item()

        event_probs = torch.sigmoid(outputs["event"]).cpu().numpy()[0]
        events = [
            self.mappings["event"][str(i)]
            for i, p in enumerate(event_probs)
            if p > 0.5 and str(i) in self.mappings["event"]
        ]

        rel_probs = torch.sigmoid(outputs["relation"]).cpu().numpy()[0]
        relations = [
            self.mappings["relation"][str(i)]
            for i, p in enumerate(rel_probs)
            if p > 0.5 and str(i) in self.mappings["relation"]
        ]

        ner_logits = outputs["ner"]
        ner_ids = torch.argmax(ner_logits, dim=-1).cpu().numpy()[0]
        tokens = self.tokenizer.convert_ids_to_tokens(input_ids[0])
        entities = self._decode_ner(tokens, ner_ids, text)

        sent_label = self.mappings.get("sentiment", SENTIMENT_MAP).get(str(sent_id), "Neutral")
        impact_label = self.mappings.get("impact", IMPACT_MAP).get(str(impact_id), "Neutral")
        time_label = self.mappings.get("time_horizon", TIME_MAP).get(str(time_id), "Swing")

        score = 0
        if sent_label == "Bullish":
            score = int(confidence * 100)
        elif sent_label == "Bearish":
            score = -int(confidence * 100)

        return {
            "score": score,
            "label": sent_label.upper(),
            "sentiment": sent_label,
            "event": events if events else ["Tidak Ada"],
            "impact": impact_label,
            "time_horizon": time_label,
            "confidence": round(confidence, 4),
            "entities": entities,
            "relations": relations,
        }

    def _decode_ner(self, tokens: List[str], ner_ids: List[int], original_text: str) -> List[Dict]:
        entities = []
        current_entity = None
        id_to_tag = {i: t for i, t in enumerate(NER_TAGS)}

        for token, tid in zip(tokens, ner_ids):
            tag = id_to_tag.get(tid, "O")
            if tag.startswith("B-"):
                if current_entity:
                    entities.append(current_entity)
                current_entity = {"text": token, "type": tag[2:], "tokens": [token]}
            elif tag.startswith("I-") and current_entity and current_entity["type"] == tag[2:]:
                current_entity["text"] += token.replace("##", "")
                current_entity["tokens"].append(token)
            else:
                if current_entity:
                    entities.append(current_entity)
                    current_entity = None

        if current_entity:
            entities.append(current_entity)

        for e in entities:
            e.pop("tokens", None)

        return entities

    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        return [self.analyze(t) for t in texts]
