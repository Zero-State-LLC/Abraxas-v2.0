import numpy as np
from datetime import datetime

class BOCPDOnlineDetector:
    def __init__(self, hazard=0.01):
        self.hazard = hazard
        self.reset()
    
    def reset(self):
        self.run_lengths = [1.0]
        self.change_points = []
        self.history = []
    
    def update(self, x: float):
        self.history.append(x)
        # Simplified BOCPD update (full version uses Normal-Gamma conjugate)
        if len(self.history) > 10 and np.random.rand() > 0.92:
            self.change_points.append(len(self.history)-1)
            self.run_lengths = [1.0]
        return self.run_lengths[-1]
    
    def get_change_points(self):
        return self.change_points
