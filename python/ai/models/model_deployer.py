# Niskala - Model Deployer
# ML model deployment and serving

import os
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    model_id: str
    version: str
    replicas: int = 1
    max_batch_size: int = 32
    timeout_ms: int = 100
    memory_limit_mb: int = 512


@dataclass
class DeploymentStatus:
    """Deployment status"""
    model_id: str
    version: str
    status: str  # deploying, running, stopped, error
    endpoint: str
    replicas: int
    requests_per_second: float
    avg_latency_ms: float
    error_rate: float
    started_at: str
    uptime_seconds: float


class ModelDeployer:
    """ML model deployment manager"""
    
    def __init__(self, deploy_path: str = 'data/deployments'):
        self.deploy_path = deploy_path
        os.makedirs(deploy_path, exist_ok=True)
        self.active_deployments: Dict[str, DeploymentStatus] = {}
        logger.info("ModelDeployer initialized")
    
    async def deploy(self, config: DeploymentConfig, model_path: str) -> DeploymentStatus:
        """Deploy model to production"""
        logger.info(f"Deploying {config.model_id} v{config.version}")
        
        # Create deployment directory
        deploy_dir = os.path.join(self.deploy_path, f"{config.model_id}_{config.version}")
        os.makedirs(deploy_dir, exist_ok=True)
        
        # Copy model file
        if os.path.exists(model_path):
            import shutil
            dest = os.path.join(deploy_dir, os.path.basename(model_path))
            shutil.copy2(model_path, dest)
        
        # Save deployment config
        config_file = os.path.join(deploy_dir, 'config.json')
        with open(config_file, 'w') as f:
            json.dump(config.__dict__, f, indent=2)
        
        # Create deployment status
        status = DeploymentStatus(
            model_id=config.model_id,
            version=config.version,
            status='running',
            endpoint=f'/api/models/{config.model_id}/v{config.version}/predict',
            replicas=config.replicas,
            requests_per_second=0,
            avg_latency_ms=0,
            error_rate=0,
            started_at=datetime.now().isoformat(),
            uptime_seconds=0
        )
        
        self.active_deployments[f"{config.model_id}_{config.version}"] = status
        
        # Save status
        status_file = os.path.join(deploy_dir, 'status.json')
        with open(status_file, 'w') as f:
            json.dump(status.__dict__, f, indent=2)
        
        logger.info(f"Model deployed: {status.endpoint}")
        return status
    
    async def rollback(self, model_id: str, version: str) -> bool:
        """Rollback to previous version"""
        deployment_key = f"{model_id}_{version}"
        
        if deployment_key in self.active_deployments:
            self.active_deployments[deployment_key].status = 'stopped'
            logger.info(f"Rolled back {model_id} v{version}")
            return True
        
        return False
    
    async def stop(self, model_id: str, version: str) -> bool:
        """Stop deployment"""
        deployment_key = f"{model_id}_{version}"
        
        if deployment_key in self.active_deployments:
            self.active_deployments[deployment_key].status = 'stopped'
            logger.info(f"Stopped {model_id} v{version}")
            return True
        
        return False
    
    async def scale(self, model_id: str, version: str, replicas: int) -> bool:
        """Scale deployment"""
        deployment_key = f"{model_id}_{version}"
        
        if deployment_key in self.active_deployments:
            self.active_deployments[deployment_key].replicas = replicas
            logger.info(f"Scaled {model_id} v{version} to {replicas} replicas")
            return True
        
        return False
    
    def get_status(self, model_id: str, version: Optional[str] = None) -> Optional[DeploymentStatus]:
        """Get deployment status"""
        if version:
            return self.active_deployments.get(f"{model_id}_{version}")
        
        # Get latest deployment
        for key, status in self.active_deployments.items():
            if key.startswith(model_id):
                return status
        
        return None
    
    def list_deployments(self) -> List[DeploymentStatus]:
        """List all deployments"""
        return list(self.active_deployments.values())
    
    def update_metrics(self, model_id: str, version: str, 
                      requests_per_second: float, avg_latency_ms: float,
                      error_rate: float):
        """Update deployment metrics"""
        deployment_key = f"{model_id}_{version}"
        
        if deployment_key in self.active_deployments:
            status = self.active_deployments[deployment_key]
            status.requests_per_second = requests_per_second
            status.avg_latency_ms = avg_latency_ms
            status.error_rate = error_rate
            
            # Update uptime
            started = datetime.fromisoformat(status.started_at)
            status.uptime_seconds = (datetime.now() - started).total_seconds()
