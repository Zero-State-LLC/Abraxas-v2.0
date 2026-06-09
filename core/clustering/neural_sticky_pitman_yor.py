import torch
import torch.nn as nn
import torch.nn.functional as F
from datetime import datetime

class NeuralStickyPitmanYor(nn.Module):
    def __init__(self, embedding_dim=512, hidden_dim=384):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.12),
            nn.Linear(hidden_dim, 3)
        )
    
    def forward(self, belief_state, temporal_slice=None, signals=None, vacuity=None):
        features = belief_state.mean(dim=0) if belief_state.dim() > 1 else belief_state
        pred = self.net(features.unsqueeze(0) if features.dim() == 1 else features)
        d = torch.sigmoid(pred[:, 0]) * 0.92
        alpha = F.softplus(pred[:, 1]) + 0.3
        kappa = F.softplus(pred[:, 2]) + 0.5
        if vacuity is not None and vacuity > 0.35:
            kappa = kappa * (1.0 - vacuity * 0.6)
        return d.item(), alpha.item(), kappa.item()
    
    def get_pitman_yor_params(self, *args, **kwargs):
        d, alpha, kappa = self.forward(*args, **kwargs)
        return {'d': d, 'alpha': alpha, 'kappa': kappa, 'provenance': {'model': 'NeuralStickyPitmanYor', 'timestamp': datetime.now().isoformat()}}
