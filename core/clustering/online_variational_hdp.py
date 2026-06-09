import torch
import torch.nn as nn
import numpy as np
from datetime import datetime

class OnlineVariationalHDP(nn.Module):
    def __init__(self, embedding_dim=512, K_max=50, gamma=1.0):
        super().__init__()
        self.K_max = K_max
        self.gamma = gamma
        self.neural_encoder = nn.Sequential(
            nn.Linear(embedding_dim, 256),
            nn.ReLU(),
            nn.Linear(256, K_max * 2)
        )
        self.reset()
    
    def reset(self):
        self.cluster_counts = torch.zeros(self.K_max)
    
    def update_online(self, embeddings):
        enc = self.neural_encoder(embeddings.mean(dim=0))
        q_mean = enc[:self.K_max]
        assignment_probs = torch.softmax(q_mean, dim=0)
        self.cluster_counts += assignment_probs
        active = (self.cluster_counts > 0.5).sum().item()
        return {
            'active_clusters': active,
            'birth_prob': self.gamma / (self.gamma + self.cluster_counts.sum()),
            'provenance': {'method': 'OnlineVariationalHDP', 'timestamp': datetime.now().isoformat()}
        }
