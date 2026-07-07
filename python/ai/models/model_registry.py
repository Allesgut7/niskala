# Niskala - Model Registry
# ML model versioning and management

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModelVersion:
    """Model version info"""
    model_id: str
    version: str
    name: str
    description: str
    model_type: str
    metrics: Dict
    parameters: Dict
    created_at: str
    updated_at: str
    status: str  # draft, staging, production, archived
    path: str
    size_mb: float = 0.0


class ModelRegistry:
    """ML model registry"""
    
    def __init__(self, registry_path: str = 'data/models'):
        self.registry_path = registry_path
        os.makedirs(registry_path, exist_ok=True)
        self._load_registry()
        logger.info(f"ModelRegistry initialized: {registry_path}")
    
    def _load_registry(self):
        """Load registry from disk"""
        registry_file = os.path.join(self.registry_path, 'registry.json')
        if os.path.exists(registry_file):
            with open(registry_file, 'r') as f:
                self.registry = json.load(f)
        else:
            self.registry = {}
    
    def _save_registry(self):
        """Save registry to disk"""
        registry_file = os.path.join(self.registry_path, 'registry.json')
        with open(registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_model(self, model_id: str, version: str, name: str,
                       description: str, model_type: str, metrics: Dict,
                       parameters: Dict, path: str) -> ModelVersion:
        """Register a new model version"""
        now = datetime.now().isoformat()
        
        model_version = ModelVersion(
            model_id=model_id,
            version=version,
            name=name,
            description=description,
            model_type=model_type,
            metrics=metrics,
            parameters=parameters,
            created_at=now,
            updated_at=now,
            status='draft',
            path=path,
            size_mb=self._get_file_size(path)
        )
        
        if model_id not in self.registry:
            self.registry[model_id] = {}
        
        self.registry[model_id][version] = asdict(model_version)
        self._save_registry()
        
        logger.info(f"Model registered: {model_id} v{version}")
        return model_version
    
    def get_model(self, model_id: str, version: Optional[str] = None) -> Optional[Dict]:
        """Get model info"""
        if model_id not in self.registry:
            return None
        
        if version:
            return self.registry[model_id].get(version)
        
        # Get latest version
        versions = self.registry[model_id]
        if not versions:
            return None
        
        latest = max(versions.values(), key=lambda v: v['created_at'])
        return latest
    
    def list_models(self, status: Optional[str] = None) -> List[Dict]:
        """List all models"""
        models = []
        for model_id, versions in self.registry.items():
            for version, info in versions.items():
                if status is None or info['status'] == status:
                    models.append(info)
        return models
    
    def update_status(self, model_id: str, version: str, status: str):
        """Update model status"""
        if model_id in self.registry and version in self.registry[model_id]:
            self.registry[model_id][version]['status'] = status
            self.registry[model_id][version]['updated_at'] = datetime.now().isoformat()
            self._save_registry()
            logger.info(f"Model {model_id} v{version} status: {status}")
    
    def get_production_model(self, model_id: str) -> Optional[Dict]:
        """Get production model"""
        if model_id not in self.registry:
            return None
        
        for version, info in self.registry[model_id].items():
            if info['status'] == 'production':
                return info
        
        return None
    
    def delete_model(self, model_id: str, version: str):
        """Delete model version"""
        if model_id in self.registry and version in self.registry[model_id]:
            del self.registry[model_id][version]
            if not self.registry[model_id]:
                del self.registry[model_id]
            self._save_registry()
            logger.info(f"Model {model_id} v{version} deleted")
    
    def get_model_lineage(self, model_id: str) -> List[Dict]:
        """Get model version history"""
        if model_id not in self.registry:
            return []
        
        versions = sorted(
            self.registry[model_id].values(),
            key=lambda v: v['created_at']
        )
        return versions
    
    def _get_file_size(self, path: str) -> float:
        """Get file size in MB"""
        if os.path.exists(path):
            size_bytes = os.path.getsize(path)
            return size_bytes / (1024 * 1024)
        return 0.0
