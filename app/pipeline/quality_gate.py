from collections import deque

class QualityGate:
    def __init__(self, min_pass_rate=0.05, abort_after=20):
        self.clip_history = deque(maxlen=50)
        self.passed_count = 0
        self.total_count = 0
        self.min_pass_rate = min_pass_rate
        self.abort_after = abort_after
        
    def get_dynamic_threshold(self):
        """Auto-calibrate based on recent performance"""
        if len(self.clip_history) < 10:
            return 0.30
        
        sorted_scores = sorted(self.clip_history, reverse=True)
        percentile_85 = sorted_scores[int(len(sorted_scores) * 0.15)]
        
        return max(0.25, percentile_85)
    
    def check(self, image, clip_score, artifact_count=0):
        """
        Returns: (passed: bool, reasons: dict)
        Raises: RuntimeError if pipeline is degrading
        """
        if self.total_count >= self.abort_after:
            pass_rate = self.passed_count / self.total_count
            if pass_rate < self.min_pass_rate:
                raise RuntimeError(
                    f"Pipeline degrading: {pass_rate:.1%} pass rate after {self.total_count} attempts. Aborting."
                )
        
        threshold = self.get_dynamic_threshold()
        
        checks = {
            'clip_alignment': clip_score > threshold,
            'no_artifacts': artifact_count == 0,
        }
        
        passed = all(checks.values())
        
        self.clip_history.append(clip_score)
        self.total_count += 1
        if passed:
            self.passed_count += 1
        
        return passed, {
            **checks,
            'clip_score': clip_score,
            'threshold': threshold,
            'pass_rate': self.passed_count / max(self.total_count, 1)
        }
    
    def get_stats(self):
        """Export statistics for logging/analysis"""
        return {
            'total_attempts': self.total_count,
            'passed': self.passed_count,
            'pass_rate': self.passed_count / max(self.total_count, 1),
            'current_threshold': self.get_dynamic_threshold(),
            'avg_clip_score': sum(self.clip_history) / len(self.clip_history) if self.clip_history else 0
        }